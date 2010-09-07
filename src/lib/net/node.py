# -*- coding: utf-8 -*-
#
# Package: net.node
#
try:
    import re
    import connect
    import util.text
except ImportError, e:
    raise ImportError(str(e) +
"""
    A critical module could not be imported.
""")


__all__ = ['Cisco', 'OmniSwitch']



class Node(object):
    """
    Classe générique définissant un noeud.
    Celle-ci ne doit être utilisée que si ce n'est pour la spécialiser.
    """

    default_prompt = re.compile('[#>\$]\s?')



    def __init__(self, mode, hostname, username, password =None, prompt =None,
                 timeout =15):
        """
        Constructeur de la classe Node.
        """

        self.connection = None

        self.mode = mode
        self.hostname = hostname
        self.username = username
        self.password = password

        self.prompt   = self.default_prompt
        
        self.timeout  = timeout


        if prompt is not None:
            self.prompt = prompt



    def set_mode(self, mode):
        """
        Définit le mode de connexion.
        """
        
        if mode == 'telnet' or mode == 'ssh':
            self.mode = mode


    def connect(self):
        """
        Etabli une connection en fonction du mode choisi.
        """

        if self.mode == 'ssh':
            self.connection = connect.SSH(self.hostname, self.username,
                                          self.password, self.prompt,
                                          self.timeout)
        if self.mode == 'telnet':
            self.connection = connect.Telnet(self.hostname, self.username,
                                             self.password, self.prompt,
                                             self.timeout)

        return self.connection.login()

    def quit(self):
        self.connection.close()

    def run(self, command, expected =None):
        return self.connection.run(command, expected)




class Cisco(Node):
    """
    Cette classe automatise les différentes actions pour les systèmes Cisco.
    """

    __default_prompt = re.compile('(.*)[>#]')
    __comment_marker = '!'

    __more = ' --More-- '
    __password = re.compile('password:', re.I)

    __show_config = 'show running-config'
    __show_privilege = 'show privilege'

    __enable = 'enable %(level)i'

    __config_level = 15



    def __init__(self, mode, hostname, username, password =None, prompt =None,
                 timeout =15):
        """
        Constructeur de la classe Cisco.
        """

        self.__config = None
        self.__level = None

        if prompt is not None:
            Node.__init__(self, mode, hostname, username, password, prompt,
                          timeout)
        else:
            Node.__init__(self, mode, hostname, username, password,
                          self.__default_prompt, timeout)



    def connect(self):
        """
        Etabli une connection en fonction du mode choisi.
        """

        if Node.connect(self):
            self.__level = self.get_privilege_level()
            return True

        return False

    def enable(self, level =15, password =None):
        """
        Cette méthode élève les privilèges de l'utilisateur.
        """

        enable_password = self.password
        if password is not None:
            enable_password = password

        self.connection.run(self.__enable % {'level': level},
                            {self.__more: ' ',
                             self.__password: enable_password})

    def run(self, command, expected =None):
        if expected is None:
            expected = {}
        expected[self.__more] = ' '

        return Node.run(self, command, expected)


    def get_config(self, refresh =False, clear_comments =False):
        """
        Récupère la configuration courrante de l'hôte.
        """

        if self.__config is None or refresh:
            if self.__level < self.__config_level:
                self.enable(self.__config_level)

            self.__config = self.run(self.__show_config)[2:]

        if clear_comments:
            return util.text.clear_comments(self.__config, self.__comment_marker)

        return self.__config

    def get_hostname(self):
        """
        Retourne le nom d'hôte du système.
        """

        config = self.get_config()

        for line in config:
            match = re.match('hostname (.*)', line)
            if match:
                return match.group(1).lower()

    def get_privilege_level(self):
        """
        Retourne le niveau de privilege actuel.
        """

        ret = self.run(self.__show_privilege)
        for line in ret:
            match = re.match('Current privilege level is (\d+)', line)

            if match:
                self.__level = match.group(1)


        return self.__level




class OmniSwitch(Node):
    """
    Cette classe automatise les différentes actions pour les systèmes
    OmniSwitch.
    """

    __default_prompt = '->'
    __comment_marker = '!'

    __show_config = 'show configuration snapshot all'



    def __init__(self, mode, hostname, username, password =None, prompt =None,
                 timeout =15):
        """
        Constructeur de la classe OmniSwitch.
        """

        self.__config = None

        if prompt is not None:
            Node.__init__(self, mode, hostname, username, password, prompt,
                          timeout)
        else:
            Node.__init__(self, mode, hostname, username, password,
                          self.__default_prompt, timeout)



    def get_config(self, refresh =False, clear_comments =False):
        """
        Récupère la configuration courrante de l'hôte.
        """

        if self.__config is None or refresh:
            self.__config = self.connection.run(self.__show_config)

        if clear_comments:
            return util.text.clear_comments(self.__config, self.__comment_marker)

        return self.__config

    def get_hostname(self):
        """
        Retourne le nom d'hôte du système.
        """

        config = self.get_config()

        for line in config:
            match = re.match('system name (.*)', line)

            if match:
                return match.group(1).lower()
