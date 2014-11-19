# -*- coding: utf-8 -*-

'''
Library to parse XML codes such as those used for the FreeCAD view result, as to get graphics elements out.
'''

# Future Work,
#  - replace custom XML parser lib with an established svg library ...
#


import numpy
from numpy import sin, cos, dot
import Svg_tools

def findOffset( text, subtext, p_start ):
    p = text.find(subtext, p_start)
    return p + len(subtext) if p > -1 else -1

def splitMultiSep( text, seperators ):
    parts = []
    i = 0
    j = 0
    while i < len(text):
        for s in seperators:
            if text[i:i+len(s)] == s:
                parts.append( text[j:i] )
                i = i + len(s)
                j = i
                continue
        i = i + 1
    if j < len(text):
        parts.append( text[j:] )
    return parts
                      

def extractParms( text, p_start, startText, sep, endText ):
    p1 = findOffset( text, startText, p_start)
    assert p1 > -1
    p2 = text.find( endText , p1 )
    assert p2 > p1
    return [ part for part in splitMultiSep(text[p1:p2], sep) if len(part) > 0 ]

def findClose_sub(text, subText, pStart):
    p = text.find(subText, pStart)
    return p if p <> -1 else len(text)-1 #if p == -1 then broken XML

def findClose(text, closingOptions, pStart):
    return min( [ findClose_sub(text, subText, pStart) for subText in closingOptions ] )

