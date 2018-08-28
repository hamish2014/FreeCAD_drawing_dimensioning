from PySide import QtGui, QtCore, QtSvg
import FreeCAD
from drawingDimensioning.svgConstructor import SvgTextRenderer

dimensioningPreferences = {}
DimensioningPreferenceClasses = {}

def RGBtoUnsigned( r,g,b ):
    return (r << 24) + (g << 16) + (b << 8) 

def unsignedToRGB( v ):
    r = v >> 24
    g = (v >> 16) - (v >> 24 << 8 )
    b = (v >>  8) - (v >> 16 << 8 )
    return r, g, b 

def unsignedToRGBText(v):
    return 'rgb(%i,%i,%i)' % unsignedToRGB(v)


def DimensioningTaskDialog_generate_row_hbox( label, inputWidget ):
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget( QtGui.QLabel(label) )
    hbox.addStretch(1)
    if inputWidget <> None:
        hbox.addWidget(inputWidget)
    return hbox

class RepeatCheckBox:
    def __init__(self, dimensioningProcess, endFunction_parm_name):
        self.d = dimensioningProcess
        self.endFunction = dimensioningProcess.endFunction
        self.parmName = endFunction_parm_name
        self.defaultValue = True
        self.dd_parms = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Drawing_Dimensioning")
    def stateChanged( self, arg1):
        c = self.checkbox.isChecked()
        self.d.endFunction = self.endFunction if self.checkbox.isChecked() else None
        self.dd_parms.SetBool( self.parmName, c )
    def generateWidget( self, dimensioningProcess ):
        self.checkbox = QtGui.QCheckBox('repeat')
        c = self.dd_parms.GetBool( self.parmName, self.defaultValue )
        self.checkbox.setChecked( c )
        self.d.endFunction = self.endFunction if self.checkbox.isChecked() else None
        self.checkbox.stateChanged.connect( self.stateChanged )
        return self.checkbox   

        

class DimensioningPreference_prototype:
    def __init__(self, name, defaultValue, label, **extraKWs):
        self.name = name
        self.defaultValue = defaultValue
        self.label = label if label <> None else name
        self.category = "Parameters" # for the freecad property category
        self.dd_parms = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Drawing_Dimensioning")
        self.process_extraKWs(**extraKWs)
        self.initExtra()
    def process_extraKWs(self):
        pass
    def initExtra(self):
        pass
    def valueChanged( self, value ):
        self.dimensioningProcess.dimensionConstructorKWs[ self.name ] = value
    def get_values_from_dimension_object( self, obj, KWs ):
        KWs[self.name] = getattr( obj, self.name )


class DimensioningPreference_float(DimensioningPreference_prototype):
    def process_extraKWs(self, increment=1.0, min=0.0, decimals=2):
        self.spinBox_increment = increment
        self.spinBox_min = min
        self.spinBox_decimals = decimals
    def getDefaultValue(self):
        return self.dd_parms.GetFloat( self.name, self.defaultValue ) 
    def updateDefault(self):
        self.dd_parms.SetFloat( self.name,  self.dimensioningProcess.dimensionConstructorKWs[ self.name ] )
    def revertToDefault( self ):
        self.spinbox.setValue( self.getDefaultValue() )
    def generateWidget( self, dimensioningProcess ):
        self.dimensioningProcess = dimensioningProcess
        spinbox = QtGui.QDoubleSpinBox()
        spinbox.setValue( self.getDefaultValue() )
        spinbox.setMinimum( self.spinBox_min )
        spinbox.setSingleStep( self.spinBox_increment )
        spinbox.setDecimals(self.spinBox_decimals)
        spinbox.valueChanged.connect( self.valueChanged )
        self.spinbox = spinbox
        return  DimensioningTaskDialog_generate_row_hbox( self.label, spinbox )
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyFloat", self.name, self.category)
        KWs = self.dimensioningProcess.dimensionConstructorKWs
        setattr( obj, self.name, KWs[ self.name ] )
