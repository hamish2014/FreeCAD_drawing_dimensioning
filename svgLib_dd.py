# This Python file uses the following encoding: utf-8
import sys, numpy, copy
from PySide import QtGui, QtSvg, QtCore
from XMLlib import SvgXMLTreeNode
from circleLib import fitCircle_to_path, findCircularArcCentrePoint, pointsAlongCircularArc, fitCircle, arccos2
from numpy import arctan2, pi, linspace, dot, sin, cos, array, cross
from numpy.linalg import norm

try:
    import FreeCAD
    def warningPrintFun( warningMsg ):
        FreeCAD.Console.PrintWarning(warningMsg + '\n')
except ImportError:
    def warningPrintFun( warningMsg ):
        print(warningMsg)
def printWarning(level, msg):
    if level <= printWarning.level:
        warningPrintFun( msg )
printWarning.level = 2

class SvgTextRenderer:
    def __init__(self, font_family='inherit', font_size='inherit', fill='rgb(0,0,0)'):
        self.font_family = font_family
        self.font_size = font_size
        self.fill = fill
    def __call__(self, x, y, text, text_anchor='inherit', rotation=None):
        '''
        text_anchor = start | middle | end | inherit
        rotation is in degress, and is done about x,y
        '''
        try:
            XML = '''<text x="%f" y="%f" font-family="%s" font-size="%s" fill="%s" text-anchor="%s" %s >%s</text>'''  % (  x, y, self.font_family, self.font_size,  self.fill, text_anchor, 'transform="rotate(%f %f,%f)"' % (rotation,x,y) if rotation <> None else '', text )
        except UnicodeDecodeError:
            text_utf8 = unicode( text, 'utf8' )
            XML = '''<text x="%f" y="%f" font-family="%s" font-size="%s" fill="%s" text-anchor="%s" %s >%s</text>'''  % (  x, y, self.font_family, self.font_size,  self.fill, text_anchor, 'transform="rotate(%f %f,%f)"' % (rotation,x,y) if rotation <> None else '', text_utf8 )
        return XML
    def __repr__(self):
        return '<svgLib_dd.SvgTextRenderer family="%s" font_size="%s" fill="%s">' % (self.font_family, self.font_size, self.fill )

class SvgTextParser:
    def __init__(self, xml):
        p_header_end = xml.find('>') 
        self.header = xml[:p_header_end]
        try:
            self.text = unicode(xml[ p_header_end+1:-len('</text>') ],'utf8')
        except TypeError:
            self.text = unicode(xml[ p_header_end+1:-len('</text>') ])
        #import FreeCAD
        #FreeCAD.Console.PrintMessage(self.text)
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
        self.x = float(self.parms['x'])
        self.y = float(self.parms['y'])
        self.font_family = self.parms.get('font-family', 'inherit')
        self.font_size = self.parms.get('font-size','inherit')
        if self.parms.has_key('style'): #for backwards compadiability
            self.font_size = self.parms['style'][len('font-size:'):]
        self.fill = self.parms.get('fill','rgb(0,0,0)')
        self.transform = self.parms.get('transform')
        if self.transform <> None:
            t = self.transform
            if 'rotate(' in t:
                self.rotation = float(t[t.find('rotate(')+len('rotate('):].split()[0])
            else:
                self.rotation = 0
        else:
            self.rotation = 0
        self.text_anchor = self.parms.get('text-anchor','inherit')
    def toXML(self):
        XML = '''<text x="%f" y="%f" font-family="%s" font-size="%s" fill="%s" text-anchor="%s" %s >%s</text>'''  % (  self.x, self.y, self.font_family, self.font_size,  self.fill, self.text_anchor, 'transform="rotate(%f %f,%f)"' % (self.rotation,self.x,self.y) if self.rotation <> 0 else '', self.text )
        return XML
    def convertUnits(self,value):
        '''http://www.w3.org/TR/SVG/coords.html#Units
        units do not seem to have on font size though:
        8cm == 8pt == 8blah?'''
        i = 0
        while i < len(value) and value[i] in '0123456789.':
            i = i + 1
        v = value[:i]
        factor = 1.0
        return float(v)*factor

    def textRect(self):
        sizeInPoints = self.convertUnits(self.font_size.strip())
        font = QtGui.QFont(self.font_family, sizeInPoints)
        fm = QtGui.QFontMetrics(font)
        return fm.boundingRect(self.text)

    def width(self):
        'return width of untransformed text'
        return self.textRect().width() *0.63
    def height(self):
        'height of untransformed text'
        return self.textRect().height() *0.6

    def __unicode__(self):
        return u'<svgLib_dd.SvgTextParser family="%s" font_size="%s" fill="%s" rotation="%f" text="%s">' % (self.font_family, self.font_size, self.fill, self.rotation, self.text )

    def __repr__(self):
        return u'<svgLib_dd.SvgTextParser family="%s" font_size="%s" fill="%s" rotation="%f">' % (self.font_family, self.font_size, self.fill, self.rotation )




