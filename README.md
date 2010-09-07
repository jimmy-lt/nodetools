Nodesnap
=======

Nodesnap is a python utility to make network nodes backups.

This tool connects to your Cisco and OmniSwitch devices by Telnet or SSH and
then gets their running's configuration. This configuration is written on the
local host.


Install
-------

Nodesnap depends of the pexpect module (http://www.noah.org/wiki/Pexpect).
You must install it before using this tool.

Then install Nodesnap by using the setup.py file:
    python setup.py install

You can now run Nodesnap from your command line interface:
    nodesnap /path/to/config_file.ini


Features
--------

Nodesnap reads an INI file described futher. It will connect to all hosts
listed in this file. Nodesnap gets the host's running configuration and
compares it to the last saved configuration. If the new configuration differs,
this one is written on the disk.

Files are written on the disk by following this pattern:

    /root_directory/backup/(group)/(node's subsection)/file_pattern
    /root_directory/diff/(group)/(node's subsection)/file_pattern

Nodesnap supports Cisco and OmniSwitch devices. It can connect by SSH and
Telnet.

Nodesnap can sends e-mails containing the grabbed configuration and the
differences from the last backup.


Configuration
-------------

This utility needs an INI file for its configuration. Here are the different
sections and options.


### General sections

    [general]
    root_directory = (string) " Working directory in which backups will be stored.
    file_pattern   = (string) " Filename pattern.
                              " This pattern uses the Unix date format and a
                              " personal format:
                              "   - %0, node's hostname;
                              "   - %1, node's subsection name.
    rotation      = (integer) " Number of files to keep in each directory. If this
                              " number is reached, oldest files will be deleted.
    write_diff    = (bool)    " Do you want to write the difference between the
                              " last saved file and the running configuration?

    [contact]
    mail_server   = (string)  " Mail server address (localhost by default).
    sender        = (string)  " Sender's e-mail address.
    send_backup   = (bool)    " Send the last configuration.
    send_diff     = (bool)    " Send the differences from the last backup file.

    [contact::subsection]
    e-mail        = (string)  " Recipient's e-mail address.

### Node sections

The Cisco section [Cisco] or OmniSwitch section [OmniSwitch] share the same
options.

    [OmniSwitch] or [Cisco]
    connection    = (string)  " This option has two possible value: ssh or telnet.
    failover      = (string)  " This option is used when the 'connection' option
                              " fails. It takes the same values as the 'connection'
                              " option.
    options       = (string)  " Not used for now.
    username      = (string)  " Host user name.
    password      = (string)  " Host password.
    prompt        = (string)  " Host prompt (the value can be a regular expression).
    timeout       = (integer) " Maximum time to wait (default 15 seconds).

    [OmniSwitch::subsection] or [Cisco::subsection]
    hostname      = (string)  " Host address
    group         = (string)  " Host's group name. So, you can put many hosts
                              " together in the same directory.

### Good to know

All section options can be overloaded in subsections. So you can redefine an
already defined section's option in a subsection. The last one will be used.


Todo
----

- Packaging
- A prettier logger solution
- Threads support for parallel connections


Copyright
---------

Copyright (C) 2010  Jimmy Thrasibule

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as
  published by the Free Software Foundation, version 3 of the
  License.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  See the LICENSE file for the full license.
