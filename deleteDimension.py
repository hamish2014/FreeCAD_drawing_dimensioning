
from dimensioning import *
from dimensioning import __dir__ # not imported with * directive
from drawingSelectionLib import generateSelectionGraphicsItems

def deleteDimension( event, referer, elementXML, elementParms, elementViewObject ):
    debugPrint(2, 'deleting dimension %s' % elementViewObject.Name)
    App.ActiveDocument.removeObject( elementViewObject.Name )
    moduleGlobals['page'].touch()
    App.ActiveDocument.recompute()
    

moduleGlobals = {}
class DeleteDimension:
    def Activated(self):
        if not get_FreeCAD_drawing_variables(moduleGlobals):
            return
        maskBrush  =   QtGui.QBrush( QtGui.QColor(160,0,0,100) )
        maskPen =      QtGui.QPen( QtGui.QColor(160,0,0,100) )
        maskPen.setWidth(0.0)
        maskHoverPen = QtGui.QPen( QtGui.QColor(255,0,0,255) )
        maskHoverPen.setWidth(0.0)

        selectGraphicsItems = generateSelectionGraphicsItems( 
            [obj for obj in moduleGlobals['page'].Group  if obj.Name.startswith('dim')], 
            deleteDimension , doTextItems = True, pointWid=2.0,
            maskPen=maskPen, maskHoverPen=maskHoverPen, maskBrush = maskBrush
            )
        for g in selectGraphicsItems:
            moduleGlobals['graphicsScene'].addItem(g)
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'deleteDimension.svg' ) , 
            'MenuText': 'Delete Dimension', 
            'ToolTip': 'Delete a dimension'
            } 

FreeCADGui.addCommand('deleteDimension', DeleteDimension())
