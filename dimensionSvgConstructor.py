# This Python file uses the following encoding: utf-8
'''
library containing commonly used SVGs construction functions
'''


import numpy
from numpy import dot, pi, arctan2, sin, cos, arccos
from numpy.linalg import norm
from svgLib_dd import SvgTextRenderer

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

def remove_tailing_zeros(s):
    if '.' in s:
        return s.rstrip('0').rstrip('.')
    else:
        return s

def dimensionText( V, formatStr, roundingDigit=6, comma=False):
    try:
        s1 = remove_tailing_zeros(formatStr % {'value':V})
    except TypeError:
        s1 = remove_tailing_zeros(formatStr % V)
    Vrounded = numpy.round(V, roundingDigit)
    try:
        s2 = remove_tailing_zeros(formatStr % {'value':Vrounded})
    except TypeError:
        s2 = remove_tailing_zeros(formatStr % Vrounded)
    s =  s2 if len(s2) < len(s1) else s1
    if comma: s = s.replace('.',',')
    return s

defaultTextRenderer = SvgTextRenderer(font_family='Verdana', font_size='5pt', fill="red")

def svgLine(  x1, y1, x2, y2, lineColor, strokeWidth):
    return '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (x1, y1, x2, y2, lineColor, strokeWidth )

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

def textPlacement_common_procedure( A, B, text, x_text, y_text, textRotation, textRenderer, autoPlaceText, autoPlaceOffset):
    if textRotation > 90:
        textRotation = textRotation - 180
    if textRotation > 88:
        textRotation = textRotation - 180
    elif textRotation > 12 :
        textRotation = textRotation - 90
    elif textRotation < -92:
        textRotation = textRotation + 90
    if not autoPlaceText:
        if x_text <> None and y_text <> None:
            return textRenderer( x_text, y_text, text, rotation=textRotation )
        else :
            return ''
    else:
        theta = (textRotation - 90)/180.0*pi
        pos_text = (A + B)/2 + autoPlaceOffset * numpy.array([ cos(theta), sin(theta)])
        return textRenderer( pos_text[0], pos_text[1], text, rotation=textRotation, text_anchor='middle' )
