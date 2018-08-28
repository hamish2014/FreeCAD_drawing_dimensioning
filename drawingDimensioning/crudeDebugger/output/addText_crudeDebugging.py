from crudeDebugger import crudeDebuggerPrint
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

crudeDebuggerPrint('''addText.py:14  	from dimensioning import * ''')
from dimensioning import *
crudeDebuggerPrint('''addText.py:15  	from dimensioning import __dir__ # not imported with * directive ''')
from dimensioning import __dir__ # not imported with * directive
crudeDebuggerPrint('''addText.py:16  	import previewDimension ''')
import previewDimension
crudeDebuggerPrint('''addText.py:17  	import addTextDialog ''')
import addTextDialog

crudeDebuggerPrint('''addText.py:19  	dimensioning = DimensioningProcessTracker() ''')
dimensioning = DimensioningProcessTracker()

def textSVG( x, y, svgTag='g', svgParms=''):
    crudeDebuggerPrint('''addText.py:22  	    XML = ''' +"'''" +'''<%s  %s > ''')
    XML = '''<%s  %s >
<text x="%f" y="%f" fill="%s" style="font-size:%i">%s</text>
</%s> ''' % ( svgTag, svgParms, x, y, dimensioning.color, dimensioning.fontSize, dimensioning.text, svgTag )
    crudeDebuggerPrint('''addText.py:25  	    debugPrint(4, 'textSVG.XML %s' % XML) ''')
    debugPrint(4, 'textSVG.XML %s' % XML)
    crudeDebuggerPrint('''addText.py:26  	    return XML ''')
    return XML

def clickEvent( x, y):
    crudeDebuggerPrint('''addText.py:29  	    viewName = findUnusedObjectName('dimText') ''')
    viewName = findUnusedObjectName('dimText')
    crudeDebuggerPrint('''addText.py:30  	    XML = textSVG(x,y) ''')
    XML = textSVG(x,y)
    crudeDebuggerPrint('''addText.py:31  	    return viewName, XML ''')
    return viewName, XML

def hoverEvent( x, y):
    crudeDebuggerPrint('''addText.py:34  	    return textSVG( x, y, **dimensioning.svg_preview_KWs ) ''')
    return textSVG( x, y, **dimensioning.svg_preview_KWs )

class AddTextDialogWidget( QtGui.QWidget ):
    def accept( self ):
        crudeDebuggerPrint('''addText.py:38  	        debugPrint(3, 'AddTextDialogWidget accept pressed') ''')
        debugPrint(3, 'AddTextDialogWidget accept pressed')
        crudeDebuggerPrint('''addText.py:39  	        widgets = dict( [c.objectName(), c] for c in self.children() ) ''')
        widgets = dict( [c.objectName(), c] for c in self.children() )
        crudeDebuggerPrint('''addText.py:40  	        debugPrint(4, 'widgets %s' % widgets) ''')
        debugPrint(4, 'widgets %s' % widgets)
        crudeDebuggerPrint('''addText.py:41  	        if widgets['textLineEdit'].text() == '': ''')
        if widgets['textLineEdit'].text() == '':
            crudeDebuggerPrint('''addText.py:42  	            debugPrint(1, 'Aborting placing empty text.') ''')
            debugPrint(1, 'Aborting placing empty text.')
            crudeDebuggerPrint('''addText.py:43  	            return ''')
            return
        crudeDebuggerPrint('''addText.py:44  	        debugPrint(2, 'Placing "%s"' % widgets['textLineEdit'].text() ) ''')
        debugPrint(2, 'Placing "%s"' % widgets['textLineEdit'].text() )
        crudeDebuggerPrint('''addText.py:45  	        self.hide() ''')
        self.hide()
        crudeDebuggerPrint('''addText.py:46  	        dimensioning.text = widgets['textLineEdit'].text() ''')
        dimensioning.text = widgets['textLineEdit'].text()
        crudeDebuggerPrint('''addText.py:47  	        widgets['textLineEdit'].setText('') ''')
        widgets['textLineEdit'].setText('')
        crudeDebuggerPrint('''addText.py:48  	        dimensioning.fontSize =  widgets['textSizeSpinBox'].value() ''')
        dimensioning.fontSize =  widgets['textSizeSpinBox'].value()
        crudeDebuggerPrint('''addText.py:49  	        dimensioning.color = widgets['colorLineEdit'].text() ''')
        dimensioning.color = widgets['colorLineEdit'].text()
        crudeDebuggerPrint('''addText.py:50  	        debugPrint(4,'previewDimension.initializePreview') ''')
        debugPrint(4,'previewDimension.initializePreview')
        crudeDebuggerPrint('''addText.py:51  	        previewDimension.initializePreview( ''')
        previewDimension.initializePreview(
            dimensioning.drawingVars,
            clickEvent, 
            hoverEvent )


crudeDebuggerPrint('''addText.py:57  	dialog = AddTextDialogWidget() ''')
dialog = AddTextDialogWidget()
crudeDebuggerPrint('''addText.py:58  	dialogUi = addTextDialog.Ui_Dialog() ''')
dialogUi = addTextDialog.Ui_Dialog()
crudeDebuggerPrint('''addText.py:59  	dialogUi.setupUi(dialog) ''')
dialogUi.setupUi(dialog)

class AddText:
    def Activated(self):
        crudeDebuggerPrint('''addText.py:63  	        V = getDrawingPageGUIVars() #needs to be done before dialog show, else Qt active is dialog and not freecads ''')
        V = getDrawingPageGUIVars() #needs to be done before dialog show, else Qt active is dialog and not freecads
        crudeDebuggerPrint('''addText.py:64  	        dimensioning.activate( V ) ''')
        dimensioning.activate( V )
        crudeDebuggerPrint('''addText.py:65  	        dialog.show() ''')
        dialog.show()
        
    def GetResources(self): 
        crudeDebuggerPrint('''addText.py:68  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'addText.svg' ) , 
            'MenuText': 'Add text to drawing', 
            'ToolTip': 'Add text to drawing'
            } 
crudeDebuggerPrint('''addText.py:73  	FreeCADGui.addCommand('addTextDimensioning', AddText()) ''')
FreeCADGui.addCommand('addTextDimensioning', AddText())