DimensioningPreferenceClasses["<type 'float'>"] = DimensioningPreference_float
DimensioningPreferenceClasses["<type 'int'>"] = DimensioningPreference_float


class DimensioningPreference_unicode(DimensioningPreference_prototype):
    def getDefaultValue(self):
        encoded_value = self.dd_parms.GetString( self.name, self.defaultValue.encode('utf8') ) 
        return unicode( encoded_value, 'utf8' )
    def updateDefault(self):
        self.dd_parms.SetString( self.name,  self.dimensioningProcess.dimensionConstructorKWs[ self.name ].encode('utf8') )
    def revertToDefault( self ):
        self.textbox.setText( self.getDefaultValue() )
    def generateWidget( self, dimensioningProcess ):
        self.dimensioningProcess = dimensioningProcess
        textbox = QtGui.QLineEdit()
        #debugPrint(1,self.getDefaultValue() )
        textbox.setText( self.getDefaultValue() )
        textbox.textChanged.connect( self.valueChanged )
        self.textbox = textbox
        return  DimensioningTaskDialog_generate_row_hbox( self.label, textbox )
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyString", self.name, self.category)
        KWs = self.dimensioningProcess.dimensionConstructorKWs
        setattr( obj, self.name, KWs[ self.name ].encode('utf8') )
    def get_values_from_dimension_object( self, obj, KWs ):
        #KWs[self.name] =  unicode( getattr( obj, self.name ), 'utf8'  )
        KWs[self.name] =  getattr( obj, self.name )
        if not type(KWs[self.name]) == unicode:
            raise ValueError,"type(KWs[%s]) != unicode but == %s" % (self.name, type(KWs[self.name]) ) 
DimensioningPreferenceClasses["<type 'unicode'>"] = DimensioningPreference_unicode

class DimensioningPreference_choice(DimensioningPreference_unicode):
    def valueChanged( self, value ):
        self.dimensioningProcess.dimensionConstructorKWs[ self.name ] = self.combobox.currentText()
    def getDefaultValue(self):
        encoded_value = self.dd_parms.GetString( self.name, self.defaultValue[0].encode('utf8') ) 
        return unicode( encoded_value, 'utf8' )
    def revertToDefault( self ):
        try:
            combobox.setCurrentIndex( self.defaultValue.index(self.getDefaultValue()) )
        except IndexError:
            pass
    def generateWidget( self, dimensioningProcess ):
        self.dimensioningProcess = dimensioningProcess
        combobox = QtGui.QComboBox()
        for i in self.defaultValue:
            combobox.addItem(i)
        try:
            combobox.setCurrentIndex( self.defaultValue.index(self.getDefaultValue()) )
        except IndexError:
            pass
        combobox.currentIndexChanged.connect( self.valueChanged )
        self.combobox = combobox
        return  DimensioningTaskDialog_generate_row_hbox( self.label, combobox )
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyEnumeration", self.name, self.category)
        setattr( obj, self.name, [ v.encode('utf8') for v in  self.defaultValue ])
        KWs = self.dimensioningProcess.dimensionConstructorKWs
        setattr( obj, self.name, KWs[ self.name ].encode('utf8') )
    def get_values_from_dimension_object( self, obj, KWs ):
        KWs[self.name] =  unicode( getattr( obj, self.name ), 'utf8'  )
DimensioningPreferenceClasses["choice"] = DimensioningPreference_choice