class SvgXMLTreeNode:
    
    def __init__(self, XML, pStart, parent=None):
        self.XML = XML
        self.pStart = pStart
        self.parent = parent
        self.children = []
        assert XML[pStart] == '<'
        pNextElement = XML.find('<', pStart + 1)
        pClose = findClose( XML, ['/','-->'], pStart)
        while pNextElement > -1 and pNextElement +1 < pClose: #+1 to handle '</svg>' styled close tags
            child = SvgXMLTreeNode( XML, pNextElement, self )
            self.children.append(child)
            pNextElement = XML.find('<', child.pEnd)
            pClose = findClose(XML, ['/','-->'], child.pEnd)
        self.pClose = pClose
        self.pEnd = findClose(XML, '>', pClose)+1
        if len(self.children) == 0:
            if XML[ pClose-1 ] == '<':
                self.header = XML[ pStart:pClose-1 ]
                self.footer = XML[ pClose-1:self.pEnd ]
            else:
                self.header = XML[ pStart:pClose ]
                self.footer = XML[ pClose:self.pEnd ]
        else:
            self.header = XML[ pStart: self.children[0].pStart ]
            self.footer = XML[ self.children[-1].pEnd : self.pEnd ]
        self.header = self.header.replace('\n','')
        self.footer = self.footer.replace('\n','')
        self.tag = self.header.split()[0][1:]
        if self.tag.startswith('!--'): #comment special case
            self.tag = '!--'
        self.parms = {}
        h = self.header
        p = h.find('=')
        while p > -1:
            i = p-1
            key = ''
            while key == '' or h[i] <> ' ':
                if h[i] <> ' ':
                    key = h[i] + key
                i = i - 1
            p1 = h.find('"', p)
            p2 = h.find('"', p1+1)
            self.parms[key] = h[p1+1:p2]
            p = self.header.find('=', p+1)
        #print(self.parms)

    def prettify(self, indent='', indentIncrease='  '):
        if len(self.children) == 0:
            return indent + self.header + self.footer
        else:
            return indent + self.header + '\n' + '\n'.join([c.prettify( indent+indentIncrease ) for c in self.children]) + '\n' + indent + self.footer

    def __repr__(self):
        return self.prettify()

    def applyTransforms(self, x, y):
        R = numpy.eye(2)
        r_o = numpy.zeros(2)
        tx, ty = 0, 0
        sx, sy = 1.0, 1.0
        if 'transform=' in self.header:
            if 'rotate(' in self.header:
                rotateDegrees, rx, ry = map(float, extractParms(self.header, 0, 'rotate(', ', ', ')'))
                rads = numpy.pi * rotateDegrees / 180
                R = numpy.array([ [ cos(rads), -sin(rads)], [ sin(rads), cos(rads)] ])
                r_o = numpy.array([ rx, ry])
            if 'translate(' in self.header:
                tx, ty = map(float, extractParms(self.header, 0, 'translate(', ', ', ')'))
            if 'scale(' in self.header:
                sx, sy = map(float, extractParms(self.header, 0, 'scale(', ', ', ')'))
        p = numpy.array( [sx*x + tx, sy*y + ty] )
        point = dot(R, p-r_o) +r_o
        if self.parent <> None:
            return self.parent.applyTransforms(*point)
        else:
            return point[0], point[1]

    def scaling(self):
        sx = 1.0
        if 'scale(' in self.header:
            sx = map(float, extractParms(self.header, 0, 'scale(', ',', ')'))[0]
        if len(self.children) == 1:
            sx_child = self.children[0].scaling()
        else:
            sx_child = 1.0
        return sx * sx_child
            

    def calculate_local_snap_points(self):
        '''
        SVG reference http://www.w3.org/TR/SVG/paths.html
        '''

        if hasattr(self, 'LSP_linearDimensioning'):
            return
        self.LSP_linearDimensioning = [] #LSP local snap points
        self.LSP_circularDimensioning = []
        self.LSP_textAnchors = []
        if self.tag == 'path':
            #print(self.XML)
            dParmsXML = self.parms['d']
            #<spacing corrections>
            i = 0
            while i < len(dParmsXML)-1:
                if dParmsXML[i] in 'MLACQ,' and dParmsXML[i+1] in '-.0123456789':
                    dParmsXML = dParmsXML[:i+1] + ' ' + dParmsXML[i+1:]
                i = i + 1
            #</spacing corrections>
            parms = dParmsXML.replace(',',' ').strip().split()
            j = 0
            fitData = []
            while j < len(parms):
                #print(parms[j:])
                if parms[j] == 'M' or parms[j] == 'L':
                    self.LSP_linearDimensioning.append( self.applyTransforms( float(parms[j+1]), float(parms[j+2]) ))
                    fitData.append( [[ float(parms[j+1]), float(parms[j+2])]] )
                    j = j + 3
                elif parms[j] == 'A':
                    # The arc command begins with the x and y radius and ends with the ending point of the arc. 
                    # Between these are three other values: x axis rotation, large arc flag and sweep flag.
                    rX, rY, xRotation, largeArc, sweep, endX, endY = map(float, parms[j+1:j+1+7])
                    self.LSP_linearDimensioning.append( self.applyTransforms( endX, endY ))
                    if rX == rY: #then circle
                        pass # no idea how to find the centre of this circle.
                    j = j + 8
                elif parms[j] == 'C': #cubic Bézier curve 
                    #Draws a cubic Bézier curve from the current point to (x,y) using 
                    # (x1,y1) as the control point at the beginning of the curve and (x2,y2) as the control point at the end of the curve.
                    x1, y1, x2, y2, x, y = map(float, parms[j+1:j+1+6])
                    self.LSP_linearDimensioning.append( self.applyTransforms( x, y) )
                    fitData = fitData + [ [ [x1, y1], [x2, y2], [x, y] ] ]
                    j = j + 7
                elif parms[j] == 'Q': # quadratic Bézier curveto
                    # Draws a quadratic Bézier curve from the current point to (x,y) using (x1,y1) as the control point. 
                    #Q (uppercase) indicates that absolute coordinates will follow; 
                    #q (lowercase) indicates that relative coordinates will follow. 
                    #Multiple sets of coordinates may be specified to draw a polybézier. 
                    #At the end of the command, the new current point becomes the final (x,y) coordinate pair used in the polybézier.
                    x1, y1, x, y = map(float, parms[j+1:j+1+6])
                    self.LSP_linearDimensioning.append( self.applyTransforms( x, y) )
                    fitData = fitData + [ [ [x1, y1], [x, y] ] ]
                    j = j + 5
                else:
                    raise RuntimeError, 'unable to parse path "%s" with d parms %s' % (self.XML[self.pStart:self.pEnd], parms)
            if len(fitData) > 0: 
                cx, cy, r, r_error = Svg_tools.fitCircle_to_path(fitData)
                if r_error < 10**-4:
                    parent = self
                    while parent.parent <> None:
                        parent = parent.parent
                    self.parms['cx'] = cx
                    self.parms['cy'] = cy
                    self.parms['r'] = r * parent.scaling()
                    self.LSP_linearDimensioning.append(   self.applyTransforms( cx, cy ))
                    self.LSP_circularDimensioning.append( self.applyTransforms( cx, cy ))
        elif self.tag == 'circle':
            cx = float( self.parms['cx'] )
            cy = float( self.parms['cy'] )
            r =  float( self.parms['r'] )
            self.LSP_linearDimensioning.append(   self.applyTransforms( cx, cy ))
            self.LSP_circularDimensioning.append( self.applyTransforms( cx, cy ))
        elif self.tag == 'text':
            x = float( self.parms['x'] )
            y = float( self.parms['y'] )
            self.LSP_textAnchors.append( self.applyTransforms( x, y ) )

    def getAllElements(self):
        return [self] + sum([c.getAllElements() for c in self.children],[])

    def linearDimensioningSnapPoints(self):
        self.calculate_local_snap_points()
        allPoints = self.LSP_linearDimensioning + sum([c.linearDimensioningSnapPoints() for c in self.children], [])
        uniquePoints = []
        for p in allPoints:
            if not p in uniquePoints:
                uniquePoints.append(p)
        return uniquePoints

    def circularDimensioningSnapPoints(self):
        self.calculate_local_snap_points()
        allPoints = self.LSP_circularDimensioning + sum([c.circularDimensioningSnapPoints() for c in self.children], [])
        uniquePoints = []
        for p in allPoints:
            if not p in uniquePoints:
                uniquePoints.append(p)
        return uniquePoints

    def textAnchorSnapPoints(self):
        self.calculate_local_snap_points()
        allPoints = self.LSP_textAnchors + sum([c.textAnchorSnapPoints() for c in self.children], [])
        uniquePoints = []
        for p in allPoints:
            if not p in uniquePoints:
                uniquePoints.append(p)
        return uniquePoints


