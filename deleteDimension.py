
from dimensioning import *
from dimensioning import __dir__ # not imported with * directive
from drawingSelectionLib import generateSelectionGraphicsItems

dimensioning = DimensioningProcessTracker()

def deleteDimension( event, referer, elementXML, elementParms, elementViewObject ):
    debugPrint(2, 'deleting dimension %s' % elementViewObject.Name)
    App.ActiveDocument.removeObject( elementViewObject.Name )
    dimensioning.drawingVars.page.touch()
    App.ActiveDocument.recompute()


maskBrush  =   QtGui.QBrush( QtGui.QColor(160,0,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(160,0,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(255,0,0,255) )
maskHoverPen.setWidth(0.0)
    
class DeleteDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V)
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
        return {
            'Pixmap' : os.path.join( __dir__ , 'deleteDimension.svg' ) , 
            'MenuText': 'Delete Dimension', 
            'ToolTip': 'Delete a dimension'
            } 

FreeCADGui.addCommand('deleteDimension', DeleteDimension())
