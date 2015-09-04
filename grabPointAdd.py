
from dimensioning import *
import previewDimension

d = DimensioningProcessTracker()

def grabPointDrawSVG( x, y, preview): # draw a cross
    if preview:
        return '''<g>
<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:rgb(0,0,0);stroke-width:0.2" />
<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:rgb(0,0,0);stroke-width:0.2" />
</g> ''' % ( x-1, y, x+1, y, x, y-1, x, y+1)
    else:
        return '<g> <line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:rgb(0,0,0);stroke-width:0.01" /> </g> ''' % ( x, y, x, y)

    
def grabPoint_preview( x, y):
    return grabPointDrawSVG( x, y, d.preview)

def grabPoint_clickHandler( x, y):
    d.preview = False
    return  'createDimension:%s' % findUnusedObjectName('grabPoint')

class AddGrabPoint:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate( V, dialogTitle='Add Grab Point', dialogIconPath=':/dd/icons/grabPointAdd.svg', endFunction=self.Activated )
        d.preview = True
        previewDimension.initializePreview(
            d,
            grabPoint_preview, 
            grabPoint_clickHandler )
        
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/grabPointAdd.svg' , 
            'MenuText': 'Add grab point to draw a free dimension', 
            'ToolTip': 'Add grab point to draw a free dimension'
            } 
FreeCADGui.addCommand('dd_grabPoint', AddGrabPoint())


