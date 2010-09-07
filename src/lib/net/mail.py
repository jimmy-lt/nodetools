# -*- coding: utf-8 -*-
#
# Package: net.mail
#
try:
    import logging
    import smtplib

    from email.mime.text import MIMEText
    from email.Utils import COMMASPACE, formatdate
except ImportError, e:
    raise ImportError(str(e) +
"""
    A critical module could not be imported.
""")


__all__ = ['Mail']



class Mail(object):
    """
    Classe permettant d'envoyer un e-mail.
    """

    def __init__(self, sender =None, to =None, subject =None, message =None):
        """
        Constructeur de la classe Mail.
        """

        # Mise en place des différents éléments composant l'e-mail.
        self.__from    = ''
        self.__to      = []
        self.__subject = ''
        self.__message = ''
        
        # Par défaut, le serveur SMTP est l'hôte local.
        self._server  = 'localhost'
        
        self.logger   = logging.getLogger('nodesnap')


        if sender is not None:
            self.set_sender(sender)

        if to is not None:
            self.add_receiver(to)

        if subject is not None:
            self.set_subject(subject)

        if message is not None:
            self.set_message(message)



    def set_message(self, message):
        """
        Définit un nouveau message.
        """

        if type(message) == list:
            self.__message = ''

            for line in message:
                self.__message += line + '\n'
        elif type(message) == str:
            self.__message = message
        else:
            raise TypeError("'message' parameter type must be either list or str.")


    def get_message(self):
        """
        Retourne le message contenu dans le mail.
        """

        return self.__message

    def add_to_message(self, message):
        """
        Ajoute le message passé en paramètre au message déjà présent dans le
        mail.
        """

        if type(message) == list:
            for line in message:
                self.__message += line + '\n'
        elif type(message) == str:
            self.__message += message
        else:
            raise TypeError("'message' parameter type must be either list or str.")

    def clear_message(self):
        """
        Efface le message du mail.
        """

        self.__message = ''


    def set_sender(self, sender):
        """
        Définit l'émetteur du message.
        """

        self.__from = sender

    def get_sender(self):
        """
        Retourne l'émetteur du message.
        """

        return self.__from


    def set_subject(self, subject):
        """
        Définit le sujet du message.
        """

        self.__subject = subject

    def get_subject(self):
        """
        Retourne le sujet du message.
        """

        return self.__subject


    def add_recipient(self, to):
        """
        Add  
        """

        self.__to.append(to)

    def get_recipient(self):
        """
        Returns the recipients list.
        """

        return self.__to

    def remove_recipient(self, to):
        """
        Removes the given recipient from the recipients list.
        """

        self.__to.remove(to)


    def set_server(self, server):
        """
        Defines mail server address.
        
        @param server:
            Mail server address.
        """

        self._server = server

    def get_server(self):
        """
        Returns mail server address.
        """

        return self._server


    def send(self):
        """
        Sends and e-mail.
        """

        mail = MIMEText(self.get_message())
        mail['From'] = self.get_sender()
        mail['To'] = COMMASPACE.join(self.get_receiver())
        mail['Date'] = formatdate(localtime=True)
        mail['Subject'] = self.get_subject()

        self.logger.debug('Mail server: ' + self.get_server())
        self.logger.info('Sending mail \'%(s)s\' to %(t)s.' % \
                         {'s': self.get_subject(),
                          't': ', '.join(self.get_receiver())})

        smtp = smtplib.SMTP(self.get_server())
        smtp.sendmail(self.get_sender(), self.get_recipient(), mail.as_string())
        smtp.quit()
