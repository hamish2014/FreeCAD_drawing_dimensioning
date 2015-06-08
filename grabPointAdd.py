
from dimensioning import *
import previewDimension

d = DimensioningProcessTracker()

def grabPointDrawSVG( x, y, strokeWidth=0.2): # draw a cross
    return '''<g>
<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:rgb(0,0,0);stroke-width:%f" />
<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:rgb(0,0,0);stroke-width:%f" />
</g> ''' % ( x-1, y, x+1, y, strokeWidth,  x, y-1, x, y+1, strokeWidth)

    
def grabPoint_preview( x, y):
    return grabPointDrawSVG( x, y, d.strokeWidth)

def grabPoint_clickHandler( x, y):
    d.strokeWidth = 0
    return  'createDimension:%s' % findUnusedObjectName('dimGrabPoint')

class AddGrabPoint:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate( V )
        d.strokeWidth = 0.2
        previewDimension.initializePreview(
            d.drawingVars,
            grabPoint_preview, 
            grabPoint_clickHandler )
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'grabPointAdd.svg' ) , 
            'MenuText': 'Add grab point to draw a free dimension', 
            'ToolTip': 'Add grab point to draw a free dimension'
            } 
FreeCADGui.addCommand('dd_grabPoint', AddGrabPoint())