class SvgPath:
    #https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d
    def __init__( self, element):
        assert isinstance(element, SvgXMLTreeNode)
        self.points = []
        self.lines = []
        self.arcs = []
        self.bezierCurves = []
        self.elements = [] # for preserving order of path elements, pen movements are not considered elements since they do not result in a direct visual effect
        dParmsXML_org = element.parms['d'].replace(',',' ')
        #<spacing corrections>
        dParmsXML = ''
        for a,b in zip(dParmsXML_org[:-1], dParmsXML_org[1:]):
            if a in 'MmLlAaCcQZzHhVv':
                if len(dParmsXML) > 0 and dParmsXML[-1] <> ' ':
                    dParmsXML = dParmsXML + ' '
                dParmsXML = dParmsXML + a
                if b <> ' ':
                    dParmsXML = dParmsXML + ' '
            elif a <> ' ' and a <> 'e' and b == '-':
                dParmsXML = dParmsXML + a + ' '
            else:
                dParmsXML = dParmsXML + a
        if b in 'MmLlAaCcQZzHhVv' and dParmsXML[-1] <> ' ':
            dParmsXML = dParmsXML + ' '
        dParmsXML = dParmsXML + b
        #<spacing corrections>
        parms = dParmsXML.replace(',',' ').strip().split()
        _pen_x = 0
        _pen_y = 0
        j = 0
        pathDescriptor = None
        while j < len(parms):
            #print(parms[j:])
            if parms[j] in list('MmLlAaCcQZzHhVv,'):
                pathDescriptor = parms[j]
            else: #using previous pathDescriptor
                if pathDescriptor == None:
                    raise RuntimeError, 'pathDescriptor == None! unable to parse path "%s" with d parms %s' % (element.XML[element.pStart: element.pEnd], parms)
                parms.insert(j, pathDescriptor.replace('m','l').replace('M','L'))
                
            if parms[j] == 'M' or parms[j] == 'm':
                if parms[j] == 'M':
                    _pen_x, _pen_y = float(parms[j+1]), float(parms[j+2])
                else: #m
                    _pen_x = _pen_x + float(parms[j+1])
                    _pen_y = _pen_y + float(parms[j+2])
                pen_x, pen_y = element.applyTransforms( _pen_x, _pen_y )
                _path_start_x , _path_start_y = _pen_x, _pen_y
                path_start_x , path_start_y = pen_x, pen_y
                self.points.append( SvgPathPoint( _pen_x, _pen_y, pen_x, pen_y ) )
                j = j + 3   
                     
            elif parms[j] in 'LlZzVvHh':
                if  parms[j] in 'Ll':
                    if parms[j] == 'L':
                        _end_x, _end_y = float(parms[j+1]), float(parms[j+2])
                    else:
                        _end_x = _pen_x + float(parms[j+1])
                        _end_y = _pen_y + float(parms[j+2])
                    end_x, end_y = element.applyTransforms( _end_x, _end_y )
                    self.points.append( SvgPathPoint( _end_x, _end_y, end_x, end_y ) )
                    j = j + 3
                elif parms[j] in  'VvHh':
                    if parms[j] == 'V':
                        _end_x, _end_y = _pen_x, float(parms[j+1])
                    elif parms[j] == 'v':
                        _end_x = _pen_x
                        _end_y = _pen_y + float(parms[j+1])
                    elif parms[j] == 'H':
                        _end_x, _end_y = float(parms[j+1]), _pen_y
                    elif parms[j] == 'h':
                        _end_x = _pen_x + float(parms[j+1])
                        _end_y = _pen_y 
                    end_x, end_y = element.applyTransforms( _end_x, _end_y )
                    self.points.append( SvgPathPoint( _end_x, _end_y, end_x, end_y ) )
                    j = j + 2
                else: #parms[j] == 'Z':
                    _end_x, _end_y = _path_start_x , _path_start_y
                    end_x, end_y = path_start_x , path_start_y
                    j = j + 1
                self.lines.append( SvgPathLine( pen_x, pen_y, end_x, end_y ) )
                self.elements.append( self.lines[-1] )
                _pen_x, _pen_y = _end_x, _end_y
                pen_x, pen_y = end_x, end_y

            elif parms[j] == 'A' or parms[j] == 'a':
                # The arc command begins with the x and y radius and ends with the ending point of the arc. 
                # Between these are three other values: x axis rotation, large arc flag and sweep flag.
                rX, rY, xRotation, largeArc, sweep, _end_x, _end_y = map( float, parms[j+1:j+1 + 7] )
                #print(_end_x, _end_y)
                if parms[j] == 'a':
                    _end_x = _pen_x + _end_x
                    _end_y = _pen_y + _end_y
                    #print(_end_x, _end_y)
                end_x, end_y = element.applyTransforms( _end_x, _end_y )
                if not ( _pen_x == _end_x and _pen_y == _end_y ) and rX <> 0 and rY <> 0:
                    self.points.append( SvgPathPoint(_end_x, _end_y, end_x, end_y) )
                    try:
                        self.arcs.append( SvgPathArc( element, _pen_x, _pen_y,  rX, rY, xRotation, largeArc, sweep, _end_x, _end_y ) )
                        self.elements.append(self.arcs[-1])
                    except SvgParseError, msg:
                        printWarning( 2, 'failed to parse arc: msg %s' % msg )
                _pen_x, _pen_y = _end_x, _end_y
                pen_x, pen_y = end_x, end_y
                j = j + 8

            elif parms[j] == 'C' or parms[j] == 'c' or parms[j] =='Q': #Bézier curve 
                if parms[j] == 'C' or parms[j] == 'c':
                    #cubic Bézier curve from the current point to (x,y) using 
                    # (x1,y1) as the control point at the beginning of the curve and (x2,y2) as the control point at the end of the curve.
                    if parms[j] == 'C':
                        _x1, _y1, _x2, _y2, _end_x, _end_y = map( float, parms[j+1:j+1 + 6] ) 
                    else: #parms[j] == 'c':
                        _x1, _y1, _x2, _y2, _end_x, _end_y = numpy.array(map( float, parms[j+1:j+1 + 6] )) + numpy.array([_pen_x,_pen_y]*3)
                    P = [ [pen_x, pen_y], element.applyTransforms(_x1, _y1), element.applyTransforms(_x2, _y2), element.applyTransforms(_end_x, _end_y) ]
                    j = j + 7
                elif parms[j] == 'Q': # quadratic Bézier curve from the current point to (x,y) using (x1,y1) as the control point. 
                    # Q (uppercase) indicates that absolute coordinates will follow; 
                    # q (lowercase) indicates that relative coordinates will follow. 
                    # Multiple sets of coordinates may be specified to draw a polybézier. 
                    # At the end of the command, the new current point becomes the final (x,y) coordinate pair used in the polybézier.
                    _x1, _y1, _end_x, _end_y = map( float, parms[j+1:j+1 + 4] ) 
                    j = j + 5
                    P = [ [pen_x, pen_y], element.applyTransforms(_x1, _y1), element.applyTransforms(_end_x, _end_y) ]
                self.bezierCurves.append( SvgPathBezierCurve(P) )
                self.elements.append(self.bezierCurves[-1])
                end_x, end_y = P[-1]
                self.points.append(  SvgPathPoint(_end_x, _end_y, end_x, end_y) )
                
            else:
                raise RuntimeError, 'unable to parse path "%s" with d parms %s' % (element.XML[element.pStart: element.pEnd], parms)


