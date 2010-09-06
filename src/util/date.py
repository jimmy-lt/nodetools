# -*- coding: utf-8 -*-
#
# Package: util.date
#
try:
    import datetime
except ImportError, e:
    raise ImportError(str(e) +
"""
    A critical module could not be imported.
""")


__all__ = ['today_to_str', 'date_to_str', 'str_to_date']



def today_to_str(format):
    return datetime.date.today().strftime(format)

def date_to_str(date, format):
    return date.strftime(format)

def str_to_date(date_string, date_format):
    return datetime.datetime.strptime(date_string, date_format)



if __name__ == '__main__':
    pass
