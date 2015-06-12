# This Python file uses the following encoding: utf-8

from dimensioning import *
import subprocess

def shellCmd(cmd, callDirectory=None):
    debugPrint(3,'$' + cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=callDirectory)
    stdout, stderr = p.communicate()
    if stdout <> '':
        debugPrint(3,'stdout:%s' % stdout )
    if p.returncode <> 0:
        raise RuntimeError, '$ %s \n STDERR:%s' % (cmd, stderr)
    return stdout

class ExportToDxfCommand:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dialog = QtGui.QFileDialog(
            QtGui.qApp.activeWindow(),
            "Enter the dxf file name"
            )
        dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        dialog.setNameFilter("DXF files (*.dxf)")
        lineEdit = [c for c in dialog.children() if isinstance(c, QtGui.QLineEdit) ][0]
        lineEdit.setText(FreeCAD.ActiveDocument.Label + '.dxf')
        if dialog.exec_():
            dxf_fn = dialog.selectedFiles()[0]
            debugPrint(3,'saving to %s' % dxf_fn)
            eps_fn = dxf_fn[:-4] + '.eps'
            if os.path.exists(eps_fn):
                raise RuntimeError,"eps file (%s) exists, aborting operation" % eps_fn
            V.page.PageResult
            shellCmd('inkscape -f %s -E %s' % (V.page.PageResult, eps_fn))
            try:
                shellCmd("pstoedit -dt -f 'dxf:-polyaslines -mm' %s %s" % (eps_fn, dxf_fn) ) 
                QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Success", "%s successfully created" % dxf_fn )
            except RuntimeError, msg:
                QtGui.QMessageBox.critical( QtGui.qApp.activeWindow(), "pstoedit failed.", "%s\n\n suggestion: relaunch FreeCAD from BASH and try again." % msg )
            #only works if FreeCAD is launched from bash shell?
            #work around for this?
            shellCmd('rm %s' % eps_fn)

    def GetResources(self): 
        return {
            #'Pixmap' : os.path.join( iconPath , 'drawLineWithArrow.svg' ) , 
            'Pixmap' : os.path.join( iconPath, 'exportToDxf.svg'),
            'MenuText': 'shortcut command for exporting active drawing page to dxf (requires inkscape and pstoedit)', 
            } 

FreeCADGui.addCommand('dd_exportToDxf', ExportToDxfCommand())
