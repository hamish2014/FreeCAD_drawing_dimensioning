from drawingDimensioning.py3_helpers import unicode
from drawingDimensioning.core import *
from drawingDimensioning import selectionOverlay, previewDimension
from drawingDimensioning.svgConstructor import *
from drawingDimensioning.proxies import *
from drawingDimensioning.grid import gridOptionsGroupBox, dimensioningGrid
from .preferences import *

class DimensioningCommand:
    def __init__(self, proxy_svgFun=None, add_viewScale_KW = False):
        self.proxy_svgFun = proxy_svgFun
        self.add_viewScale_KW = add_viewScale_KW  # for Proxy, set to true for centerLines
        self.dialogWidgets = []
        self.preferences = []
        self.ViewObjectProxyClass = Proxy_DimensionViewObject_prototype

    def activate( self, drawingVars, dialogTitle=None, dialogIconPath=None, endFunction=None, grid=True):
        self.drawingVars = drawingVars
        self.dialogIconPath = dialogIconPath
        self.endFunction = endFunction
        extraWidgets = []
        if self.endFunction != None:
            endFunction_parm_name = 'repeat_' + str(endFunction).split()[2]
            extraWidgets.append( RepeatCheckBox(self, endFunction_parm_name) )
            if grid:
               extraWidgets.append( gridOptionsGroupBox )
        self.selections = []
        KWs = {}
        for pref in self.preferences:
            KWs[pref.name] = pref.getDefaultValue()
        self.dimensionConstructorKWs = KWs
        if dialogTitle != None:
            self.taskDialog = DimensioningTaskDialog( self, dialogTitle, dialogIconPath, extraWidgets + self.dialogWidgets, self.preferences)
            FreeCADGui.Control.showDialog( self.taskDialog )
        else:
            self.taskDialog = None
        if grid:
            dimensioningGrid.initialize( drawingVars )

    def registerPreference( self, name, defaultValue=None, label=None, kind='guess', **extraKWs):
        if not name in dimensioningPreferences:
            if defaultValue == None:
                raise ValueError("registerPreferenceError: %s default required in first definition" % name)
            if type(defaultValue) == str:
                defaultValue = unicode(defaultValue, 'utf8')
            class_key = kind if kind != 'guess' else str(type(defaultValue))
            if class_key in DimensioningPreferenceClasses:
                dimensioningPreferences[name] = DimensioningPreferenceClasses[class_key](name, defaultValue, label, **extraKWs)
            else:
                App.Console.PrintError("registerPreferenceError: %s : defaultValue %s, kind %s [class_key %s] not understood, ignoring!\n" % (name, defaultValue, kind, class_key) )
                return 
        elif defaultValue != None:
            raise ValueError("registerPreferenceError: default for %s redeclared" % name)
        self.preferences.append( dimensioningPreferences[name] )


class DimensioningTaskDialog:
    def __init__(self, dimensioningCommand, title, iconPath, dialogWidgets, preferences ):
        self.dimensioningCommand = dimensioningCommand
        self.initArgs = title, iconPath, dialogWidgets, preferences
        self.createForm()

    def createForm(self):
        title, iconPath, dialogWidgets, preferences = self.initArgs
        self.form = DimensioningTaskDialogForm( self.dimensioningCommand, dialogWidgets, preferences )
        self.form.setWindowTitle( title )    
        if iconPath != None:
            self.form.setWindowIcon( QtGui.QIcon( iconPath ) )

    def reject(self): #close button
        import drawingDimensioning.previewDimension
        if hasattr(previewDimension.preview, 'drawingVars'):
            previewDimension.removePreviewGraphicItems( recomputeActiveDocument = True )
        else:
            recomputeWithOutViewReset(self.dimensioningCommand.drawingVars )
            FreeCADGui.Control.closeDialog()
    def getStandardButtons(self): #http://forum.freecadweb.org/viewtopic.php?f=10&t=11801
        return 0x00200000 #close button

class DimensioningTaskDialogForm(QtGui.QWidget):
    def __init__(self, dimensioningCommand, parameters, preferences ):
        super(DimensioningTaskDialogForm, self).__init__()
        self.dd_dimensioningCommand = dimensioningCommand
        self.dd_parameters = parameters
        self.dd_preferences = preferences#dd prefix added to avoid possible name collision
        self.initUI()
        
    def initUI(self):
        vbox = QtGui.QVBoxLayout()
        for parm in self.dd_parameters:
            w = parm.generateWidget(self.dd_dimensioningCommand )
            if isinstance(w, QtGui.QLayout):
                vbox.addLayout( w )
            else:
                vbox.addWidget( w )
        if len( self.dd_preferences ) > 0:
            preferenceGroupbox = QtGui.QGroupBox("Preferences")
            vbox_pref = QtGui.QVBoxLayout()
            for pref in self.dd_preferences:
                row =  pref.generateWidget(self.dd_dimensioningCommand )
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
