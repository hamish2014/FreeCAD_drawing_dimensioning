
from dimensioning import *
from dimensioning import __dir__ # not imported with * directive

class EscapeDimensioning:
    def Activated(self):
        V = getDrawingPageGUIVars()
        V.page.touch()
        App.ActiveDocument.recompute()
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'escape.svg' ) , 
            'MenuText': 'escape Dimensioning', 
            'ToolTip': 'escape Dimensioning'
            } 

FreeCADGui.addCommand('escapeDimensioning', EscapeDimensioning())
