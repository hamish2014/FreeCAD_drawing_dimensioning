'''
Dialog notes
Use Qt Designer to edit the textAddDialog.ui
Once completed $ pyside-uic textAddDialog.ui > textAddDialog.py

To test inside Freecad

def go(): import grabPointAdd; reload(frabPointAdd)
go()


'''

from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import previewDimension

dimensioning = DimensioningProcessTracker()
dimensioning.assignedPrefenceValues = False

def grabPointDrawSVG( x, y, svgParms=''): # draw a cross
    XML = '''<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:rgb(255,255,255);stroke-width:0.01" />''' % ( x-0.1, y, x+0.1, y)
    #debugPrint(2, 'myDrawSVG.XML = %s' % XML)
    return XML

def grabPointDrawSVGpreview( x, y, svgParms=''):
    XML = '''<svg %s >
<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:rgb(0,0,0);stroke-width:0.2" />
<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:rgb(0,0,0);stroke-width:0.2" />
</svg>
  ''' % ( svgParms, x-1, y, x+1, y, x, y-1, x, y+1)
    #debugPrint(2, 'myPreviewSVG.XML = %s' % XML)
    return XML
    
def clickEvent( x, y):
    viewName = findUnusedObjectName('grabPoint')
    XML = grabPointDrawSVG(x,y)
    return viewName, XML

def hoverEvent( x, y):
    return grabPointDrawSVGpreview( x, y, svgParms=dimensioning.svg_preview_KWs['svgParms'] )

class AddGrabPoint:
    def Activated(self):
        V = getDrawingPageGUIVars() #needs to be done before dialog show, else active window is dialog and not freecad
        dimensioning.activate( V, textParms=['textRenderer'] ) # don't know if useful...

        debugPrint(3,'textRenderer created')
        debugPrint(3,'previewDimension.initializePreview')
        previewDimension.initializePreview(
            dimensioning.drawingVars,
            clickEvent, 
            hoverEvent )
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'grabPointAdd.svg' ) , 
            'MenuText': 'Add grab point to draw a free dimension', 
            'ToolTip': 'Add grab point to draw a free dimension'
            } 
FreeCADGui.addCommand('grabPoint', AddGrabPoint())


