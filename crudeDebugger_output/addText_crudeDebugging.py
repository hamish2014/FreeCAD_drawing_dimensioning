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


crudeDebuggerPrint('''addText.py:15  	import os, FreeCADGui ''')
import os, FreeCADGui
crudeDebuggerPrint('''addText.py:16  	import FreeCAD as App ''')
import FreeCAD as App
crudeDebuggerPrint('''addText.py:17  	from PySide import QtGui, QtCore, QtSvg ''')
from PySide import QtGui, QtCore, QtSvg
crudeDebuggerPrint('''addText.py:18  	import addTextDialog ''')
import addTextDialog
crudeDebuggerPrint('''addText.py:19  	from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype ''')
from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype


class PlaceTextRect( DimensioningRectPrototype ):

    def activate(self, graphicsScene, graphicsView, page, width, height, text, textFontSize, textColor,
                 VRT_scale, VRT_ox, VRT_oy, textPreview, textSVGRenderer, **otherKWs):

        crudeDebuggerPrint('''addText.py:27  	        self.graphicsScene = graphicsScene ''')
        self.graphicsScene = graphicsScene
        crudeDebuggerPrint('''addText.py:28  	        self.graphicsView = graphicsView ''')
        self.graphicsView = graphicsView
        crudeDebuggerPrint('''addText.py:29  	        self.drawingPage = page ''')
        self.drawingPage = page
        crudeDebuggerPrint('''addText.py:30  	        self.drawingPageWidth = width ''')
        self.drawingPageWidth = width
        crudeDebuggerPrint('''addText.py:31  	        self.drawingPageHeight = height ''')
        self.drawingPageHeight = height
        crudeDebuggerPrint('''addText.py:32  	        self.textToPlace = text ''')
        self.textToPlace = text
        crudeDebuggerPrint('''addText.py:33  	        self.textFontSize = textFontSize ''')
        self.textFontSize = textFontSize
        crudeDebuggerPrint('''addText.py:34  	        self.textColor = textColor ''')
        self.textColor = textColor
        crudeDebuggerPrint('''addText.py:35  	        self.VRT_ox = VRT_ox ''')
        self.VRT_ox = VRT_ox
        crudeDebuggerPrint('''addText.py:36  	        self.VRT_oy = VRT_oy ''')
        self.VRT_oy = VRT_oy
        crudeDebuggerPrint('''addText.py:37  	        self.VRT_scale = VRT_scale ''')
        self.VRT_scale = VRT_scale
        crudeDebuggerPrint('''addText.py:38  	        self.textPreview = textPreview ''')
        self.textPreview = textPreview
        crudeDebuggerPrint('''addText.py:39  	        self.textSVGRenderer = textSVGRenderer ''')
        self.textSVGRenderer = textSVGRenderer

        crudeDebuggerPrint('''addText.py:41  	        self.svgHeaders='width="%(width)i" height="%(height)i" transform="translate( %(VRT_ox)f, %(VRT_oy)f) scale( %(VRT_scale)f, %(VRT_scale)f)"' % locals() ''')
        self.svgHeaders='width="%(width)i" height="%(height)i" transform="translate( %(VRT_ox)f, %(VRT_oy)f) scale( %(VRT_scale)f, %(VRT_scale)f)"' % locals()
        
        crudeDebuggerPrint('''addText.py:43  	        debugPrint(3, 'adding graphicsScene Objects for aiding to dimensioning to scene') ''')
        debugPrint(3, 'adding graphicsScene Objects for aiding to dimensioning to scene')
        crudeDebuggerPrint('''addText.py:44  	        graphicsScene.addItem( textPreview ) ''')
        graphicsScene.addItem( textPreview )
        crudeDebuggerPrint('''addText.py:45  	        self.cleanUpList = [ textPreview ] ''')
        self.cleanUpList = [ textPreview ]
        crudeDebuggerPrint('''addText.py:46  	        self.cleanedUp = False ''')
        self.cleanedUp = False

        crudeDebuggerPrint('''addText.py:48  	        self.setRect(0, 0, width, height) ''')
        self.setRect(0, 0, width, height)
        crudeDebuggerPrint('''addText.py:49  	        graphicsScene.addItem( self ) ''')
        graphicsScene.addItem( self )
        crudeDebuggerPrint('''addText.py:50  	        self.setAcceptHoverEvents(True) ''')
        self.setAcceptHoverEvents(True)
        crudeDebuggerPrint('''addText.py:51  	        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True ) ''')
        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
        crudeDebuggerPrint('''addText.py:52  	        debugPrint(3, 'PlaceTextRect.Activated') ''')
        debugPrint(3, 'PlaceTextRect.Activated')

    def textSVG(self, x, y, preview):
        crudeDebuggerPrint('''addText.py:55  	        svgTag = 'svg' if preview else 'g' ''')
        svgTag = 'svg' if preview else 'g'
        crudeDebuggerPrint('''addText.py:56  	        XML = ''' +"'''" +'''<%s  %s > ''')
        XML = '''<%s  %s >
<text x="%f" y="%f" fill="%s" style="font-size:%i">%s</text>
</%s> ''' % ( svgTag, self.svgHeaders if preview else '', x, y, self.textColor, self.textFontSize, self.textToPlace, svgTag )
        crudeDebuggerPrint('''addText.py:59  	        debugPrint(4, 'textSVG.XML %s' % XML) ''')
        debugPrint(4, 'textSVG.XML %s' % XML)
        crudeDebuggerPrint('''addText.py:60  	        return XML ''')
        return XML

    def hoverMoveEvent(self, event):
        crudeDebuggerPrint('''addText.py:63  	        pos = event.scenePos() ''')
        pos = event.scenePos()
        crudeDebuggerPrint('''addText.py:64  	        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale ''')
        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
        crudeDebuggerPrint('''addText.py:65  	        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale ''')
        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
        crudeDebuggerPrint('''addText.py:66  	        debugPrint(4, 'hoverMoveEvent: x %f, y %f'%(x,y)) ''')
        debugPrint(4, 'hoverMoveEvent: x %f, y %f'%(x,y))
        crudeDebuggerPrint('''addText.py:67  	        self.textSVGRenderer.load( QtCore.QByteArray( self.textSVG(x,y,True) ) ) ''')
        self.textSVGRenderer.load( QtCore.QByteArray( self.textSVG(x,y,True) ) )
        crudeDebuggerPrint('''addText.py:68  	        self.textPreview.update() ''')
        self.textPreview.update()
        crudeDebuggerPrint('''addText.py:69  	        self.textPreview.show() ''')
        self.textPreview.show()

    def mousePressEvent( self, event ):
        crudeDebuggerPrint('''addText.py:72  	        if event.button() == QtCore.Qt.MouseButton.LeftButton: ''')
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            crudeDebuggerPrint('''addText.py:73  	            pos = event.scenePos() ''')
            pos = event.scenePos()
            crudeDebuggerPrint('''addText.py:74  	            x = ( pos.x() - self.VRT_ox )/ self.VRT_scale ''')
            x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
            crudeDebuggerPrint('''addText.py:75  	            y = ( pos.y() - self.VRT_oy )/ self.VRT_scale ''')
            y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
            crudeDebuggerPrint('''addText.py:76  	            debugPrint(3, 'mousePressEvent: x %f, y %f' % (x, y)) ''')
            debugPrint(3, 'mousePressEvent: x %f, y %f' % (x, y))
            crudeDebuggerPrint('''addText.py:77  	            viewName = 'dimText001' ''')
            viewName = 'dimText001'
            crudeDebuggerPrint('''addText.py:78  	            XML = self.textSVG(x,y,False) ''')
            XML = self.textSVG(x,y,False)
            crudeDebuggerPrint('''addText.py:79  	            debugPrint(3, 'XML %s' % XML) ''')
            debugPrint(3, 'XML %s' % XML)
            crudeDebuggerPrint('''addText.py:80  	            while hasattr(App.ActiveDocument, viewName): ''')
            while hasattr(App.ActiveDocument, viewName):
                crudeDebuggerPrint('''addText.py:81  	                viewName = 'dimText%03i' % ( int(viewName[-3:]) + 1 ) ''')
                viewName = 'dimText%03i' % ( int(viewName[-3:]) + 1 )
            crudeDebuggerPrint('''addText.py:82  	            debugPrint(2, 'creating text %s' % viewName) ''')
            debugPrint(2, 'creating text %s' % viewName)
            crudeDebuggerPrint('''addText.py:83  	            App.ActiveDocument.addObject('Drawing::FeatureView',viewName) ''')
            App.ActiveDocument.addObject('Drawing::FeatureView',viewName)
            crudeDebuggerPrint('''addText.py:84  	            App.ActiveDocument.getObject(viewName).ViewResult = XML ''')
            App.ActiveDocument.getObject(viewName).ViewResult = XML                    
            crudeDebuggerPrint('''addText.py:85  	            self.drawingPage.addObject(App.ActiveDocument.getObject(viewName)) ''')
            self.drawingPage.addObject(App.ActiveDocument.getObject(viewName))
            crudeDebuggerPrint('''addText.py:86  	            self.cleanUp() ''')
            self.cleanUp()

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            crudeDebuggerPrint('''addText.py:89  	            self.cleanUp() ''')
            self.cleanUp()