class SvgPathPoint:
    def __init__(self, _x, _y, x, y): #keeping transforms outside class as to prevent multiple transformations ...
        self._x = _x
        self._y = _y 
        self.x = x
        self.y = y

class SvgPathLine:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def midPoint(self):
        return (self.x1 + self.x2)/2, (self.y1 + self.y2)/2

class SvgParseError(Exception):
    pass

class SvgPathArc:
    '''
    http://www.w3.org/TR/SVG/paths.html#PathDataEllipticalArcCommands
    #seems to be more accurate then https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d#Arcto

    The elliptical arc command draws a section of an ellipse which meets the following constraints:

    -  the arc starts at the current point
    -  the arc ends at point (x, y)
    -  the ellipse has the two radii (rx, ry)
    -  the x-axis of the ellipse is rotated by x-axis-rotation relative to the x-axis of the current coordinate system.

    For most situations, there are actually four different arcs (two different ellipses, each with two different arc sweeps) that satisfy these constraints. 
    large-arc-flag and sweep-flag indicate which one of the four arcs are drawn, as follows:

    Of the four candidate arc sweeps, two will represent an arc sweep of greater than or equal to 180 degrees (the "large-arc"), and two will represent an arc sweep of less than or equal to 180 degrees (the "small-arc"). 
    If large-arc-flag is '1', then one of the two larger arc sweeps will be chosen; otherwise, if large-arc-flag is '0', one of the smaller arc sweeps will be chosen.
    If sweep-flag is '1', then the arc will be drawn in a "positive-angle" direction (i.e., the ellipse formula x=cx+rx*cos(theta) and y=cy+ry*sin(theta) is evaluated such that theta starts at an angle corresponding to the current point and increases positively until the arc reaches (x,y)). 
    A value of 0 causes the arc to be drawn in a "negative-angle" direction (i.e., theta starts at an angle value corresponding to the current point and decreases until the arc reaches (x,y)).
    '''

    def __init__(self, element, _pen_x, _pen_y, rX, rY, xRotation, largeArc, sweep, _end_x, _end_y ):
        """
        3 coordinate systems
          circular coordinates - in this coordinate system, the elipse is circular and unrotated
          elements coordinates - circular coordinates * elipse transformation (x*rX and y*Ry, then rotate to generate the elipse)
          global coordinates - elements coordinates * upper element transformations
        """
        assert not ( _pen_x == _end_x and _pen_y == _end_y )
        assert rX <> 0
        assert rY <> 0
        self._pen_x = _pen_x
        self._pen_y = _pen_y
        self._end_x = _end_x
        self._end_y = _end_y
        self.scaling = element.scaling2() #scaling between element and global coordinates
        self.rX = rX #in elements coordinates
        self.rY = rY #in elements coordinates
        self.xRotation = xRotation
        self.largeArc = largeArc
        self.sweep = sweep
        #finding center in circular coordinates 
        # X = T_ellipse dot Y
        # where T_ellipse = [[c -s],[s, c]] dot [[ rX 0],[0 rY]], X is element coordinates, and Y is circular coordinates
        ##import FreeCAD
        ##FreeCAD.Console.PrintMessage( 'Xrotation %f\n' % (self.xRotation))
        c = cos( xRotation*pi/180)
        s = sin( xRotation*pi/180)
        T_ellipse = dot( array([[c,-s] ,[s,c]]), array([[ rX, 0], [0, rY] ]))
        self.T_ellipse = T_ellipse
        #FreeCAD.Console.PrintMessage( 'T %s\n' % (T))
        x1,y1 = numpy.linalg.solve(T_ellipse, [_pen_x, _pen_y])
        x2,y2 = numpy.linalg.solve(T_ellipse, [_end_x, _end_y])
        c_x_Y, c_y_Y = findCircularArcCentrePoint( 1, x1, y1, x2, y2, largeArc==1, sweep==1 )
        self.center_circular = array([c_x_Y, c_y_Y])
        #now determining dtheta in circular coordinates
        #a,b = 1,1
        c = ( ( x2-x1 )**2 + ( y2-y1 )**2 ) ** 0.5
        dtheta = arccos2( ( 1 + 1 - c**2 ) / ( 2 ) ) #cos rule
        #print(x2,x1,y2,y1,c)
        #print(dtheta)
        if not dtheta >= 0:
            raise SvgParseError, "dtheta not >=  0, dtheta %e. locals %s" % (dtheta, locals())
        if largeArc:
            dtheta = 2*pi - dtheta
        if not sweep: # If sweep-flag is '1', then the arc will be drawn in a "positive-angle" direction
            dtheta = -dtheta
        self.dtheta = dtheta
        self.theta_start =  arctan2( y1 - c_y_Y, x1 - c_x_Y)
        self.T_element, self.c_element = element.Transforms()
        #print(self.valueAt(0), element.applyTransforms(_pen_x, _pen_y))
        #print(self.valueAt(1), element.applyTransforms(_end_x, _end_y))
        self.startPoint = self.valueAt(0)
        self.endPoint = self.valueAt(1)
        self.center = self.applyTransforms( self.center_circular )
        self.circular = rX == rY
        if self.circular:
            self.r = rX

    def applyTransforms(self, p):
        'position in circular coordinates -> position in elements coordinates -> position in global coordinates'
        return dot( self.T_element, dot(self.T_ellipse, p) ) +  self.c_element
                 
    def valueAt(self, t):
        #position in circular coordinates
        theta = self.theta_start + t*self.dtheta
        p_c = self.center_circular + array([cos(theta), sin(theta)])
        return self.applyTransforms( p_c )
    def valueAt_element(self, t):
        theta = self.theta_start + t*self.dtheta
        p_c = self.center_circular + array([cos(theta), sin(theta)])
        return dot(self.T_ellipse, p_c )

    def length(self):
        if self.circular:
            return abs(self.dtheta) * self.rX * self.scaling
        else:
            raise NotImplementedError, "arc.length for ellipsoidal arcs not implemented"

    def tangentAt( self, t):
        offset = pi/2 if self.dtheta >= 0 else -pi/2
        theta =  self.theta_start + self.dtheta*t + offset
        p0_ = self.valueAt( t )
        p1_ = p0_ + array([cos(theta), sin(theta)])
        p0 = self.applyTransforms( p0_ )
        p1 = self.applyTransforms( p1_ )
        dP = p1 - p0
        dP = dP / norm(dP)
        return dP
    def t_of_position( self, pos ):
        pos_element = numpy.linalg.solve( self.T_element, pos - self.c_element )
        A = numpy.linalg.solve(self.T_ellipse, pos_element)
        B = self.center_circular
        C = B + array([cos(self.theta_start), sin(self.theta_start)])
        AB = (A - B) / norm(A-B)
        BC = C - B
        theta = arccos2(dot(AB,BC))
        D = array([ A[0] - B[0], A[1] - B[1], 0.0 ])
        E = array([ A[0] - C[0], A[1] - C[1], 0.0 ])
        F = cross(D,E)
        if F[2] < 0:
            theta = -theta
        #print(theta, self.dtheta, theta / self.dtheta )
        return theta / self.dtheta
    def flip( self):
        self.theta_start = self.theta_start + self.dtheta
        self.dtheta = -self.dtheta
        self.sweep = not self.sweep
        self._pen_x, self._pen_y, self._end_x, self._end_y = self._end_x, self._end_y, self._pen_x, self._pen_y
        self.startPoint = self.valueAt(0)
        self.endPoint = self.valueAt(1)
        self.center = self.applyTransforms( self.center_circular )

    def svg( self, strokeColor='blue', strokeWidth=0.3, fill= 'none'):
        transform_txt = 'matrix(%f %f %f %f %f %f)' % (
            self.T_element[0,0], self.T_element[0,1], self.T_element[1,0], self.T_element[1,1], self.c_element[0], self.c_element[1]
            )
        return '<path transform="%s" stroke = "%s" stroke-width = "%f" fill = "none" d = "M %f %f A %f %f %f %i %i %f %f"/>' % (
            transform_txt,
            strokeColor,
            strokeWidth / self.scaling,
            self._pen_x, self._pen_y,
            self.rX, self.rY,
            self.xRotation,
            self.largeArc,
            self.sweep,
            self._end_x, self._end_y,
            )

    def QPainterPath( self, n=12 ):
        path = QtGui.QPainterPath( QtCore.QPointF( *self.valueAt(0) ) )
        #path.arcTo #dont know what is up with this function so trying something else.
        for t in numpy.linspace(0,1,n)[1:]:
            path.lineTo(*self.valueAt(t))
        return path

    def dxfwrite_arc_parms(self, yT):
        'returns [ [radius=1.0, center=(0., 0.), startangle=0., endangle=360.], [...], ...]'
        x_c, y_c = self.applyTransforms(self.center_circular)
        y_c = yT(y_c)
        X = []
        Y = []
        for t in numpy.linspace(0, 1.0, 13):
            x, y = self.valueAt(t)
            X.append( x )
            Y.append( yT(y) )
        #end_x, end_y = element.applyTransforms(self._end_x, self._end_y)
        #import FreeCAD
        #FreeCAD.Console.PrintMessage( 'X %s pen_x %f end_x %f\n' % (X, pen_x, end_x))
        #FreeCAD.Console.PrintMessage( 'Y %s pen_y %f end_y %f\n' % (Y, pen_y, end_y))
        #for i in range(len(X) -1):
        #    drawing.add( dxf.line( (X[i], yT(Y[i])), (X[i+1],yT(Y[i+1]) ) ) )
        return dxfwrite_arc_parms( X, Y, x_c, y_c)
    def approximate_via_lines(self, n=12):
        X = []
        Y = []
        for t in numpy.linspace(0, 1.0, n):
            x, y = self.valueAt(t)
            X.append( x )
            Y.append( y )
        lines = []
        for i in range(len(X) -1):
            lines.append([ X[i], Y[i], X[i+1], Y[i+1] ])
        return lines
        