if __name__ == "__main__":
    print('Testing XMLlib')
    XML = '''<svg id="Ortho_0_1" width="640" height="480"
   transform="rotate(90,122.43,123.757) translate(122.43,123.757) scale(1.5,1.5)"
  >
<g   stroke="rgb(0, 0, 0)"
   stroke-width="0.233333"
   stroke-linecap="butt"
   stroke-linejoin="miter"
   fill="none"
   transform="scale(1,-1)"
  >
<path id= "1" d=" M 65.9612 -59.6792 L -56.2041 -59.6792 " />
<path d="M-56.2041 -59.6792 A4.2 4.2 0 0 0 -60.4041 -55.4792" /><path id= "3" d=" M 65.9612 49.7729 L 65.9612 -59.6792 " />
<path id= "4" d=" M -60.4041 -55.4792 L -60.4041 49.7729 " />
<path id= "5" d=" M -60.4041 49.7729 L 65.9612 49.7729 " />
<circle cx ="22.2287" cy ="-15.2218" r ="13.8651" /><!--Comment-->
<path id= "7" d="M18,0 L17.9499,-4.32955e-16  L17.8019,-4.00111e-16  L17.5637,-3.47203e-16  L17.247,-2.76885e-16  L16.8678,-1.92683e-16  L16.445,-9.88191e-17  L16,-5.43852e-32  L15.555,9.88191e-17  L15.1322,1.92683e-16  L14.753,2.76885e-16  L14.4363,3.47203e-16  L14.1981,4.00111e-16  L14.0501,4.32955e-16  L14,4.44089e-16 " />
<path d="M12.7,-53.35 C13.0276,-53.3497 13.3353,-53.4484 13.5837,-53.6066  C13.8332,-53.7643 14.0231,-53.9807 14.1457,-54.2047  C14.4256,-54.721 14.41,-55.3038 14.1502,-55.787  C14.0319,-56.0053 13.8546,-56.213 13.6163,-56.3722  C13.3789,-56.5307 13.0795,-56.6413 12.7378,-56.6496  C12.3961,-56.6571 12.0892,-56.5598 11.8429,-56.4099  C11.5956,-56.2597 11.4083,-56.0565 11.282,-55.8436  C11.0014,-55.3672 10.9667,-54.7868 11.2231,-54.2642  C11.3401,-54.0279 11.5293,-53.7969 11.7844,-53.6273  C12.0382,-53.4574 12.3575,-53.3497 12.7,-53.35 " />
</g>
<text x="50" y="-60" fill="blue" style="font-size:8" transform="rotate(0.000000 50,-60)">256.426</text>
</svg>'''
    print('parsing')
    print(XML)

    svg = SvgXMLTreeNode(XML,0)
    print(svg)

    import sys
    from PySide import QtGui, QtCore, QtSvg
    app = QtGui.QApplication(sys.argv)
    width = 640
    height = 480

    graphicsScene = QtGui.QGraphicsScene(0,0,width,height)
    graphicsScene.addText("XMLlib.py test.")
    orthoViews = []
    def addOrthoView( XML ):
        o1 = QtSvg.QGraphicsSvgItem()
        o1Renderer = QtSvg.QSvgRenderer()
        o1Renderer.load( QtCore.QByteArray( XML ))
        o1.setSharedRenderer( o1Renderer )
        graphicsScene.addItem( o1 )
        orthoViews.append([o1, o1Renderer, XML]) #protect o1 and o1Renderer against garbage collector
    addOrthoView(XML)
    view = QtGui.QGraphicsView(graphicsScene)
    view.show()

    for x,y in svg.linearDimensioningSnapPoints():
        graphicsScene.addEllipse( x-5, y-5, 10, 10, QtGui.QPen(QtGui.QColor(0,255,0)), QtGui.QBrush(QtGui.QColor(0,155,0))) 
    for x,y in svg.circularDimensioningSnapPoints():
        graphicsScene.addEllipse( x-6, y-6, 12, 12, QtGui.QPen(QtGui.QColor(255,0,0)), QtGui.QBrush(QtGui.QColor(127,0,0))) 
    for x,y in svg.textAnchorSnapPoints():
        graphicsScene.addEllipse( x-4, y-4, 8, 8, QtGui.QPen(QtGui.QColor(0,0,255)), QtGui.QBrush(QtGui.QColor(0,0,127))) 

    sys.exit(app.exec_())
