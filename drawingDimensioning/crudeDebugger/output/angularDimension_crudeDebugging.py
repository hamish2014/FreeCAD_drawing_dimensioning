from crudeDebugger import crudeDebuggerPrint

crudeDebuggerPrint('''angularDimension.py:1  	from dimensioning import * ''')
from dimensioning import *
crudeDebuggerPrint('''angularDimension.py:2  	from dimensioning import __dir__ # not imported with * directive ''')
from dimensioning import __dir__ # not imported with * directive
crudeDebuggerPrint('''angularDimension.py:3  	import selectionOverlay, previewDimension ''')
import selectionOverlay, previewDimension
crudeDebuggerPrint('''angularDimension.py:4  	from dimensionSvgConstructor import angularDimensionSVG ''')
from dimensionSvgConstructor import angularDimensionSVG

crudeDebuggerPrint('''angularDimension.py:6  	dimensioning = DimensioningProcessTracker() ''')
dimensioning = DimensioningProcessTracker()
        
def selectFun( event, referer, elementXML, elementParms, elementViewObject ):
    crudeDebuggerPrint('''angularDimension.py:9  	    x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ] ''')
    x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
    crudeDebuggerPrint('''angularDimension.py:10  	    debugPrint(2, 'selecting line %i with x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (dimensioning.stage, x1,y1,x2,y2) ) ''')
    debugPrint(2, 'selecting line %i with x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (dimensioning.stage, x1,y1,x2,y2) )
    crudeDebuggerPrint('''angularDimension.py:11  	    referer.lockSelection() ''')
    referer.lockSelection()
    crudeDebuggerPrint('''angularDimension.py:12  	    if dimensioning.stage == 0: #then select line1 ''')
    if dimensioning.stage == 0: #then select line1
        crudeDebuggerPrint('''angularDimension.py:13  	        dimensioning.line1 = x1,y1,x2,y2 ''')
        dimensioning.line1 = x1,y1,x2,y2
        crudeDebuggerPrint('''angularDimension.py:14  	        dimensioning.stage = 1 ''')
        dimensioning.stage = 1
    else: 
        crudeDebuggerPrint('''angularDimension.py:16  	        dimensioning.line2 = x1,y1,x2,y2 ''')
        dimensioning.line2 = x1,y1,x2,y2
        crudeDebuggerPrint('''angularDimension.py:17  	        dimensioning.stage = 2 ''')
        dimensioning.stage = 2
        crudeDebuggerPrint('''angularDimension.py:18  	        selectionOverlay.hideSelectionGraphicsItems() ''')
        selectionOverlay.hideSelectionGraphicsItems()
        crudeDebuggerPrint('''angularDimension.py:19  	        previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview ) ''')
        previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    crudeDebuggerPrint('''angularDimension.py:22  	    if dimensioning.stage == 2 : ''')
    if dimensioning.stage == 2 :
        crudeDebuggerPrint('''angularDimension.py:23  	        dimensioning.point3 = x, y ''')
        dimensioning.point3 = x, y
        crudeDebuggerPrint('''angularDimension.py:24  	        debugPrint(2, 'base-line point set to x=%3.1f y=%3.1f' % (x,y)) ''')
        debugPrint(2, 'base-line point set to x=%3.1f y=%3.1f' % (x,y))
        crudeDebuggerPrint('''angularDimension.py:25  	        dimensioning.stage = 3 ''')
        dimensioning.stage = 3
        crudeDebuggerPrint('''angularDimension.py:26  	        return None, None ''')
        return None, None
    else:
        crudeDebuggerPrint('''angularDimension.py:28  	        XML = angularDimensionSVG( dimensioning.line1, dimensioning.line2, ''')
        XML = angularDimensionSVG( dimensioning.line1, dimensioning.line2,
                                   dimensioning.point3[0], dimensioning.point3[1], 
                                   x, y)
        crudeDebuggerPrint('''angularDimension.py:31  	        return findUnusedObjectName('dim'), XML ''')
        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y ):
    crudeDebuggerPrint('''angularDimension.py:34  	    if dimensioning.stage == 2 : ''')
    if dimensioning.stage == 2 :
        crudeDebuggerPrint('''angularDimension.py:35  	        return angularDimensionSVG( dimensioning.line1, dimensioning.line2, x, y, **dimensioning.svg_preview_KWs) ''')
        return angularDimensionSVG( dimensioning.line1, dimensioning.line2, x, y, **dimensioning.svg_preview_KWs)
    else:
        crudeDebuggerPrint('''angularDimension.py:37  	        return angularDimensionSVG( dimensioning.line1, dimensioning.line2, ''')
        return angularDimensionSVG( dimensioning.line1, dimensioning.line2,
                                    dimensioning.point3[0], dimensioning.point3[1], 
                                    x, y, **dimensioning.svg_preview_KWs )

crudeDebuggerPrint('''angularDimension.py:41  	#selection variables for angular dimensioning ''')
#selection variables for angular dimensioning
crudeDebuggerPrint('''angularDimension.py:42  	maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) ) ''')
maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
crudeDebuggerPrint('''angularDimension.py:43  	maskPen.setWidth(2.0) ''')
maskPen.setWidth(2.0)
crudeDebuggerPrint('''angularDimension.py:44  	maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) ) ''')
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
crudeDebuggerPrint('''angularDimension.py:45  	maskHoverPen.setWidth(2.0) ''')
maskHoverPen.setWidth(2.0)

class angularDimension:
    def Activated(self):
        crudeDebuggerPrint('''angularDimension.py:49  	        V = getDrawingPageGUIVars() ''')
        V = getDrawingPageGUIVars()
        crudeDebuggerPrint('''angularDimension.py:50  	        dimensioning.activate(V) ''')
        dimensioning.activate(V)
        crudeDebuggerPrint('''angularDimension.py:51  	        selectionOverlay.generateSelectionGraphicsItems( ''')
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')], 
            selectFun ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doLines=True,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = QtGui.QBrush() #clear
            )
        
    def GetResources(self): 
        crudeDebuggerPrint('''angularDimension.py:63  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'angularDimension.svg' ) , 
            'MenuText': 'Angular Dimension', 
            'ToolTip': 'Creates a angular dimension'
            } 

crudeDebuggerPrint('''angularDimension.py:69  	FreeCADGui.addCommand('angularDimension', angularDimension()) ''')
FreeCADGui.addCommand('angularDimension', angularDimension())