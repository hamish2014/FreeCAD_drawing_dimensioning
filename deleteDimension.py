
from dimensioning import *
import selectionOverlay, previewDimension 

d = DimensioningProcessTracker()

def deleteDimension( event, referer, elementXML, elementParms, elementViewObject ):
    debugPrint(2, 'deleting dimension %s' % elementViewObject.Name)
    FreeCAD.ActiveDocument.openTransaction("Delete %s" % elementViewObject.Name)
    FreeCAD.ActiveDocument.removeObject( elementViewObject.Name )
    FreeCAD.ActiveDocument.commitTransaction()
    recomputeWithOutViewReset(d.drawingVars)
    FreeCADGui.Control.closeDialog()
    if d.endFunction <> None:
        previewDimension.preview.dimensioningProcessTracker = d
        previewDimension.timer.start( 1 )

class deleteAllButton:
    def deleteAllDimensions( self, arg1=None):
        try :
            FreeCAD.ActiveDocument.openTransaction("Delete All Dimensions")
            debugPrint(2,'Deleting all dimensioning objects')
            #FreeCAD.ActiveDocument.openTransaction("Delete All Dim. Objects")
            for obj in d.drawingVars.page.Group:
                if hasattr(obj,'Proxy') and isinstance(obj.Proxy, Proxy_DimensionObject_prototype):
                    FreeCAD.ActiveDocument.removeObject( obj.Name )
            FreeCAD.ActiveDocument.commitTransaction()
            #FreeCAD.ActiveDocument.commitTransaction()# ah undo not working ...
            recomputeWithOutViewReset(d.drawingVars)
            FreeCADGui.Control.closeDialog()
        except:
            errorMessagebox_with_traceback()
    def generateWidget( self, dimensioningProcess ):
        button = QtGui.QPushButton('Delete All')
        button.clicked.connect( self.deleteAllDimensions )
        return button
d.dialogWidgets.append( deleteAllButton() )
class UndoInfoText:
    def generateWidget( self, dimensioningProcess ):
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget( QtGui.QLabel('To undo a deletion:') )
        vbox.addWidget( QtGui.QLabel('  1) Undo') )
        vbox.addWidget( QtGui.QLabel('  2) Recompute Document') )
        return vbox
d.dialogWidgets.append( UndoInfoText() )


maskBrush  =   QtGui.QBrush( QtGui.QColor(160,0,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(160,0,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(255,0,0,255) )
maskHoverPen.setWidth(0.0)
    
class DeleteDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Delete Dimension', dialogIconPath=':/dd/icons/deleteDimension.svg' , endFunction=self.Activated, grid=False)
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if hasattr(obj,'Proxy') and isinstance(obj.Proxy, Proxy_DimensionObject_prototype)], 
            doSelectViewObjectPoints = True, 
            onClickFun=deleteDimension,
            sceneToAddTo = V.graphicsScene, 
            transform = V.transform,
            pointWid=1.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)
        
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/deleteDimension.svg', 
            'MenuText': 'Delete Dimension', 
            'ToolTip': 'Delete a dimension'
            } 

FreeCADGui.addCommand('dd_deleteDimension', DeleteDimension())
