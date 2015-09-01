# This Python file uses the following encoding: utf-8

from dimensioning import *
import subprocess

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
            export_via_dxfwrite( dxf_fn, V)
            #export_via_pstoedit( dxf_fn, V)

    def GetResources(self): 
        return {
            #'Pixmap' : os.path.join( iconPath , 'drawLineWithArrow.svg' ) , 
            'Pixmap' : os.path.join( iconPath, 'exportToDxf.svg'),
            'MenuText': 'shortcut command for exporting active drawing page to dxf (requires inkscape and pstoedit)', 
            } 

FreeCADGui.addCommand('dd_exportToDxf', ExportToDxfCommand())


def shellCmd(cmd, callDirectory=None):
    debugPrint(3,'$' + cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=callDirectory)
    stdout, stderr = p.communicate()
    if stdout <> '':
        debugPrint(3,'stdout:%s' % stdout )
    if p.returncode <> 0:
        raise RuntimeError, '$ %s \n STDERR:%s' % (cmd, stderr)
    return stdout


def export_via_pstoedit( dxf_fn, V):
    eps_fn = dxf_fn[:-4] + '.eps'
    if os.path.exists(eps_fn):
        raise RuntimeError,"eps file (%s) exists, aborting operation" % eps_fn
    V.page.PageResult
    shellCmd('inkscape -f %s -E %s' % (V.page.PageResult, eps_fn)) #circle maintained after this step
    try:
        shellCmd("pstoedit -dt -f 'dxf:-polyaslines -mm' -flat 0.01 %s %s" % (eps_fn, dxf_fn) )
        # man pstoedit
        # -dt: Draw text - Text is drawn as polygons
        # -f "format[:options]" target output format recognized by pstoedit.
        # -flat [flatness factor] If the output format does not support curves in the way PostScript does or if the -nc option is specified, all curves are approximated by lines. Using the -flat option  one  can  control  this approximation. This parameter is directly converted to a PostScript setflat command. Higher numbers, e.g. 10 give rougher, lower numbers, e.g. 0.1 finer approximations. #I the default is 1
        QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Success", "%s successfully created" % dxf_fn )
    except RuntimeError, msg:
        QtGui.QMessageBox.critical( QtGui.qApp.activeWindow(), "pstoedit failed.", "%s\n\n suggestion: relaunch FreeCAD from BASH and try again." % msg )
        #only works if FreeCAD is launched from bash shell?
        #work around for this?
        shellCmd('rm %s' % eps_fn)


def export_via_dxfwrite(  dxf_fn, V):
    import sys
    from XMLlib import SvgXMLTreeNode
    from svgLib_dd import SvgTextParser
    from numpy import arctan2
    from circleLib import fitCircle_to_path, findCircularArcCentrePoint, pointsAlongCircularArc
    sys.path.append('/tmp/dxfwrite-1.2.0/build/lib.linux-x86_64-2.7')
    from dxfwrite import DXFEngine as dxf
    drawing = dxf.drawing( dxf_fn)
    
    pageSvg = open(V.page.PageResult).read()
    XML_tree =  SvgXMLTreeNode( pageSvg,0)
    scaling = XML_tree.scaling()
    SelectViewObjectPoint_loc = None
    for element in XML_tree.getAllElements():
        if element.tag == 'circle':
            x, y = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
            r =  float( element.parms['r'] )* scaling
            drawing.add( dxf.circle( r, (x,-y)) )
        elif element.tag == 'line':
            x1, y1 = element.applyTransforms( float( element.parms['x1'] ), float( element.parms['y1'] ) )
            x2, y2 = element.applyTransforms( float( element.parms['x2'] ), float( element.parms['y2'] ) )
            drawing.add( dxf.line( (x1, -y1), (x2,-y2) ) )
        elif element.tag == 'text' and element.parms.has_key('x'):
            x,y = element.applyTransforms( float( element.parms['x'] ), float( element.parms['y'] ) )
            t = SvgTextParser(element.XML[element.pStart: element.pEnd ] )
            drawing.add(dxf.text( t.text, insert=(x, -y), layer='TEXTLAYER') )
        #elif element.tag == 'path': 
        else:
            FreeCAD.Console.PrintWarning('dxf_export: Warning export of %s elemnets not supported, ignoring...\n' % element.tag )

    #drawing.add(dxf.text('Test', insert=(0, 0.2), layer='TEXTLAYER'))
    drawing.save()
