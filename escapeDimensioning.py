import os, FreeCADGui
import FreeCAD as App
from PySide import QtGui
from dimensioning import __dir__, get_FreeCAD_drawing_variables

class EscapeDimensioning:
    def Activated(self):
        vars = {}
        if not get_FreeCAD_drawing_variables(vars):
            return
        vars['page'].touch()
        App.ActiveDocument.recompute()
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'escape.svg' ) , 
            'MenuText': 'escape Dimensioning', 
            'ToolTip': 'escape Dimensioning'
            } 

FreeCADGui.addCommand('escapeDimensioning', EscapeDimensioning())
