import dimensioning #QtCore.QResource.registerResource happens in there

class DrawingDimensioningWorkbench (Workbench):
    Icon = ':/dd/icons/linearDimension.svg'
    MenuText = 'Drawing Dimensioning'
    def Initialize(self):
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
        import table_dd
        import centerView
        import toleranceAdd
        import recomputeDimensions
        from drawing_wb_shortcuts import newpageShortcuts
        self.appendToolbar('Drawing Workbench shortcuts', newpageShortcuts + [
                    'dd_new_drawing_page_preferences',
                    'dd_Drawing_OrthoViews',                    
                    ] )
        # copy the Drawing toolbar
        import DrawingGui
        self.appendToolbar('Drawing Workbench Commands',["Drawing_NewPage",
                    "Drawing_NewView","Drawing_OrthoViews","Drawing_OpenBrowserView",
                    "Drawing_Annotation","Drawing_Clip","Drawing_Symbol",
                    "Drawing_DraftView","Drawing_ExportPage"])

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
 #           'dd_editText',   # no longer available to user, else to complicated! In particular multiple avenues available to user to change text properties
 #           'dd_moveText',   # therefore sticking with the FreeCAD way of doing things
            'dd_addTolerance', 
            'dd_addTable',
            'dd_deleteDimension', 
            'dd_escapeDimensioning',
            'dd_recomputeDimensions',
            ]
        self.appendToolbar('Drawing Dimensioning', commandslist)
        import unfold
        import unfold_bending_note
        import unfold_export_to_dxf
        unfold_cmds = [
            'dd_unfold',
            'dd_bendingNote',
            'dd_centerView',
            'dd_exportToDxf'
            ]
        self.appendToolbar( 'Drawing Dimensioning Folding', unfold_cmds )
        import weldingSymbols
        
        freecad_version = int( FreeCAD.Version()[1] )
        try:
           git_commit_no = int( FreeCAD.Version()[2].split()[0] )
        except:
           git_commit_no = -1
           freecad_version = int( FreeCAD.Version()[1] )

        if git_commit_no > 5166 or freecad_version > 15:
            weldingCommandList = ['dd_weldingGroupCommand']
        else:
            weldingCommandList = weldingSymbols.weldingCmds
        self.appendToolbar('Drawing Dimensioning Welding Symbols', weldingCommandList)
        self.appendToolbar('Drawing Dimensioning Help', [ 'dd_help' ])
        FreeCADGui.addIconPath(':/dd/icons')
        FreeCADGui.addPreferencePage( ':/dd/ui/drawing_dimensioing_prefs-base.ui','Drawing Dimensioning' )


Gui.addWorkbench(DrawingDimensioningWorkbench())