class DimensioningPreference_boolean(DimensioningPreference_prototype):
    def valueChanged( self, arg1):
        self.dimensioningProcess.dimensionConstructorKWs[ self.name ] = self.checkbox.isChecked()
    def getDefaultValue(self):
        return self.dd_parms.GetBool( self.name, self.defaultValue ) 
    def updateDefault(self):
        self.dd_parms.SetBool( self.name,  self.dimensioningProcess.dimensionConstructorKWs[ self.name ] )
    def revertToDefault( self ):
        self.checkbox.setChecked( self.getDefaultValue() )
    def generateWidget( self, dimensioningProcess ):
        self.dimensioningProcess = dimensioningProcess
        self.checkbox = QtGui.QCheckBox(self.label)
        self.revertToDefault()
        self.checkbox.stateChanged.connect( self.valueChanged )
        return  self.checkbox
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyBool", self.name, self.category)
        KWs = self.dimensioningProcess.dimensionConstructorKWs
        setattr( obj, self.name, KWs[ self.name ] )
DimensioningPreferenceClasses["<type 'bool'>"] = DimensioningPreference_boolean



class ClickRect(QtGui.QGraphicsRectItem):
    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clickFun()
class DimensioningPreference_color(DimensioningPreference_prototype):
    def initExtra(self):
        graphicsScene = QtGui.QGraphicsScene(0,0,30,30)
        pen = QtGui.QPen( QtGui.QColor(0,0,0,0) )
        pen.setWidth(0.0)
        rect = ClickRect(-100, -100, 200, 200)
        rect.setPen(pen)
        rect.clickFun = self.clickFun
        graphicsScene.addItem(rect) 
        self.graphicsScene = graphicsScene #protect from garbage collector
        self.colorRect = rect
    def clickFun(self):
        color = QtGui.QColorDialog.getColor( self.colorRect.brush().color() )
        if color.isValid():
            self.colorRect.setBrush( QtGui.QBrush(color) )
            self.dimensioningProcess.dimensionConstructorKWs[ self.name ] = 'rgb(%i,%i,%i)' % (color.red(), color.green(), color.blue() )
    def getDefaultValue(self):
        return unsignedToRGBText(self.dd_parms.GetUnsigned( self.name, self.defaultValue ))
    def updateDefault(self):
        color = self.colorRect.brush().color()
        self.dd_parms.SetUnsigned( self.name,  RGBtoUnsigned(color.red(), color.green(), color.blue()) )
    def revertToDefault( self ):
        clr = QtGui.QColor(*unsignedToRGB(self.dd_parms.GetUnsigned( self.name, self.defaultValue )) )
        self.colorRect.setBrush( QtGui.QBrush( clr ) )
        self.dimensioningProcess.dimensionConstructorKWs[ self.name ] = self.getDefaultValue()
    def generateWidget( self, dimensioningProcess, width = 60, height = 30 ):
        self.dimensioningProcess = dimensioningProcess
        clr = QtGui.QColor(*unsignedToRGB(self.dd_parms.GetUnsigned( self.name, self.defaultValue )) )
        self.colorRect.setBrush( QtGui.QBrush( clr ) )
        colorBox = QtGui.QGraphicsView( self.graphicsScene )
        colorBox.setMaximumWidth( width )
        colorBox.setMaximumHeight( height )
        colorBox.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff )
        colorBox.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff )
        return  DimensioningTaskDialog_generate_row_hbox( self.label, colorBox )
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyString", self.name, self.category)
        KWs = self.dimensioningProcess.dimensionConstructorKWs
        setattr( obj, self.name, KWs[ self.name ].encode('utf8') )
    def get_values_from_dimension_object( self, obj, KWs ):
        KWs[self.name] =  getattr( obj, self.name )

DimensioningPreferenceClasses["color"] = DimensioningPreference_color


