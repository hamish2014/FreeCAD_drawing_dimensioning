# This Python file uses the following encoding: utf-8
'''
library for constructing dimension SVGs
'''


import numpy
from numpy import dot, pi, arctan2, sin, cos, arccos
from numpy.linalg import norm
from textSvg import SvgTextRenderer

def directionVector( A, B ):
    if norm(B-A) == 0:
        return numpy.array([0.0,0.0])
    else:
        return (B-A)/norm(B-A)

def dimensionSVG_trimLine(A,B,trimA, trimB):
    d = directionVector( A, B)
    return (A + d*trimA).tolist() + (B - d*trimB).tolist()

def rotate2D( v, angle ):
    return numpy.dot( [[ cos(angle), -sin(angle)],[ sin(angle), cos(angle)]], v)

def arrowHeadSVG( tipPos, d, L1, L2, W, clr='blue'):
    d2 = numpy.dot( [[ 0, -1],[ 1, 0]], d) #same as rotate2D( d, pi/2 )
    R = numpy.array( [d, d2]).transpose()
    p2 = numpy.dot( R, [ L1,    W/2.0 ]) + tipPos
    p3 = numpy.dot( R, [ L1+L2, 0     ]) + tipPos
    p4 = numpy.dot( R, [ L1,   -W/2.0 ]) + tipPos
    return '<polygon points="%f,%f %f,%f %f,%f %f,%f" style="fill:%s;stroke:%s;stroke-width:0" />' % (tipPos[0], tipPos[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1], clr, clr)


def dimensionText( V, formatStr, roundingDigit=6):
    s1 = (formatStr % V).rstrip('0').rstrip('.')
    Vrounded = numpy.round(V, roundingDigit)
    s2 = (formatStr % Vrounded).rstrip('0').rstrip('.')
    return s2 if len(s2) < len(s1) else s1

defaultTextRenderer = SvgTextRenderer(font_family='Verdana', font_size='5pt', fill="red")

def linearDimensionSVG( x1, y1, x2, y2, x3, y3, x4=None, y4=None, scale=1.0, textFormat='%3.3f',  gap_datum_points = 2, dimension_line_overshoot=1, arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5, lineColor='blue', textRenderer=defaultTextRenderer):
    lines = []
    p1 = numpy.array([ x1, y1 ])
    p2 = numpy.array([ x2, y2 ])
    p3 = numpy.array([ x3, y3 ])
    if min(x1,x2) <= x3 and x3 <= max(x1,x2):
        d = numpy.array([ 0, 1])
        textRotation = 0
    elif  min(y1,y2) <= y3 and y3 <= max(y1,y2):
        d = numpy.array([ 1, 0])
        textRotation = -90
    elif numpy.linalg.norm(p2 - p1) > 0:
        d = numpy.dot( [[ 0, -1],[ 1, 0]], directionVector(p1,p2))
        if abs( sum( numpy.sign(d) * numpy.sign( p3- (p1+p2)/2 ))) == 0:
            return None
        textRotation = numpy.arctan( (y2 - y1)/(x2 - x1))  / numpy.pi * 180
        #if textRotation <
    else:
        return None
    A = p1 + numpy.dot(p3-p1,d)*d
    B = p2 + numpy.dot(p3-p2,d)*d
    lines.append( dimensionSVG_trimLine( p1, A, gap_datum_points,-dimension_line_overshoot))
    lines.append( dimensionSVG_trimLine( p2, B, gap_datum_points,-dimension_line_overshoot))
    lines.append( A.tolist() +  B.tolist() )

    lineTemplate = '<line x1="%%f" y1="%%f" x2="%%f" y2="%%f" style="stroke:%s;stroke-width:%1.2f" />' % (lineColor, strokeWidth)
    lineXML = '\n'.join( lineTemplate % tuple(line) for line in lines )
    if x4 <> None and y4 <> None:
        v = numpy.linalg.norm(A-B)*scale
        textXML = textRenderer( x4, y4, dimensionText(v,textFormat), rotation=textRotation )
    else :
        textXML = ''
    distAB = numpy.linalg.norm(A-B)
    if distAB > 0:
        s = 1 if distAB > 2.5*(arrowL1 + arrowL2) else -1
        arrowXML = arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW, lineColor ) + \
            arrowHeadSVG( B, s*directionVector(B,A), arrowL1, arrowL2, arrowW, lineColor )
    else:
        arrowXML = ''
    XML = '''<%s  %s >
%s
%s
%s
</%s> ''' % ( svgTag, svgParms, lineXML, arrowXML, textXML, svgTag )
    return XML


