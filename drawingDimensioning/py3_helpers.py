import sys
from PySide import QtGui

if sys.version_info.major >= 3:
    def unicode(*args):
        return str(args[0])
    unicode_type = str
else:
    unicode = unicode
    unicode_type = unicode

def translate(*args):
    if len(args) < 3:
        args.append(None)
    if sys.version_info.major < 3:
        return QtGui.QApplication.translate(args[0], args[1], args[2], QtGui.QApplication.UnicodeUTF8)
    else:
        return QtGui.QApplication.translate(args[0], args[1], args[2])

def encode_if_py2(unicode_object):
	'''return unicode for py3 and bytes for py2'''
	if sys.version_info.major < 3:
		return unicode_object.decode("utf8")
	else:
		return unicode_object

_map = map

def map(function, arg):
    return list(_map(function, arg))
