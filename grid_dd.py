import FreeCAD, traceback
from PySide import QtGui, QtCore, QtSvg

#code duplicated from dimensioning .py
def DimensioningTaskDialog_generate_row_hbox( label, inputWidget ):
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget( QtGui.QLabel(label) )
    hbox.addStretch(1)
    if inputWidget <> None:
        hbox.addWidget(inputWidget)
    return hbox

class ClickRect(QtGui.QGraphicsRectItem):
    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clickFun()
def RGBtoUnsigned( r,g,b ):
    return (r << 24) + (g << 16) + (b << 8) 

def unsignedToRGB( v ):
    r = v >> 24
    g = (v >> 16) - (v >> 24 << 8 )
    b = (v >>  8) - (v >> 16 << 8 )
    return r, g, b 

def unsignedToRGBText(v):
    return 'rgb(%i,%i,%i)' % unsignedToRGB(v)

#/end of duplicated code
default_grid_clr = RGBtoUnsigned(170,170,255)
default_grid_spacing = 1
default_grid_display_period = 20
default_grid_line_width = 0.15


def unsignedToRGBText(v):
    return 'rgb(%i,%i,%i)' % unsignedToRGB(v)

class GridOptionsGroupBox:
    def __init__(self):
        self.dd_parms = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Drawing_Dimensioning")

    def groupBoxToggled( self, checked):
        self.dd_parms.SetBool("show_grid_options", checked)
        self.groupbox.setMaximumHeight(1000 if checked else 18)

    def gridOn_checkbox_stateChanged( self, arg1=None):
        self.dd_parms.SetBool( 'grid_on', self.gridOn_checkbox.isChecked())
        dimensioningGrid.update()
    def spacingSpinbox_valueChanged( self, newValue ):
        self.dd_parms.SetFloat( 'grid_spacing',  newValue )
        dimensioningGrid.update()
    def displayPeriodSpinbox_valueChanged(self, newValue ):
        self.dd_parms.SetInt( 'grid_display_period',  newValue )
        dimensioningGrid.update()
    def lineWidthSpinbox_valueChanged(self, newValue ):
        self.dd_parms.SetFloat( 'grid_line_width',  newValue )
        dimensioningGrid.update()
    def specifyNewGridColor(self):
        color = QtGui.QColorDialog.getColor( self.colorRect.brush().color() )
        if color.isValid():
            self.colorRect.setBrush( QtGui.QBrush(color) )
            self.dd_parms.SetUnsigned( 'grid_color', RGBtoUnsigned(color.red(), color.green(), color.blue()) )
            dimensioningGrid.update()

    def generateWidget(self, dimensioningProcess):
        self.dimensioningProcess = dimensioningProcess
        groupbox = QtGui.QGroupBox("Grid Options")
        groupbox.setCheckable( True ) 
        groupbox.toggled.connect( self.groupBoxToggled )
        self.groupbox = groupbox
        checked = self.dd_parms.GetBool("show_grid_options",True)
        groupbox.setChecked(checked)
        vbox = QtGui.QVBoxLayout()

        gridOn_checkbox = QtGui.QCheckBox('grid on')
        gridOn_checkbox.setChecked( self.dd_parms.GetBool( 'grid_on', False ))
        gridOn_checkbox.stateChanged.connect( self.gridOn_checkbox_stateChanged )
        vbox.addWidget( gridOn_checkbox )
        self.gridOn_checkbox =  gridOn_checkbox

        spacingSpinbox = QtGui.QDoubleSpinBox()
        spacingSpinbox.setValue( self.dd_parms.GetFloat( 'grid_spacing', default_grid_spacing )  )
        spacingSpinbox.setMinimum( 0.01 )
        spacingSpinbox.setDecimals( 2 )
        spacingSpinbox.setSingleStep( 0.5 )
        spacingSpinbox.setSuffix('mm')
        spacingSpinbox.valueChanged.connect( self.spacingSpinbox_valueChanged )
        vbox.addLayout( DimensioningTaskDialog_generate_row_hbox('spacing', spacingSpinbox) )
        self.spacingSpinbox = spacingSpinbox

        displayPeriodSpinbox = QtGui.QSpinBox()
        displayPeriodSpinbox.setValue( self.dd_parms.GetInt( 'grid_display_period', default_grid_display_period  )  )
        displayPeriodSpinbox.setMinimum( 0 )
        displayPeriodSpinbox.valueChanged.connect( self.displayPeriodSpinbox_valueChanged )
        vbox.addLayout( DimensioningTaskDialog_generate_row_hbox('display period', displayPeriodSpinbox) )
        self.displayPeriodSpinbox = displayPeriodSpinbox

        clr = QtGui.QColor(*unsignedToRGB(self.dd_parms.GetUnsigned( 'grid_color', default_grid_clr )) )
        graphicsScene = QtGui.QGraphicsScene(0,0,30,30)
        pen = QtGui.QPen( QtGui.QColor(0,0,0,0) )
        pen.setWidth(0.0)
        rect = ClickRect(-100, -100, 200, 200)
        rect.setPen(pen)
        rect.clickFun = self.specifyNewGridColor
        graphicsScene.addItem(rect) 
        self.graphicsScene = graphicsScene #protect from garbage collector
        self.colorRect = rect
        self.colorRect.setBrush( QtGui.QBrush( clr ) )
        colorBox = QtGui.QGraphicsView( self.graphicsScene )
        colorBox.setMaximumWidth( 60 )
        colorBox.setMaximumHeight( 30 )
        colorBox.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff )
        colorBox.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff )
        vbox.addLayout(  DimensioningTaskDialog_generate_row_hbox( 'color', colorBox ) )

        lineWidthSpinbox = QtGui.QDoubleSpinBox()
        lineWidthSpinbox.setValue( self.dd_parms.GetFloat( 'grid_line_width', default_grid_line_width )  )
        lineWidthSpinbox.setMinimum( 0. )
        lineWidthSpinbox.setDecimals( 2 )
        lineWidthSpinbox.setSingleStep( 0.05 )
        lineWidthSpinbox.valueChanged.connect( self.lineWidthSpinbox_valueChanged )
        vbox.addLayout( DimensioningTaskDialog_generate_row_hbox('lineWidth', lineWidthSpinbox) )
        self.lineWidthSpinbox = lineWidthSpinbox
        groupbox.setLayout(vbox)
        return groupbox