def circularDimensionSVG( center_x, center_y, radius, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, text_x=None, text_y=None, textFormat='Ø%3.3f', centerPointDia = 1, arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5, dimScale=1.0, lineColor='blue', textRenderer=defaultTextRenderer):
    XML_body = [ ' <circle cx ="%f" cy ="%f" r="%f" stroke="none" fill="%s" /> ' % (center_x, center_y, centerPointDia*0.5, lineColor) ]
    #XML_body.append( '<circle cx="%f" cy="%f" r="%f" stroke="rgb(0,0,255)" stroke-width="%1.2f" fill="none" />' % (center_x, center_y, radius, strokeWidth) )
    if radialLine_x <> None and radialLine_y <> None:
        theta = numpy.arctan2( radialLine_y - center_y, radialLine_x - center_x )
        A = numpy.array([ center_x + radius*numpy.cos(theta) , center_y + radius*numpy.sin(theta) ])
        B = numpy.array([ center_x - radius*numpy.cos(theta) , center_y - radius*numpy.sin(theta) ])
        XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, B[0], B[1], lineColor, strokeWidth) )
        if radius > 0:
            s = 1 if radius > arrowL1 + arrowL2 + 0.5*centerPointDia else -1
            XML_body.append( arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW, lineColor ) )
            XML_body.append( arrowHeadSVG( B, s*directionVector(B,A), arrowL1, arrowL2, arrowW, lineColor ) )
        if tail_x <> None and tail_y <> None:
            XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, tail_x, radialLine_y, lineColor, strokeWidth) )
    if text_x <> None and text_y <> None:
        XML_body.append( textRenderer( text_x, text_y, dimensionText(2*radius*dimScale,textFormat) ))
        XML_body.append( '<!--%s-->' % (2*radius) )
        XML_body.append( '<!--%s-->' % (textFormat) )
    XML = '''<%s  %s >
%s
</%s> ''' % ( svgTag, svgParms, "\n".join(XML_body), svgTag )
    return XML

def radiusDimensionSVG( center_x, center_y, radius, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, text_x=None, text_y=None, textFormat='R%3.3f', centerPointDia = 1, arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5, dimScale=1.0, lineColor='blue', textRenderer=defaultTextRenderer):
    XML_body = [ ' <circle cx ="%f" cy ="%f" r="%f" stroke="none" fill="%s" /> ' % (center_x, center_y, centerPointDia*0.5, lineColor) ]
    if radialLine_x <> None and radialLine_y <> None:
        theta = numpy.arctan2( radialLine_y - center_y, radialLine_x - center_x )
        A = numpy.array([ center_x + radius*numpy.cos(theta) , center_y + radius*numpy.sin(theta) ])
        B = numpy.array([ center_x - radius*numpy.cos(theta) , center_y - radius*numpy.sin(theta) ])
        XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, center_x, center_y, lineColor, strokeWidth) )
        if radius > 0:
            s = 1 if radius > arrowL1 + arrowL2 + 0.5*centerPointDia else -1
            XML_body.append( arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW, lineColor ) )
        if tail_x <> None and tail_y <> None:
            XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, tail_x, radialLine_y, lineColor, strokeWidth) )
    if text_x <> None and text_y <> None:
        XML_body.append( textRenderer( text_x, text_y, dimensionText(radius*dimScale,textFormat)) )
        XML_body.append( '<!--%s-->' % (radius) )
        XML_body.append( '<!--%s-->' % (textFormat) )
    XML = '''<%s  %s >
%s
</%s> ''' % ( svgTag, svgParms, "\n".join(XML_body), svgTag )
    return XML


def noteCircleSVG( start_x, start_y,
                   radialLine_x=None, radialLine_y=None,
                   tail_x=None, tail_y=None,
                   textFormat='R%3.3f', centerPointDia = 1, svgTag='g', svgParms='',
                   strokeWidth=0.5, dimScale=1.0, lineColor='blue', textRenderer=defaultTextRenderer):
    XML_body = [ ]
    if radialLine_x <> None and radialLine_y <> None:
        XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, start_x, start_y, lineColor, strokeWidth) )
        if tail_x <> None and tail_y <> None:
            XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, tail_x, radialLine_y, lineColor, strokeWidth) )
            XML_body.append(' <circle cx ="%f" cy ="%f" r="%f" stroke="%s" fill="white" /> ' % (tail_x, radialLine_y, 4.5, lineColor) )
            notenum = 0
            XML_body.append( textRenderer( tail_x - 1.5, radialLine_y + 1.5, '0') )
            XML_body.append( '<!--%s-->' % (notenum) )
            XML_body.append( '<!--%s-->' % (textFormat) )
    XML = '''<%s  %s >
%s
</%s> ''' % ( svgTag, svgParms, "\n".join(XML_body), svgTag )
    return XML