crudeDebuggerPrint('''addText.py:92  	moduleGlobals = {} ''')
moduleGlobals = {}
class AddTextDialogWidget( QtGui.QWidget ):
    def accept( self ):
        crudeDebuggerPrint('''addText.py:95  	        debugPrint(3, 'AddTextDialogWidget accept pressed') ''')
        debugPrint(3, 'AddTextDialogWidget accept pressed')
        crudeDebuggerPrint('''addText.py:96  	        widgets = dict( [c.objectName(), c] for c in self.children() ) ''')
        widgets = dict( [c.objectName(), c] for c in self.children() )
        crudeDebuggerPrint('''addText.py:97  	        debugPrint(4, 'widgets %s' % widgets) ''')
        debugPrint(4, 'widgets %s' % widgets)
        crudeDebuggerPrint('''addText.py:98  	        if widgets['textLineEdit'].text() == '': ''')
        if widgets['textLineEdit'].text() == '':
            crudeDebuggerPrint('''addText.py:99  	            debugPrint(1, 'Aborting placing empty text.') ''')
            debugPrint(1, 'Aborting placing empty text.')
            crudeDebuggerPrint('''addText.py:100  	            return ''')
            return
        crudeDebuggerPrint('''addText.py:101  	        debugPrint(2, 'Placing "%s"' % widgets['textLineEdit'].text() ) ''')
        debugPrint(2, 'Placing "%s"' % widgets['textLineEdit'].text() )
        crudeDebuggerPrint('''addText.py:102  	        self.hide() ''')
        self.hide()
        crudeDebuggerPrint('''addText.py:103  	        moduleGlobals['text'] = widgets['textLineEdit'].text() ''')
        moduleGlobals['text'] = widgets['textLineEdit'].text()
        crudeDebuggerPrint('''addText.py:104  	        widgets['textLineEdit'].setText('') ''')
        widgets['textLineEdit'].setText('')
        crudeDebuggerPrint('''addText.py:105  	        moduleGlobals['textFontSize'] =  widgets['textSizeSpinBox'].value() ''')
        moduleGlobals['textFontSize'] =  widgets['textSizeSpinBox'].value()
        crudeDebuggerPrint('''addText.py:106  	        moduleGlobals['textColor'] = widgets['colorLineEdit'].text() ''')
        moduleGlobals['textColor'] = widgets['colorLineEdit'].text()
        crudeDebuggerPrint('''addText.py:107  	        if not moduleGlobals.has_key('placeTextRect') or not moduleGlobals['placeTextRect'].cleanedUp: ''')
        if not moduleGlobals.has_key('placeTextRect') or not moduleGlobals['placeTextRect'].cleanedUp: 
            crudeDebuggerPrint('''addText.py:108  	            # then initialize graphicsScene Objects, otherwise dont recreate objects. ''')
            # then initialize graphicsScene Objects, otherwise dont recreate objects. 
            crudeDebuggerPrint('''addText.py:109  	            # initializing dimPreview is particularly troublesome, as in FreeCAD 0.15 this is unstable and occasionally causes FreeCAD to crash. ''')
            # initializing dimPreview is particularly troublesome, as in FreeCAD 0.15 this is unstable and occasionally causes FreeCAD to crash.
            crudeDebuggerPrint('''addText.py:110  	            debugPrint(4, 'creating text placement preview') ''')
            debugPrint(4, 'creating text placement preview')
            crudeDebuggerPrint('''addText.py:111  	            textPreview = QtSvg.QGraphicsSvgItem() ''')
            textPreview = QtSvg.QGraphicsSvgItem()
            crudeDebuggerPrint('''addText.py:112  	            textSVGRenderer = QtSvg.QSvgRenderer() ''')
            textSVGRenderer = QtSvg.QSvgRenderer()
            crudeDebuggerPrint('''addText.py:113  	            textSVGRenderer.load( QtCore.QByteArray( ''' +"'''" +'''<svg width="%i" height="%i"> </svg>''' +"'''" +''' % (moduleGlobals['width'], moduleGlobals['height']) ) ) ''')
            textSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> </svg>''' % (moduleGlobals['width'], moduleGlobals['height']) ) )
            crudeDebuggerPrint('''addText.py:114  	            textPreview.setSharedRenderer( textSVGRenderer ) ''')
            textPreview.setSharedRenderer( textSVGRenderer )

            crudeDebuggerPrint('''addText.py:116  	            debugPrint(4, 'Adding CircularDimensioningRect to graphicsScene') ''')
            debugPrint(4, 'Adding CircularDimensioningRect to graphicsScene')
            crudeDebuggerPrint('''addText.py:117  	            placeTextRect = PlaceTextRect() ''')
            placeTextRect = PlaceTextRect()

            crudeDebuggerPrint('''addText.py:119  	            moduleGlobals.update(locals()) ''')
            moduleGlobals.update(locals())
            crudeDebuggerPrint('''addText.py:120  	            del moduleGlobals['self'] ''')
            del moduleGlobals['self']
            crudeDebuggerPrint('''addText.py:121  	            assert not moduleGlobals.has_key('moduleGlobals') ''')
            assert not moduleGlobals.has_key('moduleGlobals')
        crudeDebuggerPrint('''addText.py:122  	        debugPrint(4, '7') ''')
        debugPrint(4, '7')
        crudeDebuggerPrint('''addText.py:123  	        moduleGlobals['placeTextRect'].activate(**moduleGlobals) ''')
        moduleGlobals['placeTextRect'].activate(**moduleGlobals)


crudeDebuggerPrint('''addText.py:126  	dialog = AddTextDialogWidget() ''')
dialog = AddTextDialogWidget()
crudeDebuggerPrint('''addText.py:127  	dialogUi = addTextDialog.Ui_Dialog() ''')
dialogUi = addTextDialog.Ui_Dialog()
crudeDebuggerPrint('''addText.py:128  	dialogUi.setupUi(dialog) ''')
dialogUi.setupUi(dialog)

class AddText:
    def Activated(self):
        crudeDebuggerPrint('''addText.py:132  	        moduleGlobals.update(get_FreeCAD_drawing_variables()) #needs to be done before dialog show, else Qt active is dialog and not freecas ''')
        moduleGlobals.update(get_FreeCAD_drawing_variables()) #needs to be done before dialog show, else Qt active is dialog and not freecas
        crudeDebuggerPrint('''addText.py:133  	        dialog.show() ''')
        dialog.show()
        
    def GetResources(self): 
        crudeDebuggerPrint('''addText.py:136  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'addText.svg' ) , 
            'MenuText': 'Add text to drawing', 
            'ToolTip': 'Add text to drawing'
            } 
crudeDebuggerPrint('''addText.py:141  	FreeCADGui.addCommand('addTextDimensioning', AddText()) ''')
FreeCADGui.addCommand('addTextDimensioning', AddText())

