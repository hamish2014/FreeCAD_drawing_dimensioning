from crudeDebugger import crudeDebuggerPrint

crudeDebuggerPrint('''escapeDimensioning.py:1  	from dimensioning import * ''')
from dimensioning import *
crudeDebuggerPrint('''escapeDimensioning.py:2  	from dimensioning import __dir__ # not imported with * directive ''')
from dimensioning import __dir__ # not imported with * directive

class EscapeDimensioning:
    def Activated(self):
        crudeDebuggerPrint('''escapeDimensioning.py:6  	        V = getDrawingPageGUIVars() ''')
        V = getDrawingPageGUIVars()
        crudeDebuggerPrint('''escapeDimensioning.py:7  	        V.page.touch() ''')
        V.page.touch()
        crudeDebuggerPrint('''escapeDimensioning.py:8  	        App.ActiveDocument.recompute() ''')
        App.ActiveDocument.recompute()
        
    def GetResources(self): 
        crudeDebuggerPrint('''escapeDimensioning.py:11  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'escape.svg' ) , 
            'MenuText': 'escape Dimensioning', 
            'ToolTip': 'escape Dimensioning'
            } 

crudeDebuggerPrint('''escapeDimensioning.py:17  	FreeCADGui.addCommand('escapeDimensioning', EscapeDimensioning()) ''')
FreeCADGui.addCommand('escapeDimensioning', EscapeDimensioning())