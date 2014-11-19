import os, FreeCADGui
import FreeCAD as App
from PySide import QtGui
from dimensioning import __dir__

class EscapeDimensioning:
    def Activated(self):
        mw = QtGui.qApp.activeWindow()
        MdiArea = [c for c in mw.children() if isinstance(c,QtGui.QMdiArea)][0]
        subWinMW = MdiArea.activeSubWindow().children()[3]
        page = App.ActiveDocument.getObject( subWinMW.objectName() )
        page.touch()
        App.ActiveDocument.recompute()
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'escape.svg' ) , 
            'MenuText': 'escape Dimensioning', 
            'ToolTip': 'escape Dimensioning'
            } 

FreeCADGui.addCommand('escapeDimensioning', EscapeDimensioning())