def arctanDegrees( dY, dX ):
    theta = arctan2( dY, dX ) / pi * 180
    return theta if theta >= 0 else theta + 360          

def dxfwrite_arc_parms( X, Y, x_c=None, y_c=None, n=12 ):
    #takes a list of points describe by X,Y and returns dxfwrite_arc_parms for the 1 or 2 arcs required to plot arcs
    if x_c == None:
        x_c, y_c, r, r_error = fitCircle(X,Y)
    else:
        r = fitCircle(X,Y)[2]
    ThetaStack = []
    Theta = [ arctanDegrees( Y[0] - y_c, X[0] - x_c) ]
    for x,y in zip(X[1:], Y[1:]):
        theta = arctanDegrees( y-y_c, x-x_c)
        dTheta = Theta[-1] - theta
        if abs(dTheta) > 360.0/n: #must have crossed either 0 or 360
            if Theta[-1] > 180: #then crossed 360
                ThetaStack.append( Theta + [360] )
                Theta = [0, theta ]
            else: #then crossed 0
                ThetaStack.append( Theta +   [0] )
                Theta = [360, theta ]
        else:
            Theta.append( theta )
    ThetaStack.append( Theta )
    args = []
    #import FreeCAD
    #FreeCAD.Console.PrintMessage( 'ThetaStack %s\n' % (ThetaStack) )
    for Theta in ThetaStack:
        if max(Theta) - min(Theta) > 10**-6:
            args.append( [r, (x_c, y_c), min(Theta), max(Theta)])
    return args

    
   