gridOptionsGroupBox = GridOptionsGroupBox()


class GridManager:
    gridWidget = None
    def initialize(self, drawingVars):
        self.drawingVars = drawingVars
        self.update()
    def update(self):
        try:
            if hasattr( self, 'SVG'):
                self.remove()
            drawingVars  = self.drawingVars 
            parms = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Drawing_Dimensioning")
            div_period = parms.GetInt( 'grid_display_period',default_grid_display_period   )
            lineWidth = parms.GetFloat( 'grid_line_width', default_grid_line_width ) 
            if parms.GetBool('grid_on', False) and  div_period > 0 and lineWidth > 0: 
                self.SVG =  QtSvg.QGraphicsSvgItem() 
                self.SVGRenderer = QtSvg.QSvgRenderer()
                dArg =''
                div = parms.GetFloat( 'grid_spacing', default_grid_spacing )
                clr = unsignedToRGBText(parms.GetUnsigned( 'grid_color', default_grid_clr ))
                W = drawingVars.width / drawingVars.VRT_scale
                H = drawingVars.height / drawingVars.VRT_scale
                for i in range(1, int(W / (div*div_period) )+1):
                    dArg = dArg + ' M %f 0 L %f %f' % (i*div*div_period, i*div*div_period, H)
                for i in range(1, int(H / (div*div_period) )+1):
                    dArg = dArg + ' M 0 %f L %f %f' % (i*div*div_period, W, i*div*div_period)
                self.SVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> <path stroke="%srgb(0, 255, 0)" stroke-width="%f" d="%s"/> </svg>''' % (drawingVars.width, drawingVars.height, clr, lineWidth, dArg) ) )
                self.SVG.setSharedRenderer( self.SVGRenderer )
                self.SVG.setTransform( drawingVars.transform )
                self.SVG.setZValue( 0.08 ) #ensure behind dimension preview SVG ...
                drawingVars.graphicsScene.addItem( self.SVG )
                #FreeCAD.Console.PrintMessage('Grid Svg Added to Scene\n')
        except:
            FreeCAD.Console.PrintError(traceback.format_exc())
    def remove(self):
        if hasattr( self, 'SVG'):
            try:
                self.drawingVars.graphicsScene.removeItem( self.SVG )
            except RuntimeError:
                pass #Internal C++ object (PySide.QtSvg.QGraphicsSvgItem) already deleted.
            del self.SVG, self.SVGRenderer

dimensioningGrid = GridManager()

def applyGridRounding( x, y):
    parms = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Drawing_Dimensioning")
    if parms.GetBool('grid_on', False): #then alter x and y
        div = parms.GetFloat( 'grid_spacing', 5 )
        new_x = x - x%div
        new_y = y - y%div
        return new_x, new_y
    else:
        return x, y