class DimensioningPreference_font(DimensioningPreference_color):
    '3 linked parameters: $name_family $name_size $name_color' 
    def update_dimensionConstructorKWs(self , notUsed=None):
        textRenderer = self.dimensioningProcess.dimensionConstructorKWs[ self.name ]
        textRenderer.font_family = self.family_textbox.text()
        textRenderer.font_size = self.size_textbox.text()
        color = self.colorRect.brush().color()
        textRenderer.fill = 'rgb(%i,%i,%i)' % (color.red(), color.green(), color.blue() )

    def clickFun(self):
        color = QtGui.QColorDialog.getColor( self.colorRect.brush().color() )
        if color.isValid():
            self.colorRect.setBrush( QtGui.QBrush(color) )
            self.update_dimensionConstructorKWs()

    def getDefaultValue(self):
        family =  self.dd_parms.GetString( self.name + '_family', self.defaultValue[0])
        size = self.dd_parms.GetString( self.name + '_size', self.defaultValue[1])
        color = unsignedToRGBText(self.dd_parms.GetUnsigned( self.name + '_color', self.defaultValue[2] ))
        return SvgTextRenderer(family, size, color)

    def updateDefault(self):
        self.dd_parms.SetString( self.name + '_family', self.family_textbox.text() )
        self.dd_parms.SetString( self.name + '_size', self.size_textbox.text()  )
        color = self.colorRect.brush().color()
        self.dd_parms.SetUnsigned( self.name + '_color',  RGBtoUnsigned(color.red(), color.green(), color.blue()) )

    def revertToDefault( self ):
        self.family_textbox.setText( self.dd_parms.GetString(self.name + '_family', self.defaultValue[0]) )
        self.size_textbox.setText( self.dd_parms.GetString(self.name + '_size', self.defaultValue[1]) )
        clr = QtGui.QColor(*unsignedToRGB(self.dd_parms.GetUnsigned( self.name+'_color', self.defaultValue[2] )) )
        self.colorRect.setBrush( QtGui.QBrush( clr ) )
        self.update_dimensionConstructorKWs()

    def generateWidget( self, dimensioningProcess, width = 60, height = 30 ):
        self.dimensioningProcess = dimensioningProcess
        colorBox = QtGui.QGraphicsView( self.graphicsScene )
        colorBox.setMaximumWidth( width )
        colorBox.setMaximumHeight( height )
        colorBox.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff )
        colorBox.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff )
        self.family_textbox = QtGui.QLineEdit()
        self.size_textbox = QtGui.QLineEdit()

        groupbox = QtGui.QGroupBox(self.label)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget( self.family_textbox )
        hbox.addStretch(1)
        hbox.addWidget( self.size_textbox )
        hbox.addStretch(1)
        hbox.addWidget( colorBox )
        groupbox.setLayout(hbox)
        self.revertToDefault()
        self.family_textbox.textChanged.connect( self.update_dimensionConstructorKWs )
        self.size_textbox.textChanged.connect( self.update_dimensionConstructorKWs )
        return groupbox
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyString", self.name+ '_family', self.category)
        obj.addProperty("App::PropertyString", self.name+ '_size', self.category)
        obj.addProperty("App::PropertyString", self.name+ '_color', self.category)
        textRenderer = self.dimensioningProcess.dimensionConstructorKWs[ self.name ]
        setattr( obj, self.name + '_family', textRenderer.font_family.encode('utf8') )
        setattr( obj, self.name + '_size', textRenderer.font_size.encode('utf8') )
        setattr( obj, self.name + '_color', textRenderer.fill.encode('utf8') )
        
    def get_values_from_dimension_object( self, obj, KWs ):
        family = getattr( obj, self.name + '_family')
        size =  getattr( obj, self.name + '_size')
        color =  getattr( obj, self.name + '_color')
        KWs[self.name] = SvgTextRenderer(family, size, color)

DimensioningPreferenceClasses["font"] = DimensioningPreference_font

