import os, sys
sys.path.append( os.path.dirname( os.path.dirname( os.path.dirname( __file__ ) ) ) )
#print( sys.path[-1] )
sys.path.append('/usr/lib/freecad/lib/')
try:
    import FreeCAD, FreeCADGui
except ImportError as msg:
    print('Import error, is this testing script being run from Python2?')
    raise ImportError(msg)
assert not hasattr(FreeCADGui, 'addCommand')

def addCommand_check( name, command):
    pass
    #if not name.startswith('dd_'):
    #    raise ValueError('%s does not begin with %s' % ( name, 'assembly2_' ) )

FreeCADGui.addCommand = addCommand_check
