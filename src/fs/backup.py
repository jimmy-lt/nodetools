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
    Cette classe se charge de la gestion des fichiers de sauvegarde.
    """

    def __init__(self, root_directory):
        """
        Constructeur de la classe Backup.
        """

        # On conserve le chemin du dossier racine en prenant soin
        # d'enlever le séparateur final s'il existe. 
        self.__root_directory = re.sub(os.sep + '$', '', root_directory)
        self.logger = logging.getLogger('nodesnap')



    def __get_files_timestamp(self):
        # On retourne un dictionnaire ayant la forme :
        #   nom de fichier : date de création
        return dict([(self.__root_directory + os.sep + f, \
                      os.stat(self.__root_directory + os.sep + f).st_ctime) \
                     for f in self.get_filenames_list()])

    def __get_files_timestamp_by_pattern(self, pattern):
        return dict([(self.__root_directory + os.sep +f, \
                      util.date.str_to_date(f, pattern)) \
                      for f in self.get_filenames_list()])


    def get_filenames_list(self):
        """
        Retourne la liste des fichiers de sauvegarde contenus sur le disque.
        """

        if not os.path.exists(self.__root_directory):
            return list()

        # On récupère la liste des fichiers contenus dans le dossier.
        files = os.listdir(self.__root_directory)


        # On retourne cette liste en enlevant les fichiers commençant par un
        # point. Ceux-ci sont considérés cachés.
        return filter(lambda x: x.find('.') != 0, files)

    def get_most_recent_filename(self, pattern =None):
        """
        Cherche le fichier le plus récent contenu dans le dossier.
        """

        files_timestamp = dict()

        if pattern is not None:
            files_timestamp = self.__get_files_timestamp_by_pattern(pattern)
        else:
            # On récupère l'ensemble nom de fichier - date de création.
            files_timestamp = self.__get_files_timestamp()

        if not files_timestamp:
            return None

        # On retourne le nom du fichier ayant la date la plus élevée.
        return max(files_timestamp, key=lambda k: files_timestamp.get(k))

    def get_most_recent_file_content(self, pattern =None):
        """
        Retourne le contenu du fichier le plus récent.
        """

        last_file = self.get_most_recent_filename(pattern =pattern)
        if last_file is None: return list()

        f = open(last_file, 'r')

        # On place le contenu du fichier dans un tuple tout
        # en veyant à effacer les caractères non nécessaires. 
        content = list([(re.sub('[\b\s\n\r]*$', '', line)) \
                         for line in f.readlines()])
        f.close()


        return content



    def rotate(self, n):
        """
        Cette méthode supprime les n plus anciens fichiers du dossier.
        """

        # On récupère l'ensemble nom de fichier - date de création.
        files_timestamp = self.__get_files_timestamp()
        if files_timestamp and (len(files_timestamp) > n):
            # On prend les plus anciens fichiers et on les supprime.
            for f in sorted(files_timestamp, key=lambda k: files_timestamp.get(k))[:n]:
                os.unlink(f)

    def write(self, filename, content):
        """
        Cette méthode écrit un nouveau fichier dans le dossier de sauvegarde.
        """

        # Si le dossier n'existe pas, on le crée.
        if not os.path.exists(self.__root_directory):
            os.makedirs(self.__root_directory)

        # On ouvre le fichier et on y écrit le contenu.
        f = open(self.__root_directory + os.sep + filename, 'w')
        f.writelines('\n'.join(content))

        # Il s'agit d'une sauvegarde.
        # On s'assure donc que le système a bien écrit le fichier.
        f.flush()
        os.fsync(f.fileno())

        self.logger.info('%(path)s written.' % \
                         {'path': self.__root_directory + os.sep + filename})

        # Puis on ferme ce dernier.
        f.close()




if __name__ == '__main__':
    import sys



    if len(sys.argv) == 2:
        bak = Backup(sys.argv[1])

        print bak.get_most_recent_file()
        print bak.get_most_recent_file_content()

    if len(sys.argv) == 3:
        bak = Backup(sys.argv[1])
        pattern = sys.argv[2]

        print bak.get_most_recent_file(pattern)
        print bak.get_most_recent_file_content(pattern)