class DimensioningPreference_string_list(DimensioningPreference_prototype):
    def val_to_FreeCAD_parm( self, val ):
        return '\n'.join(text.encode('utf8') for text in val )
    def FreeCAD_parm_to_val( self, FreeCAD_parm ):
        return [ unicode( line, 'utf8' ) for line in FreeCAD_parm.split('\n') ]
    def getDefaultValue(self):
        return self.FreeCAD_parm_to_val( self.dd_parms.GetString( self.name, self.val_to_FreeCAD_parm( self.defaultValue ) ) )
    def updateDefault(self):
        self.dd_parms.SetString( self.name, self.val_to_FreeCAD_parm( self.dimensioningProcess.dimensionConstructorKWs[ self.name ] ) )
    def set_textbox_text( self, values ):
        self.textbox.clear()
        for v in values:
            self.textbox.append( str(v) if type(v) == float else v )
    def revertToDefault( self ):
        self.set_textbox_text( self.getDefaultValue() )
    def generateWidget( self, dimensioningProcess ):
        self.dimensioningProcess = dimensioningProcess
        self.textbox = QtGui.QTextEdit()
        self.revertToDefault()
        self.textbox.textChanged.connect( self.textChanged )
        return DimensioningTaskDialog_generate_row_hbox( self.label, self.textbox )
    def textChanged( self, arg1=None):
        self.dimensioningProcess.dimensionConstructorKWs[ self.name ] = self.textbox.toPlainText().split('\n')
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyStringList", self.name, self.category)
        KWs = self.dimensioningProcess.dimensionConstructorKWs
        setattr( obj, self.name, [ v.encode('utf8') for v in KWs[ self.name ] ] )
    def get_values_from_dimension_object( self, obj, KWs ):
        KWs[self.name] = getattr( obj, self.name )
DimensioningPreferenceClasses['string_list'] = DimensioningPreference_string_list

class DimensioningPreference_float_list(DimensioningPreference_string_list):
    def val_to_FreeCAD_parm( self, val ):
        return '\n'.join(map(str, val))
    def FreeCAD_parm_to_val( self, FreeCAD_parm ):
        return map(float, FreeCAD_parm.split('\n'))
    def textChanged( self, arg1=None):
        try:
            self.dimensioningProcess.dimensionConstructorKWs[ self.name ] = map(float, [v for v in self.textbox.toPlainText().split('\n') if len(v.strip())>0])
            #debugPrint(1, str(self.dimensioningProcess.dimensionConstructorKWs[ self.name ]))
        except:
            App.Console.PrintError(traceback.format_exc())
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyFloatList", self.name, self.category)
        KWs = self.dimensioningProcess.dimensionConstructorKWs
        setattr( obj, self.name, KWs[ self.name ] )
DimensioningPreferenceClasses['float_list'] = DimensioningPreference_float_list

class UnitSelectionWidget:
    def __init__(self):
        self.unitSelected_combobox_index = 0
        self.customScaleValue = 1.0
        self.dd_parms = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Drawing_Dimensioning")

    def unit_factor( self, unit_text, customScaleValue):
        if unit_text <> 'custom':
            if unit_text == 'Edit->Preference->Unit':
<<<<<<< HEAD:drawingDimensioning/command/preferences.py
                #found using FreeCAD.ParamGet("User parameter:BaseApp/Preferences").Export('/tmp/p3')
                UserSchema = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").GetInt("UserSchema")
=======
                #found using App.ParamGet("User parameter:BaseApp/Preferences").Export('/tmp/p3')
                UserSchema = App.ParamGet("User parameter:BaseApp/Preferences/Units").GetInt("UserSchema")
                v = App.Units.Quantity(1,App.Units.Length).getUserPreferred()[1]
