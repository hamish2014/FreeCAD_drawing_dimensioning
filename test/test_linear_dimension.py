if __name__ == '__main__':
    print('''run tests via
  FreeCAD_drawing_dimensioning$ python2 test''')
    exit()


import unittest
import xml.etree.ElementTree as XML_Tree
def xml_prettify( xml_str ):
    import xml.dom.minidom as minidom
    xml = minidom.parseString( xml_str )
    S = xml.toprettyxml(indent='  ')
    return '\n'.join( s for s in S.split('\n') if s.strip() != '' )

import numpy
from drawingDimensioning.linearDimension import linearDimensionSVG_points
        
class Tests(unittest.TestCase):
    
    def test_dy( self ):
        svg_string =  linearDimensionSVG_points( x1 = 0, y1 = 10 , x2 = 30, y2= 25, x3 = 40, y3= 20, x4 = 50, y4 = 30 )
        svg = XML_Tree.fromstring( svg_string )
        #print( xml_prettify( svg_string ) )
        self.assertEqual( svg.find('text').text, '15'  )

    def test_dx( self ):
        svg_string =  linearDimensionSVG_points( x1 = 0, y1 = 10 , x2 = 30, y2= 25, x3 = 15, y3= 40, x4 = 50, y4 = 30 )
        svg = XML_Tree.fromstring( svg_string )
        #print( xml_prettify( svg_string ) )
        self.assertEqual( svg.find('text').text, '30'  )

    def test_distance( self ):
        svg_string =  linearDimensionSVG_points( x1 = 0, y1 = 10 , x2 = 30, y2= 25, x3 = -15, y3= 40, x4 = 50, y4 = 30 )
        svg = XML_Tree.fromstring( svg_string )
        #print( xml_prettify( svg_string ) )
        self.assertEqual( svg.find('text').text, '%3.3f' % numpy.linalg.norm(numpy.array([0,10]) - numpy.array([30,25]) ))
