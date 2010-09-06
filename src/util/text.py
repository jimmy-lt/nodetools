# -*- coding: utf-8 -*-
#
# Package: util.text
#
try:
    import difflib
    import math
    import re
except ImportError, e:
    raise ImportError(str(e) +
"""
    A critical module could not be imported.
""")


__all__ = ['compare']



def compare(old, new):
    """
    Cette fonction compare les chaînes de caractères contenues dans deux
    listes.
    """

    # Le résultat est placé dans une liste.
    out = list()
    # Format de la ligne qui sera mise dans la liste.
    output_format = '%(line_number)i%(separator)s%(spaces)s%(line)s'
    # Séparateur remplaçant le mot clé 'separator' dans la ligne.
    separator = ': '

    # On stock le résultat obtenu dans une liste.
    delta  = list(difflib.ndiff(old, new))

    # Pour un affichage cohérent, on cacule le nombre d'espaces maximum.
    # Cela dépend du nombre total de ligne.
    #
    # On additionne donc le nombre de chiffre maximum au nombre de caractères
    # du séparateur. 
    spaces = (int(math.log10(len(delta))) + 1) + len(separator)

    # Dans un dictionnaire, on fait correspondre les lignes de chaque liste avec
    # avec leur numéro.
    old_lines = dict([(re.sub('\n$', '', line), old.index(line) + 1) \
                       for line in old])
    new_lines = dict([(re.sub('\n$', '', line), new.index(line) + 1) \
                       for line in new])


    # On parcours les lignes du résultat.
    for line in delta:
        match_del = re.match('^- (.*)', line)
        match_add = re.match('^\+ (.*)', line)
        match_hlp = re.match('^\? (.*)', line)

        line_number = None
        line = re.sub('[\b\s\n\r]*$', '', line)

        # Suppression d'une ligne
        if match_del:
            # On récupère le numéro de la ligne supprimée au niveau des
            # anciennes données.
            line_number = old_lines.get(match_del.group(1))
        # Ajout d'une ligne
        elif match_add:
            # On récupère le numéro de la ligne ajoutée au niveau des
            # nouvelles données.
            line_number = new_lines.get(match_add.group(1))

        # Si on a un numéro de ligne,
        if line_number is not None:
            # on soustraits le nombre de chiffres de la ligne et le nombre
            # de caractères contenus dans le séparateur au nombre d'espaces
            # maximums.
            line_spaces = spaces - (int(math.log10(line_number)) + 1) - len(separator)

            # Puis on ajoute à notre liste de sortie la ligne résultante.
            out.append(output_format % {'line_number': line_number,
                                        'separator': separator,
                                        'spaces': ' ' * line_spaces,
                                        'line': line})
        # Ligne d'information,
        elif match_hlp:
            # on l'ajoute avec le nombre d'espaces maximum.
            out.append((' ' * spaces) + line)


    return out


def clear_comments(content, marker):
    out = list()
    for line in content:
        if re.match('^\s*' + marker + '+.*$', line):
            continue

        comment = re.match('^.*(\s*' + marker + '+.*)$', line)
        if comment:
            line = re.sub(comment.group(1), '', line)
        out.append(line)

    return out




if __name__ == '__main__':
    pass