>>>>>>> d73728a75b595e3a40e749ca1d939e218d14b11d:dimensioning.py
            else:
                UserSchema = ['mm','m','inch'].index( unit_text )
                if UserSchema == 0: #standard (mm/kg/s/degree
                    v = 1.0
                elif UserSchema == 1: #standard (m/kg/s/degree)
                    v = 1000.0
                else: #either US customary, or Imperial decimal
                    v = 25.4
        else:
            v = customScaleValue
        return 1.0/v if v <> 0 else 1.0

    def settingsChanged(self, notUsed=False):
        unit_text = self.unitSelected_combobox.currentText()
        self.unitSelected_combobox_index = self.unitSelected_combobox.currentIndex()
        self.customScaleValue = self.customUnit_spinbox.value()
        self.dimensioningProcess.unitConversionFactor = self.unit_factor( unit_text, self.customScaleValue )

    def groupBoxToggled( self, checked):
        self.dd_parms.SetBool("show_unit_options", checked)
        self.groupbox.setMaximumHeight(1000 if checked else 18)

    def generateWidget(self, dimensioningProcess):
        self.dimensioningProcess = dimensioningProcess
        groupbox = QtGui.QGroupBox("Unit Options")
        groupbox.setCheckable( True ) 
        groupbox.toggled.connect( self.groupBoxToggled )
        self.groupbox = groupbox
        checked = self.dd_parms.GetBool("show_unit_options",True)
        groupbox.setChecked(checked)
        #self.groupBoxToggled( checked )
        #groupbox.setCheckState( QtCore.Qt.CheckState.Checked )
        vbox = QtGui.QVBoxLayout()
        unitSelected = QtGui.QComboBox()
        unitSelected.addItem('Edit->Preference->Unit')
        unitSelected.addItem('mm')
        unitSelected.addItem('inch')
        unitSelected.addItem('m')
        unitSelected.addItem('custom')
        unitSelected.setCurrentIndex( self.unitSelected_combobox_index )
        unitSelected.currentIndexChanged.connect( self.settingsChanged )
        vbox.addWidget( unitSelected )
        self.unitSelected_combobox = unitSelected
        spinbox = QtGui.QDoubleSpinBox()
        spinbox.setValue( self.customScaleValue )
        spinbox.setMinimum( 0 )
        spinbox.setDecimals( 6 )
        spinbox.setSingleStep( 0.1 )
        spinbox.setSuffix('/mm')
        spinbox.valueChanged.connect( self.settingsChanged )
        vbox.addLayout( DimensioningTaskDialog_generate_row_hbox('custom', spinbox) )
        self.customUnit_spinbox = spinbox
        groupbox.setLayout(vbox)
        self.settingsChanged()
        return groupbox

    def add_properties_to_dimension_object( self, obj ):
        KWs = self.dimensioningProcess.dimensionConstructorKWs
        obj.addProperty("App::PropertyEnumeration", 'unit_scheme', 'Units')
        obj.unit_scheme = [ v.encode('utf8') for v in ['Edit->Preference->Unit','mm','inch','m','custom'] ]
        obj.unit_scheme = self.unitSelected_combobox.currentText().encode('utf8')
        obj.addProperty("App::PropertyFloat", 'unit_custom_scale', 'Units')
        obj.unit_custom_scale = self.customScaleValue

    def get_values_from_dimension_object( self, obj, KWs ):
        unit_text =  unicode( obj.unit_scheme, 'utf8'  )
        KWs['unit_scaling_factor'] = self.unit_factor( unit_text, obj.unit_custom_scale )

unitSelectionWidget = UnitSelectionWidget()



<<<<<<< HEAD:drawingDimensioning/command/preferences.py
=======
    def createForm(self):
        title, iconPath, dialogWidgets, preferences = self.initArgs
        self.form = DimensioningTaskDialogForm( self.dimensiongProcess, dialogWidgets, preferences )
        self.form.setWindowTitle( title )    
        if iconPath <> None:
            self.form.setWindowIcon( QtGui.QIcon( iconPath ) )

    def reject(self): #close button
        import previewDimension
        if hasattr(previewDimension.preview, 'drawingVars'):
            previewDimension.removePreviewGraphicItems( recomputeActiveDocument = True )
        else:
            recomputeWithOutViewReset(self.dimensiongProcess.drawingVars )
            FreeCADGui.Control.closeDialog()
    def getStandardButtons(self): #http://forum.freecadweb.org/viewtopic.php?f=10&t=11801
        return 0x00200000 #close button


