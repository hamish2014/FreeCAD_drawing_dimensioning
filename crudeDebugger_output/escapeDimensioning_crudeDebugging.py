from crudeDebugger import crudeDebuggerPrint
crudeDebuggerPrint('''escapeDimensioning.py:0  	import os, FreeCADGui ''')
import os, FreeCADGui
crudeDebuggerPrint('''escapeDimensioning.py:1  	import FreeCAD as App ''')
import FreeCAD as App
crudeDebuggerPrint('''escapeDimensioning.py:2  	from PySide import QtGui ''')
from PySide import QtGui
crudeDebuggerPrint('''escapeDimensioning.py:3  	from dimensioning import __dir__ ''')
from dimensioning import __dir__

class EscapeDimensioning:
    def Activated(self):
        crudeDebuggerPrint('''escapeDimensioning.py:7  	        mw = QtGui.qApp.activeWindow() ''')
        mw = QtGui.qApp.activeWindow()
        crudeDebuggerPrint('''escapeDimensioning.py:8  	        MdiArea = [c for c in mw.children() if isinstance(c,QtGui.QMdiArea)][0] ''')
        MdiArea = [c for c in mw.children() if isinstance(c,QtGui.QMdiArea)][0]
        crudeDebuggerPrint('''escapeDimensioning.py:9  	        subWinMW = MdiArea.activeSubWindow().children()[3] ''')
        subWinMW = MdiArea.activeSubWindow().children()[3]
        crudeDebuggerPrint('''escapeDimensioning.py:10  	        page = App.ActiveDocument.getObject( subWinMW.objectName() ) ''')
        page = App.ActiveDocument.getObject( subWinMW.objectName() )
        crudeDebuggerPrint('''escapeDimensioning.py:11  	        page.touch() ''')
        page.touch()
        crudeDebuggerPrint('''escapeDimensioning.py:12  	        App.ActiveDocument.recompute() ''')
        App.ActiveDocument.recompute()
        
    def GetResources(self): 
        crudeDebuggerPrint('''escapeDimensioning.py:15  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'escape.svg' ) , 
            'MenuText': 'escape Dimensioning', 
            'ToolTip': 'escape Dimensioning'
            } 

crudeDebuggerPrint('''escapeDimensioning.py:21  	FreeCADGui.addCommand('escapeDimensioning', EscapeDimensioning()) ''')
FreeCADGui.addCommand('escapeDimensioning', EscapeDimensioning())