def lineIntersection(line1, line2):
    x1,y1 = line1[0:2]
    dx1 = line1[2] - x1
    dy1 = line1[3] - y1
    x2,y2 = line2[0:2]
    dx2 = line2[2] - x2
    dy2 = line2[3] - y2
    # x1 + dx1*t1 = x2 + dx2*t2
    # y1 + dy1*t1 = y2 + dy2*t2
    A = numpy.array([
            [ dx1, -dx2 ],
            [ dy1, -dy2 ],
            ])
    b = numpy.array([ x2 - x1, y2 - y1])
    t1,t2 = numpy.linalg.solve(A,b)
    x_int = x1 + dx1*t1
    y_int = y1 + dy1*t1
    #assert x1 + dx1*t1 == x2 + dx2*t2
    return x_int, y_int

def angularDimensionSVG( line1, line2, x_baseline, y_baseline, x_text=None, y_text=None, textFormat='%3.1f°',  gap_datum_points = 2, dimension_line_overshoot=1,
                         arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5, lineColor='blue', textRenderer=defaultTextRenderer):
    XML = []
    x_int, y_int = lineIntersection(line1, line2)
    #XML.append( '<circle cx ="%f" cy ="%f" r="4" stroke="none" fill="rgb(0,0,255)" /> ' % (x_int, y_int) ) #for debugging
    p_center = numpy.array([ x_int, y_int ] )
    p1 = numpy.array( [line1[0], line1[1]] )
    p2 = numpy.array( [line1[2], line1[3]] )
    p3 = numpy.array( [line2[0], line2[1]] )
    p4 = numpy.array( [line2[2], line2[3]] )
    #XML.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,255,0);stroke-width:3" />' % (p1[0],p1[1],p2[0],p2[1]) )
    #XML.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,255,0);stroke-width:3" />' % (p3[0],p3[1],p4[0],p4[1]) )

    p5 = numpy.array([ x_baseline, y_baseline ])
    r_P5 = norm( p5 -p_center )
    # determine arrow position
    def arrowPosition( d ):
        cand1 = p_center + d*r_P5
        cand2 = p_center - d*r_P5
        return cand1 if norm( cand1 - p5) < norm( cand2 - p5) else cand2
    p_arrow1 = arrowPosition(directionVector(p1,p2))
    p_arrow2 = arrowPosition(directionVector(p3,p4))
    def line_to_arrow_point( a, b, c): # where a=p1,b=p2 or a=p3,b=p4 and c=p_arrow1 or c=p_arrow2
        if abs( norm(a -b) - (norm(a-c) + norm(b-c))) < norm(a -b)/1000:
            return
        s = a if norm(a-c) < norm(b-c) else b #start_point
        d = directionVector( s, c)
        v = s + gap_datum_points*d
        w = c + dimension_line_overshoot*d
        XML.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%f" />' % (v[0],v[1],w[0],w[1], lineColor, strokeWidth) )
    line_to_arrow_point( p1, p2, p_arrow1)
    line_to_arrow_point( p3, p4, p_arrow2)

    d1 = directionVector(p_center, p_arrow1)
    d2 = directionVector(p_center, p_arrow2)

    largeArc = False # given the selection method for the arrow heads (points and line1 and line2 used for measuring the angle)
    angle_1 = arctan2( d2[1], d2[0] )
    angle_2 = arctan2( d1[1], d1[0] )
    if abs(angle_1 - angle_2) < pi: #modulo correction required, since arctan2 return [-pi, pi]
        if angle_2 < angle_1:
            angle_2 = angle_2 + 2*pi
        else:
            angle_1 = angle_1 + 2*pi
    sweep = angle_2 > angle_1
    #rX, rY, xRotation, largeArc, sweep, _end_x, _end_y =
    XML.append('<path d = "M %f %f A %f %f 0 %i %i %f %f" style="stroke:%s;stroke-width:%1.2f;fill:none" />' % (p_arrow1[0],p_arrow1[1], r_P5, r_P5, largeArc, sweep, p_arrow2[0],p_arrow2[1],lineColor, strokeWidth))

    s = 1 if angle_2 > angle_1 else -1
    XML.append( arrowHeadSVG( p_arrow1, rotate2D(d1, s*pi/2), arrowL1, arrowL2, arrowW, lineColor ) )
    XML.append( arrowHeadSVG( p_arrow2, rotate2D(d2,-s*pi/2), arrowL1, arrowL2, arrowW, lineColor ) )

    if x_text <> None and y_text <> None:
        v = arccos( numpy.dot(d1, d2) )/ pi * 180
        textRotation = numpy.arctan2( y_text - y_int, x_text - x_int)
        textXML = textRenderer( x_text, y_text, dimensionText(v,textFormat), textRotation)
        textXML = textXML + '\n <!--%s-->' % v
        textXML = textXML + '\n <!--%s-->' % textFormat
        XML.append( textXML )
    XML = '''<%s  %s >
 %s
</%s> ''' % ( svgTag, svgParms, '\n'.join(XML), svgTag )
    return XML


