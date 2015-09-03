from dimensioning import *


class NewPageCommand:
    def Activated(self):
        Page = FreeCAD.ActiveDocument.addObject('Drawing::FeaturePage','Page')
        Page.Template = '/usr/share/freecad/Mod/Drawing/Templates/A4_Landscape.svg'
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.getObject(Page.Name).show()

    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'drawing-landscape-new.svg' ) , 
            'MenuText': 'Shortcut for creating a new drawing page', 
            } 

FreeCADGui.addCommand('dd_new_drawing_page', NewPageCommand())

class DrawingOrthoViewsCommand:
    def Activated(self):
        FreeCADGui.runCommand('Drawing_OrthoViews')
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'drawing-orthoviews.svg' ) , 
            'MenuText': 'Shortcut to Drawing-OrthoViews Command', 
            } 

FreeCADGui.addCommand('dd_Drawing_OrthoViews', DrawingOrthoViewsCommand())
