# -*- coding: utf-8 -*-
#
# Package: net.connect
#
try:
    import re
    import pexpect
except ImportError, e:
    raise ImportError(str(e) +
"""
    A critical module could not be imported.
""")


__all__ = ['SSH', 'Telnet']



class Connect(object):
    """
    Classe servant de base pour la gestion des connexions.
    Elle ne doit être utilisée que pour la spécialiser.
    """

    default_prompt = re.compile('[#>\$]\s?')

    default_login_str = re.compile('(username|login)\s?:', re.I)
    default_password_str = re.compile('password\s?:', re.I)



    def __init__(self, hostname, username, password =None, prompt =None,
                 timeout =15):
        """
        Constructeur de la classe Connect.
        """

        self.hostname = hostname
        self.username = username
        self.password = password

        self.prompt   = self.default_prompt

        self.child    = None
        self.timeout  = timeout


        if prompt is not None:
            self.prompt = re.compile(prompt)



    def close(self):
        """
        Cette méthode ferme la conexion.
        """

        self.child.close()

    def interact(self):
        """
        Cette méthode permet de rendre la main à l'utilisateur.
        """

        self.child.interact()

    def run(self, command, expected =None):
        """
        Cette méthode exécute la commande passée en paramètre et renvoi son
        résultat.
        
        L'utilisateur peut spécifier des éléments attendues avant le prompt
        et les actions à effectuer.


        @param command:
            Commande à exécuter.
        @type command:
            str

        @param expected:
            Elément(s) attendu durant l'exécution de la commande.
        @type expected:
            dict
        
        @raise TypeError:
            Raises TypeError if 'expected' parameter is not a dictionnary.
        """

        out = []
        expected_list = []


        # Si la liste des éléments attendus est spécifiée,
        # on vérifie qu'il s'agit bien d'un dictionnaire et on récupère
        # les clés dans une liste.
        if expected is not None:
            if type(expected) is not dict:
                raise TypeError("'expected' parameter must be a dictionary.")

            expected_list = expected.keys()

        # On exécute la commande
        self.child.sendline(command)

        # On boucle tant que l'on a pas le prompt..
        ret = -1
        while ret != 0:
            # Si la liste des éléments attendus est spécifiée,
            # on l'ajoute.
            if expected is not None:
                ret = self.child.expect([self.prompt, ', '.join(expected_list)])
            else:
                ret = self.child.expect(self.prompt)

            if re.search('[\b\n\r]', self.child.before):
                # Puis, on sépare chaque ligne.
                for line in re.split('[\b\n\r]', self.child.before):
                    # On enlève les espace éventuels en fin de ligne.
                    line = re.sub('[\b\s\n\r]*$', '', line)

                    # On ajoute chaque ligne dans la liste de retour si celle-ci
                    # n'est pas vide ou ne possède pas que des espaces.
                    if not re.search('^[\b\s\n]*$', line):
                        out.append(line)
            else:
                out.append(re.sub('[\b\s\n\r]*$', '', self.child.before))

            # Si la valeur de retour est différente de celle correspondant
            # au prompt, 0.
            # On envoi la commande correspondant à l'élément trouvé.
            if ret != 0:
                self.child.send(expected[expected_list[ret - 1]])

        # La première ligne contient la commande et la dernière le prompt.
        # Donc on les enlève.
        out.pop(0)


        return out




class SSH(Connect):
    """
    Classe gérant la connexion SSH vers un noeud.
    """

    __first_connection = "Are you sure you want to continue connecting (yes/no)?"
    __kb_interractive  = "%(username)s's password for keyboard-interactive method:"
    __exchange_id_conn_closed = "ssh_exchange_identification: Connection closed by remote host"



    def __init__(self, hostname, username, password =None, prompt =None,
                 timeout =15):
        """
        Constructeur de la classe SSH.
        """

        Connect.__init__(self, hostname, username, password, prompt, timeout)



    def login(self):
        """
        Cette méthode établi la connexion avec l'hôte.
        """

        self.child = pexpect.spawn('ssh %(username)s@%(hostname)s' % \
                                   {
                                    'username': self.username,
                                    'hostname': self.hostname
                                   },
                                   timeout = self.timeout)

        # Tant que l'on a pas le prompt, on considère que l'on est pas loggué.
        while True:
            try:
                # On liste toutes les possibilités.
                ret = self.child.expect([
                                         self.__first_connection,

                                         self.default_login_str,

                                         self.__kb_interractive % {'username': self.username},
                                         self.default_password_str,

                                         self.prompt,

                                         self.__exchange_id_conn_closed
                                        ])

                # La valeur de retour correspond à l'élément identifié dans la
                # liste.
                if ret == 0:
                    # Première connexion, on accèpte le nouvel hôte.
                    self.child.sendline('yes')

                if ret == 1:
                    # Demande du nom d'utilisateur.
                    self.child.sendline(self.username)

                if ret == 2 or ret == 3:
                    # Demande du mot de passe.
                    self.child.sendline(self.password)

                if ret == 4:
                    # On a le prompt.
                    return True

                if ret == 5:
                    return False
            except pexpect.TIMEOUT:
                return False
            except pexpect.EOF:
                return False



class Telnet(Connect):
    """
    Classe gérant la connexion Telnet vers un noeud.
    """

    ##
    # Note: telnet ne semble pas fonctionner dans un environnement Windows.
    ##

    def __init__(self, hostname, username, password =None, prompt =None,
                 timeout =15):
        """
        Constructeur de la classe Telnet.
        """

        Connect.__init__(self, hostname, username, password, prompt, timeout)



    def login(self, port = 23):
        """
        Cette méthode établi la connexion avec l'hôte.
        """

        try:
            self.child = pexpect.spawn('telnet -l %(username)s %(hostname)s %(port)i' % \
                                       {
                                        'username': self.username,
                                        'hostname': self.hostname,
                                        'port': port
                                       },
                                       timeout = self.timeout)

            # Tant que l'on a pas le prompt, on considère que l'on est pas loggué.
            while True:
                # On liste toutes les possibilités.
                ret = self.child.expect([
                                         self.default_login_str,

                                         self.default_password_str,

                                         self.prompt
                                        ])

                # La valeur de retour correspond à l'élément identifié dans la
                # liste.
                if ret == 0:
                    # Demande du nom d'utilisateur.
                    self.child.sendline(self.username)

                if ret == 1:
                    # Demande du mot de passe.
                    self.child.sendline(self.password)

                if ret == 2:
                    # On a le prompt.
                    return True
        except pexpect.TIMEOUT:
            return False
        except pexpect.EOF:
            return False
