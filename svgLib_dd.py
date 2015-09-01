# This Python file uses the following encoding: utf-8
import sys, numpy
from PySide import QtGui, QtSvg, QtCore
from XMLlib import SvgXMLTreeNode
from circleLib import fitCircle_to_path, findCircularArcCentrePoint, pointsAlongCircularArc


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
        self.text = unicode(xml[ p_header_end+1:-len('</text>') ])
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
            self.rotation = float(t[t.find('rotate(')+len('rotate('):].split()[0])
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




class svgPath:
    #https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d
    def __init__( self, element):
        assert isinstance(element, SvgXMLTreeNode)
        self.points = []
        self.lines = []
        self.arcs = []
        self.bezierCurves = []
        dParmsXML_org = element.parms['d']
        #<spacing corrections>
        dParmsXML = ''
        for a,b in zip(dParmsXML_org[:-1], dParmsXML_org[1:]):
            if a in 'MmLlACcQZzHhVv,' and b in '-.0123456789':
                dParmsXML = dParmsXML + a + ' '
            else:
                dParmsXML = dParmsXML + a
        dParmsXML = dParmsXML + b
        parms = dParmsXML.replace(',',' ').strip().split()
        _pen_x = 0
        _pen_y = 0
        j = 0
        pathDescriptor = None
        while j < len(parms):
            #print(parms[j:])
            if parms[j] in list('MmLlACcQZzHhVv,'):
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
                self.points.append( svgPathPoint( _pen_x, _pen_y, pen_x, pen_y ) )
                j = j + 3   
                     
            elif parms[j] in ['L','l','Z','z']:
                if  parms[j] == 'L' or parms[j] == 'l':
                    if parms[j] == 'L':
                        _end_x, _end_y = float(parms[j+1]), float(parms[j+2])
                    else:
                        _end_x = _pen_x + float(parms[j+1])
                        _end_y = _pen_y + float(parms[j+2])
                    end_x, end_y = element.applyTransforms( _end_x, _end_y )
                    self.points.append( svgPathPoint( _end_x, _end_y, end_x, end_y ) )
                    j = j + 3
                else: #parms[j] == 'Z':
                    _end_x, _end_y = _path_start_x , _path_start_y
                    end_x, end_y = path_start_x , path_start_y
                    j = j + 1
                self.lines.append( svgPathLine( pen_x, pen_y, end_x, end_y ) )
                _pen_x, _pen_y = _end_x, _end_y
                pen_x, pen_y = end_x, end_y

            elif parms[j] == 'A':
                # The arc command begins with the x and y radius and ends with the ending point of the arc. 
                # Between these are three other values: x axis rotation, large arc flag and sweep flag.
                rX, rY, xRotation, largeArc, sweep, _end_x, _end_y = map( float, parms[j+1:j+1 + 7] )
                end_x, end_y = element.applyTransforms( _end_x, _end_y )
                self.points.append( svgPathPoint(_end_x, _end_y, end_x, end_y) )
                self.arcs.append( svgPathArc( element, _pen_x, _pen_y,  rX, rY, xRotation, largeArc, sweep, _end_x, _end_y ) )
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
                self.bezierCurves.append( svgPathBezierCurve(P) )
                end_x, end_y = P[-1]
                self.points.append(  svgPathPoint(_end_x, _end_y, end_x, end_y) )
                
            else:
                raise RuntimeError, 'unable to parse path "%s" with d parms %s' % (element.XML[element.pStart: element.pEnd], parms)


class svgPathPoint:
    def __init__(self, _x, _y, x, y): #keeping transforms outside class as to prevent multiple transformations ...
        self._x = _x
        self._y = _y 
        self.x = x
        self.y = y

class svgPathLine:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def midPoint(self):
        return (self.x1 + self.x2)/2, (self.y1 + self.y2)/2

class svgPathArc:
    def __init__(self, element, _pen_x, _pen_y, rX, rY, xRotation, largeArc, sweep, _end_x, _end_y ):
        self.element, self._pen_x, self._pen_y, self.rX, self.rY, self.xRotation, self.largeArc, self.sweep, self._end_x, self._end_y = element, _pen_x, _pen_y, rX, rY, xRotation, largeArc, sweep, _end_x, _end_y
        self.circular = False # and not eliptical
        if rX == rY:
            _c_x, _c_y = findCircularArcCentrePoint( self.rX, self._pen_x, self._pen_y, self._end_x, self._end_y, self.largeArc==1, self.sweep==1 ) #do in untranformed co-ordinates as to preserve sweep flag
            if not numpy.isnan(_c_x): 
                self.circular = True
                self.c_x, self.c_y = element.applyTransforms( _c_x, _c_y )
                self.r = rX
    def svgPath( self ):
        element, _pen_x, _pen_y, rX, rY, xRotation, largeArc, sweep, _end_x, _end_y = self.element, self._pen_x, self._pen_y, self.rX, self.rY, self.xRotation, self.largeArc, self.sweep, self._end_x, self._end_y
        assert rX == rY
        path = QtGui.QPainterPath(QtCore.QPointF( * element.applyTransforms(_pen_x, _pen_y ) ) )
        #path.arcTo(c_x - r, c_y -r , 2*r, 2*r, angle_1, angle_CCW) #dont know what is up with this function so trying something else.
        for _p in pointsAlongCircularArc(self.rX, _pen_x, _pen_y, _end_x, _end_y, largeArc==1, sweep==1, noPoints=12):
            path.lineTo(* element.applyTransforms(*_p) )
        return path

class svgPathBezierCurve:
    def __init__(self, P):
        self.P = P
    def fitCircle( self ):
        'returns x, y, r, r_error'
        return fitCircle_to_path([self.P])
    def svgPath( self ):
        P = self.P
        path = QtGui.QPainterPath(QtCore.QPointF(*P[0]))
        if len(P) == 4:
            path.cubicTo( QtCore.QPointF(*P[1]), QtCore.QPointF(*P[2]), QtCore.QPointF(*P[3]) )
        else:
            path.quadTo( QtCore.QPointF(*P[1]), QtCore.QPointF(*P[2]) )
        return path


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


