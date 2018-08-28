from crudeDebugger import crudeDebuggerPrint

crudeDebuggerPrint('''deleteDimension.py:1  	from dimensioning import * ''')
from dimensioning import *
crudeDebuggerPrint('''deleteDimension.py:2  	from dimensioning import __dir__ # not imported with * directive ''')
from dimensioning import __dir__ # not imported with * directive
crudeDebuggerPrint('''deleteDimension.py:3  	from selectionOverlay import generateSelectionGraphicsItems ''')
from selectionOverlay import generateSelectionGraphicsItems

crudeDebuggerPrint('''deleteDimension.py:5  	dimensioning = DimensioningProcessTracker() ''')
dimensioning = DimensioningProcessTracker()

def deleteDimension( event, referer, elementXML, elementParms, elementViewObject ):
    crudeDebuggerPrint('''deleteDimension.py:8  	    debugPrint(2, 'deleting dimension %s' % elementViewObject.Name) ''')
    debugPrint(2, 'deleting dimension %s' % elementViewObject.Name)
    crudeDebuggerPrint('''deleteDimension.py:9  	    App.ActiveDocument.removeObject( elementViewObject.Name ) ''')
    App.ActiveDocument.removeObject( elementViewObject.Name )
    crudeDebuggerPrint('''deleteDimension.py:10  	    dimensioning.drawingVars.page.touch() ''')
    dimensioning.drawingVars.page.touch()
    crudeDebuggerPrint('''deleteDimension.py:11  	    App.ActiveDocument.recompute() ''')
    App.ActiveDocument.recompute()


crudeDebuggerPrint('''deleteDimension.py:14  	maskBrush  =   QtGui.QBrush( QtGui.QColor(160,0,0,100) ) ''')
maskBrush  =   QtGui.QBrush( QtGui.QColor(160,0,0,100) )
crudeDebuggerPrint('''deleteDimension.py:15  	maskPen =      QtGui.QPen( QtGui.QColor(160,0,0,100) ) ''')
maskPen =      QtGui.QPen( QtGui.QColor(160,0,0,100) )
crudeDebuggerPrint('''deleteDimension.py:16  	maskPen.setWidth(0.0) ''')
maskPen.setWidth(0.0)
crudeDebuggerPrint('''deleteDimension.py:17  	maskHoverPen = QtGui.QPen( QtGui.QColor(255,0,0,255) ) ''')
maskHoverPen = QtGui.QPen( QtGui.QColor(255,0,0,255) )
crudeDebuggerPrint('''deleteDimension.py:18  	maskHoverPen.setWidth(0.0) ''')
maskHoverPen.setWidth(0.0)
    
class DeleteDimension:
    def Activated(self):
        crudeDebuggerPrint('''deleteDimension.py:22  	        V = getDrawingPageGUIVars() ''')
        V = getDrawingPageGUIVars()
        crudeDebuggerPrint('''deleteDimension.py:23  	        dimensioning.activate(V) ''')
        dimensioning.activate(V)
        crudeDebuggerPrint('''deleteDimension.py:24  	        selectGraphicsItems = generateSelectionGraphicsItems( ''')
        selectGraphicsItems = generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if obj.Name.startswith('dim')], 
            deleteDimension , 
            sceneToAddTo = V.graphicsScene, 
            transform = V.transform,
            doTextItems = True, 
            pointWid=2.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )

        
    def GetResources(self): 
        crudeDebuggerPrint('''deleteDimension.py:38  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'deleteDimension.svg' ) , 
            'MenuText': 'Delete Dimension', 
            'ToolTip': 'Delete a dimension'
            } 

crudeDebuggerPrint('''deleteDimension.py:44  	FreeCADGui.addCommand('deleteDimension', DeleteDimension()) ''')
FreeCADGui.addCommand('deleteDimension', DeleteDimension())