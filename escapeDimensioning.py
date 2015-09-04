
from dimensioning import *

class EscapeDimensioning:
    def Activated(self):
        drawingVars = getDrawingPageGUIVars()
        drawingVars.page.touch()
        App.ActiveDocument.recompute()
        
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/escape.svg' , 
            'MenuText': 'escape Dimensioning', 
            'ToolTip': 'escape Dimensioning'
            } 

FreeCADGui.addCommand('dd_escapeDimensioning', EscapeDimensioning())
