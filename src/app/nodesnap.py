# -*- coding: utf-8 -*-
#
# Package: app.nodesnap
#
try:
    import logging
    import logging.handlers

    import re
    import os

    from fs import backup
    from net import mail, node
    from util import config, date, text
except ImportError, e:
    raise ImportError(str(e) +
"""
    A critical module could not be imported.
""")



class Nodesnap(object):
    """
    This is the main class for the nodesnap application.

    my_app = Nodesnap('/path/to/my/config_file')
    my_app.run()
    """

    __info_format  = '%(asctime)s: %(levelname)s: %(message)s'
    __debug_format = '%(asctime)s: %(levelname)s: %(module)s.%(funcName)s() at line %(lineno)d, %(message)s'



    def __init__(self, config_file):
        """
        Nodesnap constructor.

        @param config_file:
            Path to INI configuration file.
        """

        # Parse and load the configuration file.
        self.config = config.Config(config_file)

        # Setup the logger.
        # TODO: put the logger in its own class and make it prettier.
        self.logger  = None
        self.handler = None
        self.__set_logger('nodesnap', 'nodesnap.log', logging.DEBUG)

    def __del__(self):
        """
        Desctructor for the Nodesnap class.
        """

        # We want one log file by run.
        # So we do a rollover on exit.
        if self.handler:
            self.handler.doRollover()


    def get_config_value(self, section, option):
        """
        A safe wrapper in order to get an option from the configuration.

        @param section:
            Configuration's section name.

        @param option:
            Section's option to get the value from.
        """

        # This may not be very useful.
        if self.config.has_option(section, option):
            return self.config.get_value(section, option)
        return None

    def __set_logger(self, name, filename, log_level):
        """
        Configure the logger and returns it.
        """

        # Get the logger from the name.
        # TODO: add some configuration options for the logging.
        self.logger  = logging.getLogger(name)
        self.handler = logging.handlers.RotatingFileHandler(filename,
                                                            mode ='w',
                                                            backupCount =7)

        # We use a different format for debugging purpose.
        if log_level == logging.INFO:
            self.handler.setFormatter(logging.Formatter(self.__info_format))
        else:
            self.handler.setFormatter(logging.Formatter(self.__debug_format))

        self.logger.setLevel(log_level)
        self.logger.addHandler(self.handler)


    def get_root_directory(self, item, node_section):
        """
        This method returns the root directory for the given node section.

        @param item:
            The item parameter must be 'diff' or 'backup'.

            If it is set to 'diff', the root directory to store diffs will be
            returned.

            If it is set to 'backup', the root directory to store backups will
            be returned.

        @param node_section:
            For which node do we have to return the root directory ?
        """

        # We first remove any leading separator in the main directory path.
        root_directory = re.sub(os.sep + '$', '',
                                self.get_config_value('general', 'root_directory'))

        # Then we add the backup or the diff directory.
        if item == 'backup':
            root_directory += os.sep + 'backup'
        elif item == 'diff':
            root_directory += os.sep + 'diff'

        # We look if the node is part of a group and if so we add it to the
        # path.
        if self.config.has_option(node_section, 'group'):
            root_directory += os.sep \
                              + self.get_config_value(node_section, 'group')

        # Finally, we add the subsection name to the path.
        root_directory += os.sep \
                          + self.config.get_subsection_name(node_section)

        self.logger.debug('root_directory:' + root_directory)
        return root_directory


    def connect(self, node_section):
        """
        This method tries to connect to the given node.

        This method is set up in two tries.

        It will first try to use the mode provided by the 'connection' option.
        If this one fails it will try the 'failover' option.

        @param node_section:
            Node's configuration section.
        """

        hostname   = self.get_config_value(node_section, 'hostname')
        connection = self.get_config_value(node_section, 'connection')
        failover   = self.get_config_value(node_section, 'failover')
        username   = self.get_config_value(node_section, 'username')
        password   = self.get_config_value(node_section, 'password')
        prompt     = self.get_config_value(node_section, 'prompt')
        timeout    = self.get_config_value(node_section, 'timeout')

        node_type  = self.config.get_parent_section_name(node_section)
        host = None

        self.logger.info('Connecting %(n)s %(h)s with: connection %(c)s, failover %(f)s, prompt %(p)s, timeout %(t)s.' % \
                          {'n': node_type,
                           'h': hostname,
                           'c': connection,
                           'f': failover,
                           'p': prompt,
                           't': timeout})

        fail = False
        while True:
            mode = None

            # If we have not encounter a connection failure,
            if not fail:
                # we set the connection mode to the specified one.
                mode = connection

                self.logger.info('Connecting to %(h)s using %(m)s.' % \
                                 {'h': hostname,
                                  'm': mode})
            elif fail and failover:
                # Else, we try the fail over if exists.
                mode = failover

                self.logger.info('Connecting to %(h)s using %(m)s.' % \
                                 {'h': hostname,
                                  'm': mode})
            else:
                # We don't have fail over solution so we quit.
                self.logger.info('Connection to %(h)s failed.' % \
                                 {'h': hostname})
                return None

            if node_type == 'Cisco':
                host = node.Cisco(mode, hostname, username, password, prompt,
                                  timeout)
            if node_type == 'OmniSwitch':
                host = node.OmniSwitch(mode, hostname, username, password,
                                       prompt, timeout)

            if host:
                # We have an host so we try to connect to it.
                if host.connect():
                    # Connection succeed.
                    self.logger.info('Connection to %(h)s succeed.' % \
                                     {'h': hostname})
                    return host
            if fail:
                # If we are here, this mean that we are trying the fail over
                # solution and it failed too. So we quit.
                self.logger.info('Connection to %(h)s failed.' % \
                                 {'h': hostname})
                return None

            # If we reach here, the first try failed.
            self.logger.info('Connection %(m)s failed.' % {'m': mode})
            fail = True

    def format_filename(self, node_section, host, apply_date =True):
        """
        This method create a filename for the given node section according
        to the 'pattern' configuration option.

        This pattern uses the Unix date format for date support and a private
        format.

        - %0: Node's hostname.
        - %1: Node's subsection name.
        """

        pattern = self.get_config_value('general', 'file_pattern')
        self.logger.debug('Input pattern: ' + pattern)

        pattern = re.sub('%0',
                         host.get_hostname(),
                         pattern)
        pattern = re.sub('%1',
                         self.config.get_subsection_name(node_section),
                         pattern)

        self.logger.debug('Pattern before applying date: ' + pattern)
        if apply_date:
            return date.today_to_str(pattern)
        return pattern

    def run(self):
        """
        Main method for the nodesnap application. This method is the only one
        you may need to call and it will do the rest.
        """

        # Get all node sections from the configuration.
        sections = self.config.get_nodes_section()

        # Loop for each node's type
        for key in sections.keys():
            self.logger.debug('Loop for ' + key)

            # Loop for each node of this type.
            for node_section in sections.get(key):
                self.logger.debug('Section ' + node_section)

                # We first try to connect the node.
                host = self.connect(node_section)
                if not host:
                    # If we can't connect, we pass.
                    continue

                # Set up the backup's root directory and filename.
                config_directory = self.get_root_directory('backup', node_section)
                filename = self.format_filename(node_section, host)

                # We get the running configuration without any comments.
                running_config = host.get_config(True, True)

                # Print the running configuration contents for debugging.
                self.logger.debug('**** Running config ***')
                for line in running_config:
                    self.logger.debug(line)

                # We create a new Backup object to store the running configuration.
                config_bak = backup.Backup(config_directory)

                # The pattern will help use to find the most recent file.
                # TODO: add an option to specify if we want to use it or not.
                pattern = self.format_filename(node_section, host, False)
                last_bak = config_bak.get_most_recent_file_content(pattern)

                if not last_bak:
                    # There is no file.
                    # So, we can write our backup without any other test.
                    config_bak.write(filename, running_config)

                    # Lets send the running configuration.
                    self.send('backup', node_section, running_config)
                else:
                    # We found an older backup file.

                    # Lets print its content for debugging.
                    self.logger.debug('**** Last config ***')
                    for line in last_bak:
                        self.logger.debug(line)

                    # Once again we use the pattern to get the most recent
                    # backup's filename.
                    last_filename = config_bak.get_most_recent_filename(pattern)

                    # Then we compare both old backup and currently running
                    # configuration.
                    delta = text.compare(last_bak, running_config)
                    if delta:
                        # We found some differences so we can write the backup
                        # file and send it.
                        config_bak.write(filename, running_config)
                        self.send('backup', node_section, running_config)

                        if self.get_config_value('general', 'write_diff'):
                            # If the user wants to store the diff we create a
                            #new backup object for this one.
                            delta_directory = self.get_root_directory('diff',
                                                                      node_section)
                            delta_bak = backup.Backup(delta_directory)

                            # We add the filenames in top of diff file.
                            delta.insert(0, '%(old)s -> %(new)s\n\n' % \
                                            {'old': last_filename,
                                             'new': filename})

                            delta_bak.write(filename, delta)
                            self.send('diff', node_section, delta)

                            # Apply file rotation on the diff directory.
                            delta_bak.rotate(self.get_config_value('general', 'rotation'))

                # Apply file rotation on the backup directory.
                config_bak.rotate(self.get_config_value('general', 'rotation'))

                host.quit()

    def send(self, item, node_section, msg):
        """
        This method sends the given message to involved contacts.
        """

        sections = self.config.get_subsections('contact')

        for contact in sections.get('contact'):
            sender = self.get_config_value(contact, 'sender')
            mail_server = self.get_config_value(contact, 'mail_server')
            to = self.get_config_value(contact, 'e-mail')

            # The title is set according to the 'item' parameter.
            title = ''
            if item == 'backup' and self.get_config_value('contact', 'send_backup'):
                title = 'New configuration for '
            elif item == 'diff' and self.get_config_value('contact', 'send_diff'):
                title = 'New change on '
            else: return

            title += self.config.get_subsection_name(node_section) \
                     + ' (' \
                     + self.get_config_value(node_section, 'hostname') \
                     + ')'

            email = mail.Mail(sender =sender, to =to, subject =title, message =msg)
            if mail_server:
                email.set_server(mail_server)

            email.send()