class SvgPathBezierCurve:
    def __init__(self, P):
        self.P = P
    def fitCircle( self ):
        'returns x, y, r, r_error'
        return fitCircle_to_path([self.P])
    def QPainterPath( self ):
        P = self.P
        path = QtGui.QPainterPath(QtCore.QPointF(*P[0]))
        if len(P) == 4:
            path.cubicTo( QtCore.QPointF(*P[1]), QtCore.QPointF(*P[2]), QtCore.QPointF(*P[3]) )
        else:
            path.quadTo( QtCore.QPointF(*P[1]), QtCore.QPointF(*P[2]) )
        return path
    def points_along_curve( self, no=12):
        T = linspace(0, 1, no)
        if len(self.P) == 4: #then cubic Bezier
            p0, p1, p2, p3 = self.P
            t0 =    T**0 * (1-T)**3
            t1 = 3* T**1 * (1-T)**2
            t2 = 3* T**2 * (1-T)**1
            t3 =    T**3 * (1-T)**0
            X = t0*p0[0] + t1*p1[0] + t2*p2[0] + t3*p3[0]
            Y = t0*p0[1] + t1*p1[1] + t2*p2[1] + t3*p3[1]
        if len(self.P) == 3: #then quadratic Bezier plot, https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B.C3.A9zier_curves
            #\mathbf{B}(t) = (1 - t)^{2}\mathbf{P}_0 + 2(1 - t)t\mathbf{P}_1 + t^{2}\mathbf{P}_2 \mbox{ , } t \in [0,1]. 
            p0, p1, p2 = self.P
            X = (1-T)**2*p0[0] + 2*(1-T)*T**p1[0] + T**2*p2[0]
            Y = (1-T)**2*p0[1] + 2*(1-T)*T**p1[1] + T**2*p2[1]
        return X, Y
    def dxfwrite_arc_parms(self, x_c, y_c, r):
        x1, y1 = self.P[0]
        x2, y2 = self.P[-1]
        x_c, y_c = self.c_x, self.c_y
        startangle = arctan2( y1 - y_c, x1 - x_c) / pi * 180
        endangle = arctan2( y2 - y_c, x2 - x_c) / pi * 180
        return r, (x_c, y_c), startangle, endangle


