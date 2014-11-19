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


import os, FreeCADGui
import FreeCAD as App
from PySide import QtGui, QtCore, QtSvg
import addTextDialog
from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype


class PlaceTextRect( DimensioningRectPrototype ):

    def activate(self, graphicsScene, graphicsView, page, width, height, text, textFontSize, textColor,
                 VRT_scale, VRT_ox, VRT_oy, textPreview, textSVGRenderer, **otherKWs):

        self.graphicsScene = graphicsScene
        self.graphicsView = graphicsView
        self.drawingPage = page
        self.drawingPageWidth = width
        self.drawingPageHeight = height
        self.textToPlace = text
        self.textFontSize = textFontSize
        self.textColor = textColor
        self.VRT_ox = VRT_ox
        self.VRT_oy = VRT_oy
        self.VRT_scale = VRT_scale
        self.textPreview = textPreview
        self.textSVGRenderer = textSVGRenderer

        self.svgHeaders='width="%(width)i" height="%(height)i" transform="translate( %(VRT_ox)f, %(VRT_oy)f) scale( %(VRT_scale)f, %(VRT_scale)f)"' % locals()
        
        debugPrint(3, 'adding graphicsScene Objects for aiding to dimensioning to scene')
        graphicsScene.addItem( textPreview )
        self.cleanUpList = [ textPreview ]
        self.cleanedUp = False

        self.setRect(0, 0, width, height)
        graphicsScene.addItem( self )
        self.setAcceptHoverEvents(True)
        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
        debugPrint(3, 'PlaceTextRect.Activated')

    def textSVG(self, x, y, preview):
        svgTag = 'svg' if preview else 'g'
        XML = '''<%s  %s >
<text x="%f" y="%f" fill="%s" style="font-size:%i">%s</text>
</%s> ''' % ( svgTag, self.svgHeaders if preview else '', x, y, self.textColor, self.textFontSize, self.textToPlace, svgTag )
        debugPrint(4, 'textSVG.XML %s' % XML)
        return XML

    def hoverMoveEvent(self, event):
        pos = event.scenePos()
        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
        debugPrint(4, 'hoverMoveEvent: x %f, y %f'%(x,y))
        self.textSVGRenderer.load( QtCore.QByteArray( self.textSVG(x,y,True) ) )
        self.textPreview.update()
        self.textPreview.show()

    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
            y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
            debugPrint(3, 'mousePressEvent: x %f, y %f' % (x, y))
            viewName = 'dimText001'
            XML = self.textSVG(x,y,False)
            debugPrint(3, 'XML %s' % XML)
            while hasattr(App.ActiveDocument, viewName):
                viewName = 'dimText%03i' % ( int(viewName[-3:]) + 1 )
            debugPrint(2, 'creating text %s' % viewName)
            App.ActiveDocument.addObject('Drawing::FeatureView',viewName)
            App.ActiveDocument.getObject(viewName).ViewResult = XML                    
            self.drawingPage.addObject(App.ActiveDocument.getObject(viewName))
            self.cleanUp()

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.cleanUp()


moduleGlobals = {}
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
        moduleGlobals['text'] = widgets['textLineEdit'].text()
        widgets['textLineEdit'].setText('')
        moduleGlobals['textFontSize'] =  widgets['textSizeSpinBox'].value()
        moduleGlobals['textColor'] = widgets['colorLineEdit'].text()
        if not moduleGlobals.has_key('placeTextRect') or not moduleGlobals['placeTextRect'].cleanedUp: 
            # then initialize graphicsScene Objects, otherwise dont recreate objects. 
            # initializing dimPreview is particularly troublesome, as in FreeCAD 0.15 this is unstable and occasionally causes FreeCAD to crash.
            debugPrint(4, 'creating text placement preview')
            textPreview = QtSvg.QGraphicsSvgItem()
            textSVGRenderer = QtSvg.QSvgRenderer()
            textSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> </svg>''' % (moduleGlobals['width'], moduleGlobals['height']) ) )
            textPreview.setSharedRenderer( textSVGRenderer )

            debugPrint(4, 'Adding CircularDimensioningRect to graphicsScene')
            placeTextRect = PlaceTextRect()

            moduleGlobals.update(locals())
            del moduleGlobals['self']
            assert not moduleGlobals.has_key('moduleGlobals')
        debugPrint(4, '7')
        moduleGlobals['placeTextRect'].activate(**moduleGlobals)


dialog = AddTextDialogWidget()
dialogUi = addTextDialog.Ui_Dialog()
dialogUi.setupUi(dialog)

class AddText:
    def Activated(self):
        moduleGlobals.update(get_FreeCAD_drawing_variables()) #needs to be done before dialog show, else Qt active is dialog and not freecas
        dialog.show()
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'addText.svg' ) , 
            'MenuText': 'Add text to drawing', 
            'ToolTip': 'Add text to drawing'
            } 
FreeCADGui.addCommand('addTextDimensioning', AddText())


