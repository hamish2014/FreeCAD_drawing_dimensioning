from dimensioning import *
import datetime

parms = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Drawing_Dimensioning")

class TaskDialog_pagePreferences:
    def __init__(self ):
        self.form = Form_pagePreferences()
        self.form.setWindowTitle('drawing shortcut settings')    
        self.form.setWindowIcon( QtGui.QIcon(':/dd/icons/drawing-shortcut-settings.svg'))
                       
    def accept(self):
        parms.SetString( 'shortcut_page_templates', self.form.Templates_textEdit.toPlainText() )
        parms.SetString( 'shortcut_substations_matches', self.form.Substations_matches_textEdit.toPlainText())
        parms.SetString( 'shortcut_substations_with', self.form.Substations_with_textEdit.toPlainText())
        FreeCADGui.Control.closeDialog()

    def reject(self):
        FreeCADGui.Control.closeDialog()


class Form_pagePreferences(QtGui.QWidget):
    def __init__(self):
        super(Form_pagePreferences, self).__init__()
        self.initUI()        
    def initUI(self):
        vbox = QtGui.QVBoxLayout()
        GroupBox_templates = QtGui.QGroupBox('Page Templates:')
        vbox2 =  QtGui.QVBoxLayout()
        Templates_textEdit = QtGui.QPlainTextEdit()
        Templates_textEdit.setPlainText( parms.GetString( 'shortcut_page_templates', ''))
        Templates_textEdit.setMinimumHeight(42)
        vbox2.addWidget( Templates_textEdit )
        self.Templates_textEdit = Templates_textEdit
        addTemplate_button = QtGui.QPushButton('+')
        addTemplate_button.clicked.connect( self.addTemplate_button_clicked )
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(addTemplate_button )
        vbox2.addLayout(hbox)
        self.addTemplate_button = addTemplate_button
        vbox2.addWidget( QtGui.QLabel('*FreeCAD needs to be restared'))
        vbox2.addWidget( QtGui.QLabel('for changes to take effect'))
        GroupBox_templates.setLayout(vbox2)
        vbox.addWidget(GroupBox_templates)

        GroupBox_substations = QtGui.QGroupBox('Page Editable Substations:')
        vbox3 =  QtGui.QVBoxLayout()
        Substations_matches_textEdit = QtGui.QPlainTextEdit()
        Substations_with_textEdit = QtGui.QPlainTextEdit()
        Substations_matches_textEdit.setPlainText( parms.GetString( 'shortcut_substations_matches', ''))
        Substations_with_textEdit.setPlainText( parms.GetString( 'shortcut_substations_with', ''))
        hbox3 = QtGui.QHBoxLayout()
        vbox4 = QtGui.QVBoxLayout()
        vbox4.addWidget( QtGui.QLabel('Substitute'))
        vbox4.addWidget( Substations_matches_textEdit )
        hbox3.addLayout(vbox4 )
        #hbox3.addStretch(1)
        hbox3.addWidget(QtGui.QLabel('->'))
        #hbox3.addStretch(1)
        vbox5 = QtGui.QVBoxLayout()
        vbox5.addWidget( QtGui.QLabel('with'))
        vbox5.addWidget( Substations_with_textEdit )
        hbox3.addLayout(vbox5 )
        vbox3.addLayout(hbox3)
        self.Substations_matches_textEdit = Substations_matches_textEdit
        self.Substations_with_textEdit = Substations_with_textEdit
        substatutionHelp_button = QtGui.QPushButton('?')
        substatutionHelp_button.clicked.connect( self.substatutionHelp_button_clicked )
        hbox4 = QtGui.QHBoxLayout()
        hbox4.addStretch(1)
        hbox4.addWidget(substatutionHelp_button )
        vbox3.addLayout(hbox4)
        GroupBox_substations.setLayout(vbox3)
        vbox.addWidget(GroupBox_substations)

        self.setLayout(vbox) 
    def addTemplate_button_clicked( self ):
        try:
            dialogDir = os.path.join( FreeCAD.getResourceDir(), 'Mod', 'Drawing', 'Templates' )
            dialog = QtGui.QFileDialog(
                QtGui.qApp.activeWindow(),
                "Select Drawing Page Template",
                dialogDir
                )
            dialog.setNameFilter("Drawing Templates (*.svg *.dxf)")
            if dialog.exec_():
                filename = dialog.selectedFiles()[0]
                self.Templates_textEdit.appendPlainText(filename )
        except:
            FreeCAD.Console.PrintError(traceback.format_exc())    
    
    def substatutionHelp_button_clicked(self):
        QtGui.QMessageBox.information( 
            QtGui.qApp.activeWindow(), 
            'Drawing Dimensioning Shortcut Substatutions Help', 
            '''When a page is created using drawing dimension shortcut command, each line in that page's editable texts is checked against these substatution lists.

Examples:
- Designed by Name -> Marco Polo
- Title -> $BASENAME
- Date ->  $DATETIME %_d %b %Y

Supported context specific variables: BASENAME DIRECTORY DIRNAME DATETIME'''  )
            

