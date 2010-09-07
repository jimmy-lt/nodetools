# -*- coding: utf-8 -*-
#
# Package: util.config
#
try:
    import re

    from ConfigParser import ConfigParser, NoOptionError
except ImportError, e:
    raise ImportError(str(e) +
"""
    A critical module could not be imported.
""")


__all__ = ['ConfigError', 'Config']



class ConfigError(Exception):
    """
    Classe permettant de gérer les erreurs sur le fichier de configuration.
    """




class Config(ConfigParser):
    """Classe gérant la configuration de l'utilitaire."""


    # On définit les différents éléments autorisés dans le fichier de
    # configuration.

    # Options autorisées pour les sections concernant les noeuds.
    # Le même principe est appliqué que pour les options globales.
    __nodes_spec_options     = (
                                ('connection', 'string', True),
                                ('failover', 'string', False),
                                ('options', 'string', False),
                                ('username', 'string', False),
                                ('password', 'string', False),
                                ('prompt', 'string', False),
                                ('timeout', 'int', False),
                               )
    __nodes_spec_sub_options = (
                                ('hostname', 'string', True),
                                ('group', 'string', False),
                               )

    __nodes_section_name     = (
                                'OmniSwitch',
                                'Cisco'
                               )

    #===========================================================================
    # Nom et options autorisées pour chaque section globales.
    # 
    # L'ensemble des section constituent un dictionnaire. La clé d'un champs est
    # le nom de la section et la valeur est un tuple composé d'au maximum 4
    # éléments :
    #  - un booléen désignant si la section est obligatoire ou non ;
    #  - un booléen désignant si la section a des sous-sections ;
    #  - la liste des options ;
    #  - la liste des options s'ajoutant pour les sous-sections.
    # 
    # Une sous-section hérite des options de sa section parente. Elle a aussi la
    # possibilité de les redéfinir.
    # 
    # Chaque option est caractéisée par 3 éléments :
    #  - son nom ;
    #  - son type ;
    #  - son obligation.
    # 
    # Il y a 3 types d'options possibles :
    #  - string, chaîne de caractères ;
    #  - int, entier ;
    #  - bool, booléen, vrai ou faux.
    #===========================================================================
    __spec_sections = {'general':    (
                                      # La section est-elle obligatoire ?
                                      True,
                                      # La section a t-elle des sous-section ?
                                      False,
                                      # Liste des options de la section.
                                      (
                                       ('root_directory', 'string', True),
                                       ('file_pattern', 'string', True),
                                       ('rotation', 'int', False),
                                       ('write_diff', 'bool', False),
                                      ),
                                     ),
                       'contact':    (
                                      False,
                                      True,
                                      (
                                       ('mail_server', 'string', False),
                                       ('sender', 'string', False),
                                       ('send_backup', 'bool', False),
                                       ('send_diff', 'bool', False),
                                      ),
                                      # Liste des options pour les sous-sections.
                                      (
                                       ('e-mail', 'string', True),
                                      ),
                                     ),
                       __nodes_section_name[0]: (
                                      False,
                                      True,
                                      __nodes_spec_options,
                                      __nodes_spec_sub_options,
                                     ),
                       __nodes_section_name[1]: (
                                      False,
                                      True,
                                      __nodes_spec_options,
                                      __nodes_spec_sub_options,
                                     ),
                      }

    # Séparateur utilisé pour les sous-sections.
    __subsection_sep = '::'



    def __init__(self, config_file):
        """
        Constructeur de la classe Config.
        """

        ConfigParser.__init__(self)

        # On vérifie la validité du fichier.
        read_ok = self.read(config_file)

        # Si le fichier n'a pas pu être lu, on quitte.
        parse_ok = False
        for config in read_ok:
            if config == config_file:
                parse_ok = True
        if not parse_ok:
            raise ConfigError("Could not read file: %(file)s." % \
                              {'file': config_file}) 

        # On vérifie ensuite que le fichier correspond à la spécification.
        self.__check()


    def __check(self):
        """
        Parcours le fichier de configuration à la recherche de données
        invalides.
        """

        # On vérifie tout d'abord que les sections obligatoires sont présentes.
        for section in self.__get_spec_mandatory_sections():
            if not self.has_section(section):
                raise ConfigError("The section '%(section)s' is mandatory." % \
                                  {'section': section})

        # On vérifie ensuite que toutes les sections du fichier
        # correspondent au format défini.
        for f_sec in self._sections:
            # Si la section courrante fait parti de la spécification,
            if self.__spec_sections.has_key(f_sec):
                # On vérifie les options de cette section.
                self.__check_options(f_sec)

                # Tout est corect, la section est donc connue.
                # On peut sauter à l'élément suivant.
                continue

            # On test la section courante pour savoir s'il s'agit d'une
            # sous-section.
            if self.__spec_has_subsection(self.get_parent_section_name(f_sec)):
                # Si oui, on vérifie ses options.
                self.__check_options(f_sec)

                # Tout est corect, la section est donc connue.
                # On peut sauter à l'élément suivant.
                continue

            # La section ne correspond pas au format,
            # on déclare qu'il y a une erreur.
            raise NameError("Invalid section: '%(section)s.'" % \
                            {'section': f_sec})

    def __check_options(self, section):
        """
        Vérifie la validité des options pour la section passée en paramètre.
        """

        # On vérifie tout d'abord la présence des options obligatoires dans
        # le fichier de configuration.
        for option in self.__get_spec_mandatory_options(section):
            if not self.has_option(section, option[0]):
                raise ConfigError("Section '%(section)s', the option '%(option)s' is mandatory." % \
                                  {'section': section, 'option': option[0]})

        # Puis on vérifie que les options du fichier sont conformes à la
        # spécification.
        for item in self.items(section):
            if not self.__spec_has_option(section, item[0]):
                raise ConfigError("Section '%(section)s, invalid option: '%(option)s'." % \
                                  {'section': section, 'option': item[0]})



    def __spec_has_subsection(self, section):
        """
        Renvoi si la section contenue dans la spécification a des
        sous-sections ou non.
        """

        if self.__spec_sections.has_key(section):
            return self.__spec_sections.get(section)[1]
        else:
            raise NameError("Invalid section name: '%(section)s'." % \
                            {'section': section})

    def __spec_has_option(self, section, option):
        """
        Renvoi si la section contenue dans la spécification possède l'option
        passée en paramètre.
        """

        parent_section = self.get_parent_section_name(section)


        if self.is_subsection(section):
            for item in self.__spec_sections.get(parent_section)[3]:
                if item[0] == option:
                    return True

        for item in self.__spec_sections.get(parent_section)[2]:
            if item[0] == option:
                return True

        return False


    def __get_spec_mandatory_sections(self):
        """
        Retourne la liste des sections obligatoires de la spécification.
        """

        mandatory = []

        for section in self.__spec_sections.keys():
            if self.__spec_sections.get(section)[0]:
                mandatory.append(section)

        return mandatory

    def __get_spec_mandatory_options(self, section):
        """
        Retourne la liste des options obligatoires pour la section contenue
        dans la spécification.
        """

        mandatory = []
        parent_section = self.get_parent_section_name(section)


        if self.is_subsection(section):
            for item in self.__spec_sections.get(parent_section)[3]:
                if item[2]:
                    mandatory.append(item)

        for item in self.__spec_sections.get(parent_section)[2]:
            if item[2]:
                mandatory.append(item)

        return mandatory


    def has_option(self, section, option):
        """
        Renvoi si la section possède l'option passée en paramètre.
        """

        # On travaille sur le nom de la section parente
        # ou cas où s'il s'agit d'une sous-section.
        parent_section = self.get_parent_section_name(section)


        if self.__spec_sections.has_key(parent_section):
            if ConfigParser.has_option(self, section, option):
                return True
            if ConfigParser.has_option(self, parent_section, option):
                return True

            return False
        else:
            raise NameError("Invalid section name: '%(section)s'." % \
                            {'section': section})


    def is_subsection(self, section):
        """
        Permet de déterminer si la section est en fait une sous-section.
        """

        # Le schéma recherché est le suivant :
        # section-parente(séparateur)sous-section
        if re.search('^[-\w]+%(separator)s[-\w]+$' % {'separator': self.__subsection_sep},
                     section):
            return True
        else:
            return False


    def get_subsections(self, parent_section):

        if self.__spec_has_subsection(parent_section):
            sections = dict()
            for f_sec in self._sections:
                match = re.match('(%(section)s)%(separator)s(.*)$' % \
                                 {'section': parent_section,
                                  'separator': self.__subsection_sep},
                                 f_sec)
                if match:
                    if not sections.has_key(match.group(1)):
                        sections[match.group(1)] = list()

                    sections[match.group(1)].append(f_sec)
            return sections

        return None

    def get_nodes_section(self):
        """
        Retourne la liste des noeuds de la configuration.
        """
        
        sections = dict()
        for node_section in self.__nodes_section_name:
            sections.update(self.get_subsections(node_section))

        return sections

    def get_parent_section_name(self, section):
        """
        Retourne le nom de la section parente.
        """

        return re.split(self.__subsection_sep, section)[0]

    def get_subsection_name(self, section):
        """
        Retourne le nom de la sous-section.
        """

        return re.split(self.__subsection_sep, section)[1]

    def get_value(self, section, option):
        """
        Retourne la valeur de l'option contenue dans la section passée en
        paramètre.
        """

        # On travaille sur le nom de la section parente
        # au cas où s'il s'agit d'une sous-section.
        parent_section = self.get_parent_section_name(section)


        # On vérifie d'abord que la section existe.
        if self.__spec_sections.has_key(parent_section):
            # Puis on récupère la spécification de la section.
            section_spec = self.__spec_sections.get(parent_section)
            option_type  = None

            # On parcours les options de la spécification à la recherche
            # du type de la valeur de l'option que l'on souhaite obtenir.
            for option_spec in section_spec[2]:
                if option_spec[0] == option:
                    option_type = option_spec[1]

            # Introuvable dans les options de la section ?
            # On regarde dans ceux de la sous-section si elle existe.
            if self.__spec_has_subsection(parent_section):
                for sub_option_spec in section_spec[3]:
                    if sub_option_spec[0] == option:
                        option_type = sub_option_spec[1]


            # On appelle la fonction qui va bien en fonction du type à obtenir.
            #
            # Les sous-sections héritent des options de leur section parente.
            # Si l'option n'existe pas dans la section, il doit sûrement s'agir
            # d'une sous-section. On cherche alors l'option dans la section
            # parente.
            if option_type == 'string':
                try:
                    return ConfigParser.get(self, section, option)
                except NoOptionError:
                    return ConfigParser.get(self, parent_section, option)

            if option_type == 'int':
                try:
                    return ConfigParser.getint(self, section, option)
                except NoOptionError:
                    return ConfigParser.getint(self, parent_section, option)

            if option_type == 'bool':
                try:
                    return ConfigParser.getboolean(self, section, option)
                except NoOptionError:
                    return ConfigParser.getboolean(self, parent_section, option)


            return None
        else:
            raise NameError("Invalid section name: '%(section)s'." % \
                            {'section': section})


    @classmethod
    def print_spec(cls):
        """
        Affiche le format que doit avoir le fichier de configuration.
        """
        
        legend = "Légende : \n" \
                 + "  [section]\t- Section \n" \
                 + "  [section%s]\t- Sous-section \n" % Config.__subsection_sep \
                 + "  *\t\t- Elément obligatoire. \n" \
                 + "\n\n"
        print legend
        
        # Pour cahque section contenue dans la spécification.
        for section in Config.__spec_sections.keys():
            section_str = ''

            # En-tête de la section
            
            if Config.__spec_sections.get(section)[0]:
                section_str += '*'
            section_str += '[%s]\n' % section

            # Pour chaque option de cette section.
            for option in Config.__spec_sections.get(section)[2]:
                if option[2]:
                    section_str += "*"
                section_str += '%s = %s\n' % (option[0], option[1])

            if Config.__spec_sections.get(section)[1]:
                section_str += '\n[%s%s]\n' % (section, Config.__subsection_sep)

                for sub_option in Config.__spec_sections.get(section)[3]:
                    if sub_option[2]:
                        section_str += "*"
                    section_str += '%s = %s\n' % (sub_option[0], sub_option[1])

            print section_str




# Ce code est exécuté si on lance le fichier seul.
if __name__ == '__main__':
    import sys



    # Sans argument, la spécification est affichée.
    if len(sys.argv) == 1:
        Config.print_spec()

    # Avec un argument, on vérifie le fichier.
    if len(sys.argv) == 2:
        CONFIG = Config(sys.argv[1])

    sys.exit(0)
