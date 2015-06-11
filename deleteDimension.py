
from dimensioning import *
import selectionOverlay, previewDimension 

d = DimensioningProcessTracker()

def deleteDimension( event, referer, elementXML, elementParms, elementViewObject ):
    debugPrint(2, 'deleting dimension %s' % elementViewObject.Name)
    App.ActiveDocument.removeObject( elementViewObject.Name )
    recomputeWithOutViewReset(d.drawingVars)
    FreeCADGui.Control.closeDialog()
    if d.endFunction <> None:
        previewDimension.preview.dimensioningProcessTracker = d
        previewDimension.timer.start( 1 )

class deleteAllButton:
    def deleteAllDimensions( self, arg1=None):
        try :
            reply = QtGui.QMessageBox.question(
                QtGui.qApp.activeWindow(), "Confirm Delete All",
                "Delete all dimension objects?\n(this action can not be undone)", 
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                debugPrint(2,'Deleting all dimensioning objects')
                #FreeCAD.ActiveDocument.openTransaction("Delete All Dim. Objects")
                for obj in d.drawingVars.page.Group:
                    if any( obj.Name.startswith(prefix) for prefix in ['dim','grabPoint','center','unfold']):
                        App.ActiveDocument.removeObject( obj.Name )
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

maskBrush  =   QtGui.QBrush( QtGui.QColor(160,0,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(160,0,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(255,0,0,255) )
maskHoverPen.setWidth(0.0)
    
class DeleteDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Delete Dimension', dialogIconPath=os.path.join( iconPath , 'deleteDimension.svg' ), endFunction=self.Activated)
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
            [obj for obj in V.page.Group  if obj.Name.startswith('dim') or obj.Name.startswith('grabPoint')], 
            doSelectViewObjectPoints = True, 
            **commonArgs)
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if obj.Name.startswith('center') or  obj.Name.startswith('unfold')], 
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

FreeCADGui.addCommand('dd_deleteDimension', DeleteDimension())
