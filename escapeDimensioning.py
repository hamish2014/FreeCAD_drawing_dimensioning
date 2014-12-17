
from dimensioning import *
from dimensioning import iconPath # not imported with * directive

class EscapeDimensioning:
    def Activated(self):
        drawingVars = getDrawingPageGUIVars()
        drawingVars.page.touch()
        App.ActiveDocument.recompute()
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'escape.svg' ) , 
            'MenuText': 'escape Dimensioning', 
            'ToolTip': 'escape Dimensioning'
            } 

FreeCADGui.addCommand('escapeDimensioning', EscapeDimensioning())
