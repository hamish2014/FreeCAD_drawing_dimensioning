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
import previewDimension
import textAddDialog

d = DimensioningProcessTracker()
d.assignedPrefenceValues = False

def textSVG( x, y):
    return '<g> %s </g>' % d.textRenderer(x,y,d.text,rotation=d.rotation)

def clickEvent( x, y):
    return 'createDimension:%s' % findUnusedObjectName('dimText')

class AddTextDialogWidget( QtGui.QWidget ):
    def accept( self ):
        debugPrint(2, 'AddTextDialogWidget accept pressed')
        widgets = dict( [c.objectName(), c] for c in self.children() )
        debugPrint(2, 'widgets %s' % widgets)
        if widgets['textLineEdit'].text() == '':
            debugPrint(1, 'Aborting placing empty text.')
            return
        debugPrint(2, 'Placing "%s"' % widgets['textLineEdit'].text() )
        self.hide()
        d.text = widgets['textLineEdit'].text()
        widgets['textLineEdit'].setText('')
        family = widgets['familyLineEdit'].text()
        size = widgets['sizeLineEdit'].text()
        fill = widgets['colorLineEdit'].text()
        d.textRenderer = SvgTextRenderer( family, size, fill )
        d.rotation = widgets['doubleSpinBox_rotation'].value()
        debugPrint(3,'textRenderer created')
        debugPrint(3,'previewDimension.initializePreview')
        previewDimension.initializePreview(
            d.drawingVars,
            textSVG, 
            clickEvent )


dialog = AddTextDialogWidget()
dialogUi = textAddDialog.Ui_Dialog()
dialogUi.setupUi(dialog)

class AddText:
    def Activated(self):
        V = getDrawingPageGUIVars() #needs to be done before dialog show, else active window is dialog and not freecad
        d.activate( V, textParms=['textRenderer'] )
        if not d.assignedPrefenceValues:
            tR = d.dimensionConstructorKWs['textRenderer']
            widgets = dict( [c.objectName(), c] for c in dialog.children() )
            widgets['sizeLineEdit'].setText( tR.font_size )
            widgets['colorLineEdit'].setText(  tR.fill )
            widgets['familyLineEdit'].setText( tR.font_family )
            d.assignedPrefenceValues = True
        dialog.show()
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'textAdd.svg' ) , 
            'MenuText': 'Add text to drawing', 
            'ToolTip': 'Add text to drawing'
            } 
FreeCADGui.addCommand('dd_addText', AddText())