class DimensioningTaskDialogForm(QtGui.QWidget):
    
    def __init__(self, dimensiongProcess, parameters, preferences ):
        super(DimensioningTaskDialogForm, self).__init__()
        self.dd_dimensiongProcess = dimensiongProcess
        self.dd_parameters = parameters
        self.dd_preferences = preferences#dd prefix added to avoid possible name collision
        self.initUI()
        
    def initUI(self):
        vbox = QtGui.QVBoxLayout()
        for parm in self.dd_parameters:
            w = parm.generateWidget(self.dd_dimensiongProcess )
            if isinstance(w, QtGui.QLayout):
                vbox.addLayout( w )
            else:
                vbox.addWidget( w )
        if len( self.dd_preferences ) > 0:
            preferenceGroupbox = QtGui.QGroupBox("Preferences")
            vbox_pref = QtGui.QVBoxLayout()
            for pref in self.dd_preferences:
                row =  pref.generateWidget(self.dd_dimensiongProcess )
                if isinstance(row, QtGui.QLayout):
                    vbox_pref.addLayout( row )
                else:
                    vbox_pref.addWidget( row )
            preferenceGroupbox.setLayout(vbox_pref)
            vbox.addWidget(preferenceGroupbox)

            #buttonRevert = QtGui.QPushButton("Revert to default")
            #buttonRevert.clicked.connect( self.revertToDefaults )
            #vbox.addWidget( buttonRevert )

            buttonSave = QtGui.QPushButton("Set as default")
            buttonSave.clicked.connect( self.updateDefaults )
            vbox.addWidget( buttonSave )
        self.setLayout(vbox)            

    def updateDefaults(self):
        debugPrint(4,'updateDefaults clicked')
        for parm in self.dd_parameters:
            if hasattr(parm , 'updateDefault'):
                parm.updateDefault()
        for pref in self.dd_preferences:
            pref.updateDefault()
        debugPrint(3,'updateDefaults successfully completed')
    def revertToDefaults( self ):
        debugPrint(4,'revertToDefault clicked')
        for parm in self.dd_parameters:
            if hasattr(parm , 'revertToDefault'):
                parm.revertToDefault()
        for pref in self.dd_preferences:
            pref.revertToDefault()
        debugPrint(3,'revertToDefault successfully completed')



def recomputeWithOutViewReset( drawingVars ):
    '''
    By default app.recompute() resets the drawing view, which can be rather frustrating...
    '''
    printGraphicsViewInfo( drawingVars )
    gV =  drawingVars.graphicsView
    T = gV.transform()
    scale = T.m11()
    ##attempting to find centre of view
    #dx = gV.mapToScene( 0,0).x()
    #dy = gV.mapToScene( 0,0).y()
    ## now scene_x = view_x/scale + dx; so
    #centerView = [
    #    0.5*gV.width(),
    #    0.5*gV.height(),
    #    ]
    #centerScene = gV.mapToScene( *centerView )
    #centerOn approach did not work rather using scroll bars.
    h_scrollValue = gV.horizontalScrollBar().value()
    v_scrollValue = gV.verticalScrollBar().value()
    import selectionOverlay
    selectionOverlay.hideSelectionGraphicsItems()    
    drawingVars.page.touch()
    App.ActiveDocument.recompute()
    gV.scale( scale , scale )
    #scale correction
    for i in range(3):
        scale_actual = gV.transform().m11()
        debugPrint(4, 'scale_desired %1.3f scale_actual %1.3f' % (scale, scale_actual))
        s_correction = scale / scale_actual
        gV.scale( s_correction, s_correction )

    gV.horizontalScrollBar().setValue( h_scrollValue )
    gV.verticalScrollBar().setValue( v_scrollValue )
    printGraphicsViewInfo( drawingVars )


