'''
Dialog notes
Use Qt Designer to edit the addTextDialog.ui
Once completed $ pyside-uic addTextDialog.ui > addTextDialog.py

To test inside Freecad
from addTextDialog import DialogWidget
dialog = DialogWidget()
dialogUi = addTextDialog.Ui_Dialog()
dialogUi.setupUi(dialog)
dialog.show()

'''

from dimensioning import *
from dimensioning import __dir__ # not imported with * directive
import previewDimension
import addTextDialog

dimensioning = DimensioningProcessTracker()

def textSVG( x, y, svgTag='g', svgParms=''):
    XML = '''<%s  %s >
<text x="%f" y="%f" fill="%s" style="font-size:%i">%s</text>
</%s> ''' % ( svgTag, svgParms, x, y, dimensioning.color, dimensioning.fontSize, dimensioning.text, svgTag )
    debugPrint(4, 'textSVG.XML %s' % XML)
    return XML

def clickEvent( x, y):
    viewName = findUnusedObjectName('dimText')
    XML = textSVG(x,y)
    return viewName, XML

def hoverEvent( x, y):
    return textSVG( x, y, **dimensioning.svg_preview_KWs )

class AddTextDialogWidget( QtGui.QWidget ):
    def accept( self ):
        debugPrint(3, 'AddTextDialogWidget accept pressed')
        widgets = dict( [c.objectName(), c] for c in self.children() )
        debugPrint(4, 'widgets %s' % widgets)
        if widgets['textLineEdit'].text() == '':
            debugPrint(1, 'Aborting placing empty text.')
            return
        debugPrint(2, 'Placing "%s"' % widgets['textLineEdit'].text() )
        self.hide()
        dimensioning.text = widgets['textLineEdit'].text()
        widgets['textLineEdit'].setText('')
        dimensioning.fontSize =  widgets['textSizeSpinBox'].value()
        dimensioning.color = widgets['colorLineEdit'].text()
        debugPrint(4,'previewDimension.initializePreview')
        previewDimension.initializePreview(
            dimensioning.drawingVars,
            clickEvent, 
            hoverEvent )


dialog = AddTextDialogWidget()
dialogUi = addTextDialog.Ui_Dialog()
dialogUi.setupUi(dialog)

class AddText:
    def Activated(self):
        V = getDrawingPageGUIVars() #needs to be done before dialog show, else Qt active is dialog and not freecads
        dimensioning.activate( V )
        dialog.show()
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'addText.svg' ) , 
            'MenuText': 'Add text to drawing', 
            'ToolTip': 'Add text to drawing'
            } 
FreeCADGui.addCommand('addTextDimensioning', AddText())


