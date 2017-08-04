# -*- coding: utf-8 -*-

'''
Library to parse XML codes such as those used for the FreeCAD view result, as to get graphics elements out.
'''

# Future Work,
#  - replace custom XML parser lib with an established svg library ...
#


import numpy
from numpy import sin, cos, dot

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
        self.header = self.header.replace('\n','').replace('\t',' ')
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

    def rootNode(self):
        if self.parent is None:
            return self
        else:
            return self.parent.rootNode()
        

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
                rotateParms = map(float, extractParms(self.header, 0, 'rotate(', ', ', ')'))
                if len(rotateParms) == 3:
                    rotateDegrees, rx, ry = rotateParms
                else:
                    assert len(rotateParms) == 1
                    rotateDegrees, rx, ry = rotateParms[0], 0.0, 0.0
                rads = numpy.pi * rotateDegrees / 180
                R = numpy.array([ [ cos(rads), -sin(rads)], [ sin(rads), cos(rads)] ])
                r_o = numpy.array([ rx, ry])
            if 'translate(' in self.header:
                tx, ty = map(float, extractParms(self.header, 0, 'translate(', ', ', ')'))
            if 'scale(' in self.header:
                scaleParms = map(float, extractParms(self.header, 0, 'scale(', ', ', ')'))
                if len(scaleParms) == 2:
                    sx, sy = scaleParms
                else:
                    sx, sy = scaleParms[0], scaleParms[0]
            if 'matrix(' in self.header: #"matrix(1.25,0,0,-1.25,-348.3393,383.537)"
                sx, shear_1, shear_2, sy, tx, ty = map(float, extractParms(self.header, 0, 'matrix(', ', ', ')'))
                if not shear_1 == 0 and shear_2 == 0:
                    raise NotImplementedError, " not shear_1 == 0 and shear_2 == 0! header %s" % self.header 
        p = numpy.array( [sx*x + tx, sy*y + ty] )
        point = dot(R, p-r_o) +r_o
        if self.parent <> None:
            return self.parent.applyTransforms(*point)
        else:
            return point[0], point[1]

    def Transforms( self, cumalative=True, T=None, c=None):
        'y = dot(T,x) + c'
        if T is None:
            T = numpy.eye(2)
            c = numpy.zeros(2)
        R = numpy.eye(2)
        r_o = numpy.zeros(2)
        tx, ty = 0, 0
        sx, sy = 1.0, 1.0
            
        if 'transform=' in self.header:
            if 'matrix(' in self.header: #"matrix(1.25,0,0,-1.25,-348.3393,383.537)"
                t_11, t_12, t_21, t22, c1, c2 = map(float, extractParms(self.header, 0, 'matrix(', ', ', ')'))
                T_e = numpy.array([[ t_11, t_12], [t_21, t22]])
                c_e = numpy.array([c1,c2])
                T = dot( T_e, T )
                c = dot( T_e, c) + c_e
            if 'translate(' in self.header:
                tx, ty = map(float, extractParms(self.header, 0, 'translate(', ', ', ')'))
                
            if 'scale(' in self.header:
                scaleParms = map(float, extractParms(self.header, 0, 'scale(', ', ', ')'))
                if len(scaleParms) == 2:
                    sx, sy = scaleParms
                else:
                    sx, sy = scaleParms[0], scaleParms[0]
            if 'rotate(' in self.header:
                rotateParms = map(float, extractParms(self.header, 0, 'rotate(', ', ', ')'))
                if len(rotateParms) == 3:
                    rotateDegrees, rx, ry = rotateParms
                else:
                    assert len(rotateParms) == 1
                    rotateDegrees, rx, ry = rotateParms[0], 0.0, 0.0
                rads = numpy.pi * rotateDegrees / 180
                R = numpy.array([ [ cos(rads), -sin(rads)], [ sin(rads), cos(rads)] ])
                r_o = numpy.array([ rx, ry])
        T_e = numpy.array([[ sx, 0.0], [0.0, sy]])
        c_e = numpy.array([tx,ty])
        T = dot( T_e, T )
        c = dot( T_e, c) + c_e
        # z = dot(R, y - r_o) + r_o
        # z = dot(R, dot(T,x) + c - r_o) + r_o
        T = dot(R,T)
        c = dot(R,c) - dot(R,r_o) + r_o
        if self.parent <> None and cumalative:
            return self.parent.Transforms(T=T, c=c)
        else:
            return T, c

    def scaling(self):
        sx = 1.0
        if 'scale(' in self.header:
            sx = map(float, extractParms(self.header, 0, 'scale(', ',', ')'))[0]
        if len(self.children) == 1:
            sx_child = self.children[0].scaling()
        else:
            sx_child = 1.0
        return sx * sx_child

    def scaling2(self, s=1.0):
        'other scaling works only for drawingObject.ViewResult groups...'
        if 'transform=' in self.header:
            if 'scale(' in self.header:
                scaleParms = map(float, extractParms(self.header, 0, 'scale(', ', ', ')'))
                if len(scaleParms) == 2:
                    sx, sy = scaleParms
                else:
                    sx, sy = scaleParms[0], scaleParms[0]
                s = s * sx
            elif 'matrix(' in self.header: #"matrix(1.25,0,0,-1.25,-348.3393,383.537)"
                sx, shear_1, shear_2, sy, tx, ty = map(float, extractParms(self.header, 0, 'matrix(', ', ', ')'))
                assert shear_1 == 0 and shear_2 == 0
                s = s *sx
        if self.parent <> None:
            return self.parent.scaling2(s)
        else:
            return s
            
    def getAllElements(self):
        return [self] + sum([c.getAllElements() for c in self.children],[])

def replaceParm( xml, parm, newText ):
    # <text x="50" y="-60" fill="blue" style="font-size:8" >256.426</text> '''
    keyPos = xml.find(parm)
    p1 = xml.find('"', keyPos)
    p2 = xml.find('"', p1+1)
    return xml[:p1+1] + newText + xml[p2:]

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
    print('')
    print('result:')
    svg = SvgXMLTreeNode(XML,0)
    print(svg)
