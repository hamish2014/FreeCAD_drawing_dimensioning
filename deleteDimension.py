
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay 

dimensioning = DimensioningProcessTracker()

def deleteDimension( event, referer, elementXML, elementParms, elementViewObject ):
    debugPrint(2, 'deleting dimension %s' % elementViewObject.Name)
    App.ActiveDocument.removeObject( elementViewObject.Name )
    recomputeWithOutViewReset(dimensioning.drawingVars)


maskBrush  =   QtGui.QBrush( QtGui.QColor(160,0,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(160,0,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(255,0,0,255) )
maskHoverPen.setWidth(0.0)
    
class DeleteDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V)
        commonArgs = dict( 
            onClickFun=deleteDimension,
            sceneToAddTo = V.graphicsScene, 
            transform = V.transform,
            pointWid=1.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if obj.Name.startswith('dim')], 
            doSelectViewObjectPoints = True, 
            **commonArgs)
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if obj.Name.startswith('center')], 
            clearPreviousSelectionItems = False,
            doSelectViewObjectPoints=True, 
            **commonArgs)
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'deleteDimension.svg' ) , 
            'MenuText': 'Delete Dimension', 
            'ToolTip': 'Delete a dimension'
            } 

FreeCADGui.addCommand('deleteDimension', DeleteDimension())
