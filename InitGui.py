
class DimensioningWorkbench (Workbench): 
    # Icon generated using Gimp to convert linearDimension.svg to xpm format
    Icon = '''
/* XPM */
static char * linearDimension_xpm[] = {
"32 32 10 1",
"       c None",
".      c #000000",
"+      c #0008FF",
"@      c #0009FF",
"#      c #000AFF",
"$      c #00023D",
"%      c #0008F7",
"&      c #0008EE",
"*      c #000587",
"=      c #000001",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".      +@@             +       .",
".    @+@@+            +@@+@    .",
". +@+@@@@@@          @@@@@@@#  .",
"$%@@@@@@@@@+@@@@@@@@@@@@@@@@@@&$",
". #@@@@@@@@         #+@@@@@@@@*=",
".    @+@@+            +@@@@@   .",
".      +@             #@++     .",
".                      #       .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              ."};
'''
    MenuText = 'Drawing Dimensioning'
    def Initialize(self):
        import importlib, os
        from dimensioning import __dir__, debugPrint, iconPath
        DEBUG=False
        if DEBUG:
            import crudeDebugger
        for module in ['linearDimension', 'deleteDimension', 'circularDimension', 'textAdd', 'textEdit', 'textMove','escapeDimensioning', 'angularDimension' ,'radiusDimension']:
            if not DEBUG:
                importlib.import_module( module )
            else:
                crudeDebugger.printingDebugging( os.path.join(__dir__, module + '.py') )
                importlib.import_module(  module + '_crudeDebugging')
        commandslist = ['linearDimension', 'circularDimension', 'radiusDimension', 'angularDimension', 'textAddDimensioning','textEditDimensioning', 'textMoveDimensioning', 'deleteDimension', 'escapeDimensioning']
        self.appendToolbar('Drawing Dimensioning', commandslist)
        FreeCADGui.addIconPath(iconPath)
        FreeCADGui.addPreferencePage( os.path.join( __dir__, 'Resources', 'ui', 'drawing_dimensioing_prefs-base.ui'),'Drawing Dimensioning' )


Gui.addWorkbench(DimensioningWorkbench())