def _centerLineSVG( x1, y1, x2, y2, len_dot, len_dash, len_gap, start_with_half_dot=False):
    start = numpy.array( [x1, y1] )
    end = numpy.array( [x2, y2] )
    d = directionVector(start, end)
    dCode = ''
    pos = start
    step = len_dot*0.5 if start_with_half_dot else len_dot
    while norm(pos - start) + 10**-6 < norm(end - start):
        dCode = dCode + 'M %f,%f' %  (pos[0], pos[1])
        pos = pos + d*step
        if norm(pos - start) > norm(end - start):
            pos = end
        dCode = dCode + ' L %f,%f ' % (pos[0], pos[1])
        pos = pos + d*len_gap
        step = len_dash if step < len_dash else len_dot
    if dCode <> '':
        return '<path d="%s"/>' % dCode
    else:
        return ''

def _centerLinesSVG( center, topLeft, bottomRight, dimScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, svgTag, svgParms, strokeWidth, lineColor, doVertical, doHorizontal ):
    XML_body = []
    center = numpy.array( center ) / dimScale
    topLeft = numpy.array( topLeft ) / dimScale
    if bottomRight <> None: bottomRight =  numpy.array( bottomRight ) / dimScale
    commonArgs =  centerLine_len_dot / dimScale,  centerLine_len_dash / dimScale,  centerLine_len_gap / dimScale
    if doVertical: XML_body.append( _centerLineSVG(center[0], center[1], center[0], topLeft[1], *commonArgs ) )
    if doHorizontal: XML_body.append( _centerLineSVG(center[0], center[1], topLeft[0], center[1], *commonArgs ) )
    if bottomRight <> None:
        if doVertical: XML_body.append( _centerLineSVG(center[0], center[1], center[0], bottomRight[1], *commonArgs ) )
        if doHorizontal: XML_body.append( _centerLineSVG(center[0], center[1], bottomRight[0], center[1], *commonArgs ) )
    return '''<%s %s transform="scale(%f,%f)" stroke="%s"  stroke-width="%f" >
%s
</%s> ''' % ( svgTag, svgParms, dimScale, dimScale, lineColor, strokeWidth/ dimScale, "\n".join(XML_body), svgTag )


def centerLinesSVG( center, topLeft, bottomRight=None, dimScale=1.0, centerLine_len_dot=2.0, centerLine_len_dash=6.0, centerLine_len_gap=2.0, svgTag='g', svgParms='', centerLine_width=0.5, centerLine_color='blue'):
    return _centerLinesSVG( center, topLeft, bottomRight, dimScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, svgTag, svgParms, centerLine_width, centerLine_color, True, True )

def centerLineSVG( center, topLeft, bottomRight=None,  dimScale=1.0, centerLine_len_dot=2.0, centerLine_len_dash=6.0, centerLine_len_gap=2.0, svgTag='g', svgParms='', centerLine_width=0.5, centerLine_color='blue'):
    v = abs(center[0] - topLeft[0]) < abs(center[1] - topLeft[1]) #vertical
    return _centerLinesSVG( center, topLeft, bottomRight, dimScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, svgTag, svgParms, centerLine_width, centerLine_color, v, not v )
