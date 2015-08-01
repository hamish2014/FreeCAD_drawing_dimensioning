class DrawingDimensioningWorkbench (Workbench):
    # Icon generated using by converting linearDimension.svg to xpm format using Gimp
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
        import linearDimension
        import linearDimension_stack
        import deleteDimension
        import circularDimension
        import grabPointAdd
        import textAdd
        import textEdit
        import textMove
        import escapeDimensioning
        import angularDimension
        import radiusDimension
        import centerLines
        import noteCircle
        import toleranceAdd
        commandslist = [
            'dd_linearDimension', #where dd is short-hand for drawing dimensioning
            'dd_linearDimensionStack',
            'dd_circularDimension',
            'dd_radiusDimension',
            'dd_angularDimension',
            'dd_centerLines',
            'dd_centerLine', 
            'dd_noteCircle', 
            'dd_grabPoint',
            'dd_addText',
            'dd_editText',
            'dd_moveText',
            'dd_addTolerance', 
            'dd_deleteDimension', 
            'dd_escapeDimensioning',
            ]
        self.appendToolbar('Drawing Dimensioning', commandslist)
        import unfold
        import unfold_bending_note
        import unfold_export_to_dxf
        unfold_cmds = [
            'dd_unfold',
            'dd_bendingNote',
            ]
        if hasattr(os,'uname') and os.uname()[0] == 'Linux' : #this command only works on Linux systems
            unfold_cmds.append('dd_exportToDxf')
        self.appendToolbar( 'Drawing Dimensioning Folding', unfold_cmds )
        import weldingSymbols
        if int( FreeCAD.Version()[1] > 15 ) and  int( FreeCAD.Version()[2].split()[0] ) > 5165:
            weldingCommandList = ['dd_weldingGroupCommand']
        else:
            weldingCommandList = weldingSymbols.weldingCmds
        self.appendToolbar('Drawing Dimensioning Welding Symbols', weldingCommandList)
        self.appendToolbar('Drawing Dimensioning Help', [ 'dd_help' ])
        FreeCADGui.addIconPath(iconPath)
        FreeCADGui.addPreferencePage( os.path.join( __dir__, 'Resources', 'ui', 'drawing_dimensioing_prefs-base.ui'),'Drawing Dimensioning' )


Gui.addWorkbench(DrawingDimensioningWorkbench())