def doSubstituations( EditableTexts ):
    MatchList = parms.GetString( 'shortcut_substations_matches').split('\n')
    ReplaceWithList = parms.GetString( 'shortcut_substations_with').split('\n')
    BASENAME = os.path.splitext(os.path.basename( FreeCAD.ActiveDocument.FileName ))[0]
    DIRNAME = os.path.dirname( FreeCAD.ActiveDocument.FileName )
    DIRECTORY =  os.path.basename( DIRNAME )
    output = []
    for line in EditableTexts:
        matchFound = False
        for textToMatch, replaceWith in zip(MatchList, ReplaceWithList):
            if line == textToMatch:
                newLine = replaceWith
                if BASENAME <> '':
                    newLine = replaceWith.replace('$BASENAME',BASENAME).replace('$DIRECTORY',DIRECTORY).replace('$DIRNAME', DIRNAME)
                if '$DATETIME' in newLine:
                    p = newLine.find('$DATETIME')
                    newLine =  newLine[:p] + datetime.datetime.now().strftime(newLine[p+len('$DATETIME '):])
                output.append(newLine)
                matchFound = True
                continue
        if not matchFound:
            output.append(line)
    return output



class NewPagePreferencesCommand:
    def Activated(self):
        self.taskDialog = TaskDialog_pagePreferences()
        FreeCADGui.Control.showDialog( self.taskDialog )
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/drawing-shortcut-settings.svg' , 
            'MenuText': 'Change the settings for new drawing page shortcuts', 
            } 

FreeCADGui.addCommand('dd_new_drawing_page_preferences', NewPagePreferencesCommand())

class NewPageShorcut:
    def __init__(self, template, icon):
        self.template = template
        self.icon = icon
    def Activated(self):
        Page = FreeCAD.ActiveDocument.addObject('Drawing::FeaturePage','Page')
        Page.Template = self.template
        Page.EditableTexts = doSubstituations( Page.EditableTexts )
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.getObject(Page.Name).show()

    def GetResources(self): 
        return {
            'Pixmap' :  self.icon, 
            'MenuText': 'Shortcut for creating a new drawing page', 
            } 

newpageShortcuts = []
templateFns = [ s.strip() for s in parms.GetString( 'shortcut_page_templates').split('\n') if len(s.strip()) > 0 ]
for i, templateFn in enumerate(templateFns[:4]):
    cmd_name = 'dd_new_drawing_page_%i' % (i+1)
    FreeCADGui.addCommand(cmd_name, NewPageShorcut(templateFn,  ':/dd/icons/new-drawing-page-%i.svg' %(i+1) ) )
    newpageShortcuts.append( cmd_name )

class DrawingOrthoViewsCommand:
    def Activated(self):
        FreeCADGui.runCommand('Drawing_OrthoViews')
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/drawing-orthoviews.svg' , 
            'MenuText': 'Shortcut to Drawing-OrthoViews Command', 
            } 

FreeCADGui.addCommand('dd_Drawing_OrthoViews', DrawingOrthoViewsCommand())