class SvgPolygon:
    def __init__(self, element):
        assert isinstance(element, SvgXMLTreeNode)
        self.points = []
        self.lines = []
        points_raw = map( float, element.parms['points'].replace(',',' ').split() )
        X = []
        Y = []
        for i in range(len(points_raw)/2):
            _x = points_raw[i*2]
            _y = points_raw[i*2 + 1]
            x, y =  element.applyTransforms( _x, _y )
            X.append(x)
            Y.append(y)
            self.points.append( SvgPathPoint( _x, _y, x, y ) )
        X.append(X[0])
        Y.append(Y[0])
        for i in range(len(X)-1):
            self.lines.append( SvgPathLine( X[i], Y[i], X[i+1], Y[i+1] ) )




if __name__ == '__main__':
    print('launching test app for svgLib_dd.py')
    textRender = SvgTextRenderer(font_family='Verdana', font_size='4.2pt', fill='rgb(0,255,0)')
    print(textRender)
    XML = textRender(1,2,'hello world')
    print(XML)
    text = SvgTextParser(XML)
    print(text)
    print(text.toXML())
    exit()

            
    class TestApp(QtGui.QWidget):
        ''' based on code from http://zetcode.com/gui/pysidetutorial/dialogs/'''
        def __init__(self):
            super(TestApp, self).__init__()
            self.textRenderer = SvgTextRenderer()
            self.initUI()
        
        def initUI(self):      

            vbox = QtGui.QVBoxLayout()

            btn = QtGui.QPushButton('Dialog', self)
            btn.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
            btn.move(20, 20)
            vbox.addWidget(btn)

            btn.clicked.connect(self.showDialog)
            
            self.lbl = QtGui.QLabel('Knowledge only matters', self)
            self.lbl.move(130, 20)
            vbox.addWidget(self.lbl)

        
            width = 250
            height = 180

            self.graphicsScene = QtGui.QGraphicsScene(0,0,width*0.8,height/2)
            self.dimPreview = QtSvg.QGraphicsSvgItem()
            self.dimSVGRenderer = QtSvg.QSvgRenderer()
            self.dimSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"></svg>''' % (width, height)) )
            self.dimPreview.setSharedRenderer( self.dimSVGRenderer )
            self.graphicsScene.addItem( self.dimPreview )
            self.graphicsView = QtGui.QGraphicsView( self.graphicsScene )
            vbox.addWidget( self.graphicsView )

            self.setLayout(vbox)          
            self.setGeometry(300, 300, width, height)
            self.setWindowTitle('Font dialog')
            self.show()
        
        def showDialog(self):

            font, ok = QtGui.QFontDialog.getFont()
            if ok:
                self.lbl.setFont(font)
                self.textRenderer.font_family = font.family()
                self.textRenderer.font_size = '%fpt' % font.pointSizeF()
                self.textRenderer.fill='rgb(255,0,0)'
                
                text = 'Knowledge only matters'
                XML = '''<svg width="180" height="120" > %s </svg> '''  % \
                      self.textRenderer(50,20, text)
                print(XML)
                self.dimSVGRenderer.load( QtCore.QByteArray( XML ) )
                self.dimPreview.update()

    app = QtGui.QApplication(sys.argv)
    ex = TestApp()
    sys.exit(app.exec_())


