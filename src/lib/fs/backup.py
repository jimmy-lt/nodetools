# -*- coding: utf-8 -*-
#
# Package: fs.backup
#
try:
    import re
    import os
    import logging
    import util.date
except ImportError, e:
    raise ImportError(str(e) +
"""
    A critical module could not be imported.
""")


__all__ = ['Backup']



class Backup(object):
    """
    This class manages backup files.
    """

    def __init__(self, root_directory):
        """
        Backup constructor.
        """

        self.__root_directory = re.sub(os.sep + '$', '', root_directory)
        self.logger = logging.getLogger('nodesnap')



    def __get_files_timestamp(self):
        """
        Returns a dictionary containing all backup files timestamp using
        operating system capabilities.
        """

        return dict([(self.__root_directory + os.sep + f, \
                      os.stat(self.__root_directory + os.sep + f).st_ctime) \
                     for f in self.get_filenames_list()])

    def __get_files_timestamp_by_pattern(self, pattern):
        """
        Returns a dictionary containing all backup files timestamp using
        dates in files name.
        """

        return dict([(self.__root_directory + os.sep +f, \
                      util.date.str_to_date(f, pattern)) \
                      for f in self.get_filenames_list()])


    def get_filenames_list(self):
        """
        Returns backup directory files list.
        """

        if not os.path.exists(self.__root_directory):
            return list()

        files = os.listdir(self.__root_directory)


        return filter(lambda x: x.find('.') != 0, files)

    def get_most_recent_filename(self, pattern =None):
        """
        Returns most recent backup file's name.
        """

        files_timestamp = dict()

        if pattern is not None:
            files_timestamp = self.__get_files_timestamp_by_pattern(pattern)
        else:
            files_timestamp = self.__get_files_timestamp()

        if not files_timestamp:
            return None

        return max(files_timestamp, key=lambda k: files_timestamp.get(k))

    def get_most_recent_file_content(self, pattern =None):
        """
        Returns most recent backup file's content.
        """

        last_file = self.get_most_recent_filename(pattern =pattern)
        if last_file is None:
            return list()

        f = open(last_file, 'r')
        content = list([(re.sub('[\b\s\n\r]*$', '', line)) \
                         for line in f.readlines()])
        f.close()


        return content



    def rotate(self, n):
        """
        Remove oldest files in the backup directory.
        
        :param n:
            Number of files to keep.
        """

        files_timestamp = self.__get_files_timestamp()
        if files_timestamp and (len(files_timestamp) > n):
            # We remove oldest files.
            for f in sorted(files_timestamp, key=lambda k: files_timestamp.get(k))[:n]:
                os.unlink(f)

    def write(self, filename, content):
        """
        This method writes the given content in the backup directory.
        
        :param filename:
            File name.
        :param content:
            File content.
        """

        # We create the directory if it doesn't exists.
        if not os.path.exists(self.__root_directory):
            os.makedirs(self.__root_directory)

        # We open the file and write its content.
        f = open(self.__root_directory + os.sep + filename, 'w')
        f.writelines('\n'.join(content))

        # We make sure that the file is really written on the disk.
        f.flush()
        os.fsync(f.fileno())

        self.logger.info('%(path)s written.' % \
                         {'path': self.__root_directory + os.sep + filename})

        # Closing the file.
        f.close()
