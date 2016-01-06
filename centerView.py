# -*- coding: utf-8 -*-

import FreeCAD,FreeCADGui,os,re
from XMLlib import SvgXMLTreeNode
from svgLib_dd import SvgPath
from dimensioning import debugPrint


def getPoints(svg):
    "returns a series of (x,y) points from an SVG fragment"
    # adapted from selectionOverlay.py
    points = []
    XML_tree =  SvgXMLTreeNode(svg,0)
    scaling = XML_tree.scaling()
    SelectViewObjectPoint_loc = None
    for element in XML_tree.getAllElements():
        if element.tag == 'circle':
            x, y = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
            points.append((x,y))
        elif element.tag == 'ellipse':
            x, y = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
            points.append((x,y))
        elif element.tag == 'text' and element.parms.has_key('x'):
            x, y = element.applyTransforms( float( element.parms['x'] ), float( element.parms['y'] ) )
            points.append((x,y))
        elif element.tag == 'path': 
            path = SvgPath( element )
            for p in path.points:
                points.append((p.x, p.y))
        elif element.tag == 'line':
            x1, y1 = element.applyTransforms( float( element.parms['x1'] ), float( element.parms['y1'] ) )
            x2, y2 = element.applyTransforms( float( element.parms['x2'] ), float( element.parms['y2'] ) )
            points.append((x1, y1))
            points.append((x2, y2))
    return points


def getCenterPoint(viewObject):
    "returns the (x,y) center point of a DrawingView object"
    if not hasattr(viewObject, 'ViewResult'):
        return None
    if viewObject.ViewResult.strip() == '':
        return None
    points = getPoints(viewObject.ViewResult)
    xmin = 9999999999999999
    xmax = -9999999999999999
    ymin = 9999999999999999
    ymax = -9999999999999999
    for p in points:
        if p[0] < xmin:
            xmin = p[0]
        if p[0] > xmax:
            xmax = p[0]
        if p[1] < ymin:
            ymin = p[1]
        if p[1] > ymax:
            ymax = p[1]
    x = xmin + (xmax-xmin)/2
    y = ymin + (ymax-ymin)/2
    return (x,y)


def getPageDimensions(pageObject):
    "returns the (x,y) dimensions of a page"
    if not pageObject.PageResult:
        return None
    if not os.path.exists(pageObject.PageResult):
        return None
    f = open(pageObject.PageResult)
    svg = f.read()
    f.close()
    svg = svg.replace("\n","   ")
    width = re.findall("<svg.*?width=\"(.*?)\".*?>",svg)
    if width:
        width = float(width[0].strip("mm").strip("px"))
    else:
        return None
    height = re.findall("<svg.*?height=\"(.*?)\".*?>",svg)
    if height:
        height = float(height[0].strip("mm").strip("px"))
    else:
        return None
    return (width,height)


class CenterView:
    "Defines the CenterView command"
    
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/centerView.svg' , 
            'MenuText': 'Centers a view on its page', 
            'ToolTip': 'Centers a view on its page'
            } 
            
    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        for obj in sel:
            done = False
            if obj.isDerivedFrom("Drawing::FeatureView"):
                for parent in obj.InList:
                    if parent.isDerivedFrom("Drawing::FeaturePage"):
                        pagedims = getPageDimensions(parent)
                        if pagedims:
                            viewcenter = getCenterPoint(obj)
                            if viewcenter:
                                debugPrint( 2, "current center point: %3.3f, %3.3f" % viewcenter )
                                debugPrint( 2, "page center: %3.3f, %3.3f" % (pagedims[0]/2, pagedims[1]/2) )
                                dx = pagedims[0]/2 - viewcenter[0]
                                dy = pagedims[1]/2 - viewcenter[1]
                                debugPrint( 2, "delta: %3.3f, %3.3f" % (dx, dy) )
                                FreeCAD.ActiveDocument.openTransaction("Center View")
                                obj.X = obj.X+dx
                                obj.Y = obj.Y+dy
                                FreeCAD.ActiveDocument.commitTransaction()
                                done = True
            if not done:
                FreeCAD.Console.PrintError("Unable to move view "+obj.Label+"\n")
        FreeCAD.ActiveDocument.recompute()
        

FreeCADGui.addCommand('dd_centerView', CenterView())


    
