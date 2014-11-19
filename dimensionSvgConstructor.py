# This Python file uses the following encoding: utf-8
'''
library for constructing dimension SVGs
'''


import numpy

def directionVector( A, B ):
    if numpy.linalg.norm(B-A) == 0:
        return numpy.array([0.0,0.0])
    else:
        return (B-A)/numpy.linalg.norm(B-A)

def dimensionSVG_trimLine(A,B,trimA, trimB):
    d = directionVector( A, B) 
    return (A + d*trimA).tolist() + (B - d*trimB).tolist()

def arrowHeadSVG( tipPos, d, L1, L2, W):
    d2 = numpy.dot( [[ 0, -1],[ 1, 0]], d)
    R = numpy.array( [d, d2]).transpose()
    p2 = numpy.dot( R, [ L1,    W/2.0 ]) + tipPos
    p3 = numpy.dot( R, [ L1+L2, 0     ]) + tipPos
    p4 = numpy.dot( R, [ L1,   -W/2.0 ]) + tipPos
    return '<polygon points="%f,%f %f,%f %f,%f %f,%f" style="fill:blue;stroke:blue;stroke-width:0" />' % (tipPos[0], tipPos[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1])


def dimensionText( V, formatStr, roundingDigit=6):
    s1 = (formatStr % V).rstrip('0').rstrip('.')
    Vrounded = numpy.round(V, roundingDigit)
    s2 = (formatStr % Vrounded).rstrip('0').rstrip('.')
    return s2 if len(s2) < len(s1) else s1

def linearDimensionSVG( x1, y1, x2, y2, x3, y3, x4=None, y4=None, scale=1.0, textFormat='%3.3f',  gap_datum_points = 2, dimension_line_overshoot=1, arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', fontSize=4, strokeWidth=0.5):
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

    lineTemplate = '<line x1="%%f" y1="%%f" x2="%%f" y2="%%f" style="stroke:rgb(0,0,255);stroke-width:%1.2f" />' % strokeWidth
    lineXML = '\n'.join( lineTemplate % tuple(line) for line in lines )
    if x4 <> None and y4 <> None:
        v = numpy.linalg.norm(A-B)*scale
        textXML = '<text x="%f" y="%f" fill="red" style="font-size:%i" transform="rotate(%f %f,%f)">%s</text>' % ( x4, y4, fontSize, textRotation, x4, y4, dimensionText(v,textFormat))
        textXML = textXML + '\n <!--%s-->' % v
        textXML = textXML + '\n <!--%s-->' % textFormat
    else :
        textXML = ''
    distAB = numpy.linalg.norm(A-B)
    if distAB > 0:
        s = 1 if distAB > 2.5*(arrowL1 + arrowL2) else -1
        arrowXML = arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW ) + \
            arrowHeadSVG( B, s*directionVector(B,A), arrowL1, arrowL2, arrowW )
    else:
        arrowXML = ''
    XML = '''<%s  %s >
%s
%s
%s
</%s> ''' % ( svgTag, svgParms, lineXML, arrowXML, textXML, svgTag )
    return XML


def circularDimensionSVG( center_x, center_y, radius, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, text_x=None, text_y=None, textFormat='Ø%3.3f', centerPointDia = 1, arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', fontSize=4, strokeWidth=0.5, dimScale=1.0):
    XML_body = [ ' <circle cx ="%f" cy ="%f" r="%f" stroke="none" fill="rgb(0,0,255)" /> ' % (center_x, center_y, centerPointDia*0.5) ]
    XML_body.append( '<circle cx="%f" cy="%f" r="%f" stroke="rgb(0,0,255)" stroke-width="%1.2f" fill="none" />' % (center_x, center_y, radius, strokeWidth) )
    if radialLine_x <> None and radialLine_y <> None:
        theta = numpy.arctan2( radialLine_y - center_y, radialLine_x - center_x )
        A = numpy.array([ center_x + radius*numpy.cos(theta) , center_y + radius*numpy.sin(theta) ])
        B = numpy.array([ center_x - radius*numpy.cos(theta) , center_y - radius*numpy.sin(theta) ])
        XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,255);stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, B[0], B[1], strokeWidth) )
        if radius > 0:
            s = 1 if radius > arrowL1 + arrowL2 + 0.5*centerPointDia else -1
            XML_body.append( arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW ) )
            XML_body.append( arrowHeadSVG( B, s*directionVector(B,A), arrowL1, arrowL2, arrowW ) )
        if tail_x <> None and tail_y <> None:
            XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,255);stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, tail_x, radialLine_y, strokeWidth) )
    if text_x <> None and text_y <> None:
        XML_body.append( '<text x="%f" y="%f" fill="red" style="font-size:%i">%s</text>' % ( text_x, text_y, fontSize, dimensionText(2*radius*dimScale,textFormat)))
        XML_body.append( '<!--%s-->' % (2*radius) )
        XML_body.append( '<!--%s-->' % (textFormat) )
    XML = '''<%s  %s >
%s
</%s> ''' % ( svgTag, svgParms, "\n".join(XML_body), svgTag )
    return XML