def printGraphicsViewInfo( drawingVars ):
    '''
    A PySide.QtGui.QTransform object contains a 3 x 3 matrix. The m31 (dx ) and m32 (dy ) elements specify horizontal and vertical translation.
    The m11 and m22 elements specify horizontal and vertical scaling.
    The m21 and m12 elements specify horizontal and vertical shearing .
    And finally, the m13 and m23 elements specify horizontal and vertical projection, with m33 as an additional projection factor.

    This function was written help restore the view transform after App.ActiveDocument.recompute();
    example of how to get T, T= preview.drawingVars.graphicsView.transform()

    DrawingView.cpp: line134: s->setSceneRect(m_outlineItem->boundingRect().adjusted(-10, -10, 10, 10)); # s is QGraphicsScene  used for scroll bars!
    '''
    T = drawingVars.graphicsView.transform()
    sx, sy, dx, dy = T.m11(), T.m22(), T.m31(), T.m32()
    debugPrint(4,'graphicsView transform info: sx %1.2f, sy %1.2f, dx %1.2f, dy %1.2f' % (sx, sy, dx, dy) )
    debugPrint(4,'    [ %1.2f  %1.2f  %1.2f ]' % (T.m11(), T.m12(), T.m13() ))
    debugPrint(4,'M = [ %1.2f  %1.2f  %1.2f ]' % (T.m21(), T.m22(), T.m23() ))
    debugPrint(4,'    [ %1.2f  %1.2f  %1.2f ]' % (T.m31(), T.m32(), T.m33() ))

    #r = preview.drawingVars.graphicsView.sceneRect() #seems to be used for scroll bars, not for anything else
    #debugPrint(2,'graphicsView.sceneRect info: topLeft.x %3.2f, topLeft.y %3.2f, bottomRight.x %3.2f, bottomRight.y %3.2f' \
    #               % (r.topLeft().x(), r.topLeft().y(), r.bottomRight().x(), r.bottomRight().y() ) )

    #T = drawingVars.graphicsView.viewportTransform()
    #sx, sy, dx, dy = T.m11(), T.m22(), T.m31(), T.m32()
    #debugPrint(2,'viewPort transform info: sx %1.2f, sy %1.2f, dx %1.2f, dy %1.2f' % (sx, sy, dx, dy) )
    #debugPrint(4,'    [ %1.2f  %1.2f  %1.2f ]' % (T.m11(), T.m12(), T.m13() ))
    #debugPrint(4,'M = [ %1.2f  %1.2f  %1.2f ]' % (T.m21(), T.m22(), T.m23() ))
    #debugPrint(4,'    [ %1.2f  %1.2f  %1.2f ]' % (T.m31(), T.m32(), T.m33() ))


class helpCommand:
    def Activated(self):
        QtGui.QMessageBox.information( 
            QtGui.qApp.activeWindow(), 
            'Drawing Dimensioning Help', 
            '''For help getting started, please refer to the following YouTube video tutorials:

- https://www.youtube.com/watch?v=CTEPu50bG4U
- https://www.youtube.com/watch?v=ztMTLp4wZx4 '''  )
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/help.svg', 
            'MenuText': 'Help', 
            'ToolTip': 'Help'
            } 

FreeCADGui.addCommand('dd_help', helpCommand())


def dimensionableObjects ( page ):
    'commonly used code in Activate, exclude centerlines'
    from unfold import Proxy_unfold
    drawingViews = []
    for obj in page.Group:
        if obj.isDerivedFrom("Drawing::FeatureView"):
            if hasattr(obj, 'Proxy'):
                # skipping all drawing_dimensioning objects except unfolds
                if hasattr( obj.Proxy, "dimensionProcess"):
                    if not isinstance( obj.Proxy, Proxy_unfold ):
                        continue
            drawingViews.append( obj )
    return drawingViews
>>>>>>> d73728a75b595e3a40e749ca1d939e218d14b11d:dimensioning.py
