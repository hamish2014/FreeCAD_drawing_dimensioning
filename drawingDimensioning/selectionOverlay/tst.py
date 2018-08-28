assert __name__ == "__main__"
import sys
if len(sys.argv) == 2:
    print('Testing selectionOverlay.py')
    XML = open(sys.argv[1]).read()
else:
    print('usage\n\tpython selectionOverlay.py svg_file')
    exit(2)
    #XML = testCase9
import tst_setup
from PySide import QtGui, QtSvg, QtCore
    
app = QtGui.QApplication([])
#need to be defined before drawingDimensioning , else Qt crashes
from drawingDimensioning.selectionOverlay import  generateSelectionGraphicsItems


width = 1200
height = 1200 / 16.0 * 9

graphicsScene = QtGui.QGraphicsScene()#0,0,width,height)
#graphicsScene.addText("Svg_Tools.py test")
orthoViews = []
def addOrthoView( XML ):
    o1 = QtSvg.QGraphicsSvgItem()
    o1Renderer = QtSvg.QSvgRenderer()
    o1Renderer.load( QtCore.QByteArray( XML ))
    o1.setSharedRenderer( o1Renderer )
    graphicsScene.addItem( o1 )
    orthoViews.append([o1, o1Renderer, XML]) #protect o1 and o1Renderer against garbage collector
addOrthoView(XML)


class dummyViewObject:
    def __init__(self, XML):
        self.ViewResult = XML
        self.Name = 'dummyViewObject'
        self.X = 0
        self.Y = 0
        
viewObject = dummyViewObject( XML )

def onClickFun( event, referer, elementXML, elementParms, elementViewObject ):
    print( elementXML  )
    print( elementParms )
    referer.adjustScale( 2 )


maskBrush = QtGui.QBrush( QtGui.QColor(0,255,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
maskPen.setWidth(4)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidthF(5)
generateSelectionGraphicsItems( 
    [viewObject], onClickFun, sceneToAddTo=graphicsScene, doPoints=True, doCircles=True, doTextItems=True, doLines=True, doFittedCircles=True, doEllipses=True,
    maskPen=maskPen , maskBrush=maskBrush, maskHoverPen=maskHoverPen, pointWid=4.0
)

view = QtGui.QGraphicsView(graphicsScene)
view.setGeometry(0, 0, height-30, height-30)
#view.show()
class ViewHoldingWidget(QtGui.QWidget):
    def __init__(self):
        super(ViewHoldingWidget, self).__init__()
        self.initUI()
        
    def initUI(self):
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget( view )
        self.setLayout(vbox)   
        self.setGeometry(0, 0, width+30, height+30)
        
ex = ViewHoldingWidget()
    #view.fitInView( graphicsScene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
    #noTransform = QtGui.QTransform(1, 0, 0, 1, 0.0, 0.0)
    #view.setTransform( noTransform )

ex.show()
sys.exit(app.exec_())



