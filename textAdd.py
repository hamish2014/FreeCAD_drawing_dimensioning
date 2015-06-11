# This Python file uses the following encoding: utf-8
from dimensioning import *
import previewDimension
from dimensionSvgConstructor import *

d = DimensioningProcessTracker()

def textSVG( x, y, text='text', rotation=0.0, textRenderer_addText= defaultTextRenderer):
    return '<g> %s </g>' % textRenderer_addText(x,y,text,rotation=rotation)

d.registerPreference( 'textRenderer_addText', ['inherit','5', 0], 'text properties (AddText)', kind='font' )

class text_widget:
    def valueChanged( self, arg1):
        d.text = arg1
    def generateWidget( self, dimensioningProcess ):
        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setText('text')
        d.text = 'text'
        self.lineEdit.textChanged.connect(self.valueChanged)
        return self.lineEdit
d.dialogWidgets.append( text_widget() )
class rotation_widget:
    def valueChanged( self, arg1):
        d.rotation = arg1
    def generateWidget( self, dimensioningProcess ):
        self.spinbox = QtGui.QDoubleSpinBox()
        self.spinbox.setValue(0)
        d.rotation = 0
        self.spinbox.setMinimum( -180 )
        self.spinbox.setMaximum(  180 )
        self.spinbox.setDecimals( 1 )
        self.spinbox.setSingleStep( 5 )
        self.spinbox.setSuffix(unicode('°','utf8'))
        self.spinbox.valueChanged.connect(self.valueChanged)
        return  DimensioningTaskDialog_generate_row_hbox('rotation', self.spinbox)
d.dialogWidgets.append( rotation_widget() )


def addText_preview(mouseX, mouseY):
    return textSVG(mouseX, mouseY, d.text, d.rotation, **d.dimensionConstructorKWs )

def addText_clickHandler( x, y ):
    return 'createDimension:%s' % findUnusedObjectName('dimText')

class AddText:
    def Activated(self):
        V = getDrawingPageGUIVars() 
        d.activate( V,  dialogTitle='Add Text', dialogIconPath=os.path.join( iconPath , 'textAdd.svg' ), endFunction=self.Activated )
        previewDimension.initializePreview( d, addText_preview, addText_clickHandler)
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'textAdd.svg' ) , 
            'MenuText': 'Add text to drawing', 
            'ToolTip': 'Add text to drawing'
            } 
FreeCADGui.addCommand('dd_addText', AddText())


