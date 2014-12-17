'''
Dialog notes
Use Qt Designer to edit the textAddDialog.ui
Once completed $ pyside-uic textAddDialog.ui > textAddDialog.py

To test inside Freecad
from addTextDialog import DialogWidget
dialog = DialogWidget()
dialogUi = addTextDialog.Ui_Dialog()
dialogUi.setupUi(dialog)
dialog.show()

'''

from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay 
import textAddDialog
import XMLlib

dimensioning = DimensioningProcessTracker()

def EditDimensionText( event, referer, elementXML, elementParms, elementViewObject ):
    dimensioning.dimToEdit = elementViewObject    
    dimensioning.elementXML = elementXML
    selectionOverlay.hideSelectionGraphicsItems()
    e = elementXML
    xml = e.XML[e.pStart:e.pEnd]
    text = xml[xml.find('>')+1:-len('</text>')]
    widgets = dict( [c.objectName(), c] for c in dialog.children() )
    widgets['textLineEdit'].setText( text )
    widgets['textSizeSpinBox'].setValue( float( e.parms['style'][len('font-size:'):] ) )
    widgets['colorLineEdit'].setText( e.parms['fill'] )
    widgets['placeButton'].setText('Change')
    dialog.setWindowTitle('Editing %s' % elementViewObject.Name)
    dialog.show()
    
class EditTextDialogWidget( QtGui.QWidget ):
    def accept( self ):
        debugPrint(3, 'EditTextDialogWidget accept pressed')
        widgets = dict( [c.objectName(), c] for c in self.children() )
        debugPrint(4, 'widgets %s' % widgets)
        if widgets['textLineEdit'].text() == '':
            debugPrint(1, 'Aborting placing empty text.')
            return
        self.hide()
        newText = widgets['textLineEdit'].text()
        widgets['textLineEdit'].setText('')
        newSize = widgets['textSizeSpinBox'].value()
        newColor = widgets['colorLineEdit'].text()
        debugPrint(3,'updating %s.ViewResult to' % dimensioning.dimToEdit.Name)
        e = dimensioning.elementXML
        xml = e.XML[e.pStart:e.pEnd]
        xml = XMLlib.replaceParm(xml, 'style', 'font-size:%i' % newSize )
        xml = XMLlib.replaceParm(xml, 'fill', newColor )
        p1 = xml.find('>')+1
        p2 = xml.find('</text>')
        xml = xml[:p1] + newText + xml[p2:]
        debugPrint(4,xml)
        newXML = e.XML[:e.pStart] + xml + e.XML[e.pEnd:]
        debugPrint(3,newXML)
        dimensioning.dimToEdit.ViewResult = newXML
        recomputeWithOutViewReset(dimensioning.drawingVars)
        

dialog = EditTextDialogWidget()
dialogUi = textAddDialog.Ui_Dialog()
dialogUi.setupUi(dialog)

maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)

class EditText:
    def Activated(self):
        V = getDrawingPageGUIVars() #needs to be done before dialog show, else Qt active is dialog and not freecads
        dimensioning.activate( V )
        selectGraphicsItems = selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if obj.Name.startswith('dim')], 
            EditDimensionText , 
            sceneToAddTo = V.graphicsScene, 
            transform = V.transform,
            doTextItems = True, 
            pointWid=2.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        
    def GetResources(self): 
        msg = "Edit a dimension's text"
        return {
            'Pixmap' : os.path.join( iconPath , 'textEdit.svg' ) , 
            'MenuText': msg, 
            'ToolTip': msg
            } 
FreeCADGui.addCommand('textEditDimensioning', EditText())


