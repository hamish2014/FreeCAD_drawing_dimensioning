from crudeDebugger import crudeDebuggerPrint
crudeDebuggerPrint('''axialConstraint.py:0  	from assembly2lib import * ''')
from assembly2lib import *
crudeDebuggerPrint('''axialConstraint.py:1  	from assembly2lib import __dir__ #varialbe not imported * directive ... ''')
from assembly2lib import __dir__ #varialbe not imported * directive ...
crudeDebuggerPrint('''axialConstraint.py:2  	from pivy import coin ''')
from pivy import coin

class AxialConstraint:
     def __init__(self, obj, object1Name, object1FaceInd, object2Name, object2FaceInd):
          '''Add some custom properties to our box feature'''
          obj.addProperty("App::PropertyString","Object1","AxialConstraint","Object 1").Object1 = object1Name
          obj.addProperty("App::PropertyInteger","FaceInd1","AxialConstraint","Object 1 face index").FaceInd1 = object1FaceInd
          obj.addProperty("App::PropertyString","Object2","AxialConstraint","Object 2").Object2 = object2Name
          obj.addProperty("App::PropertyInteger","FaceInd2","AxialConstraint","Object 2 face index").FaceInd2 = object2FaceInd
          for prop in ["Object1","Object2","FaceInd1","FaceInd2"]:
               obj.setEditorMode(prop, 1) 
               #0 -- default mode, read and write  1 -- read-only  2 -- hidden
          obj.Proxy = self
          
     def onChanged(self, fp, prop):
          '''Do something when a property has changed'''
          crudeDebuggerPrint('''axialConstraint.py:18  	          FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n") ''')
          FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
          
     def execute(self, fp):
          '''Do something when doing a recomputation, this method is mandatory'''
          FreeCAD.Console.PrintMessage("Recompute Python Box feature\n")
 
class ViewProviderAxialConstraint:
     def __init__(self, obj):
          "Set this object to the proxy object of the actual view provider"
          #obj.addProperty("App::PropertyColor","Color","Box","Color of the box").Color=(1.0,0.0,0.0)
          obj.Proxy = self
 
     def attach(self, obj):
          '''Setup the scene sub-graph of the view provider, this method is mandatory'''
          crudeDebuggerPrint('''axialConstraint.py:32  	          pass ''')
          pass
 
     def getDisplayModes(self,obj):
          '''Return a list of display modes.'''
          modes=["None"]
          return modes
 
     def getDefaultDisplayMode(self):
          '''Return the name of the default display mode. It must be defined in getDisplayModes.'''
          crudeDebuggerPrint('''axialConstraint.py:41  	          return "None" ''')
          return "None"
 
     def getIcon(self):
          '''Return the icon in XPM format which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
          return os.path.join( __dir__ , 'axialConstraint.svg' ) 
          return '''
 			/* XPM */
 			static const char * ViewProviderBox_xpm[] = {
 			"16 16 6 1",
 			" 	c None",
 			".	c #141010",
 			"+	c #615BD2",
 			"@	c #C39D55",
 			"#	c #000000",
 			"$	c #57C355",
 			"        ........",
 			"   ......++..+..",
 			"   .@@@@.++..++.",
 			"   .@@@@.++..++.",
 			"   .@@  .++++++.",
 			"  ..@@  .++..++.",
 			"###@@@@ .++..++.",
 			"##$.@@$#.++++++.",
 			"#$#$.$$$........",
 			"#$$#######      ",
 			"#$$#$$$$$#      ",
 			"#$$#$$$$$#      ",
 			"#$$#$$$$$#      ",
 			" #$#$$$$$#      ",
 			"  ##$$$$$#      ",
 			"   #######      "};
 			'''
 

class AxialConstraintSelecter:
     def __init__(self):
          crudeDebuggerPrint('''axialConstraint.py:77  	          self.observer = SelectionObserver( self.addSelection ) ''')
          self.observer = SelectionObserver( self.addSelection )
          crudeDebuggerPrint('''axialConstraint.py:78  	          self.selections = [] ''')
          self.selections = []
          crudeDebuggerPrint('''axialConstraint.py:79  	          FreeCADGui.Selection.addObserver(self.observer) ''')
          FreeCADGui.Selection.addObserver(self.observer)      
          
     def addSelection( self, doc, objName, sub, pnt ):
          crudeDebuggerPrint('''axialConstraint.py:82  	          if sub.startswith('Face'): ''')
          if sub.startswith('Face'):
               crudeDebuggerPrint('''axialConstraint.py:83  	               obj = FreeCAD.ActiveDocument.getObject(objName) ''')
               obj = FreeCAD.ActiveDocument.getObject(objName)
               crudeDebuggerPrint('''axialConstraint.py:84  	               faceInd = int(sub[4:]) - 1 ''')
               faceInd = int(sub[4:]) - 1
               crudeDebuggerPrint('''axialConstraint.py:85  	               face = obj.Shape.Faces[faceInd] ''')
               face = obj.Shape.Faces[faceInd]
               crudeDebuggerPrint('''axialConstraint.py:86  	               if hasattr(face.Surface, 'Radius'): ''')
               if hasattr(face.Surface, 'Radius'):
                    crudeDebuggerPrint('''axialConstraint.py:87  	                    self.selections.extend([objName, faceInd]) ''')
                    self.selections.extend([objName, faceInd])
                    crudeDebuggerPrint('''axialConstraint.py:88  	                    FreeCAD.Console.PrintMessage("axial Constraint: Selected %s:%s\n" % (objName, sub)) ''')
                    FreeCAD.Console.PrintMessage("axial Constraint: Selected %s:%s\n" % (objName, sub))
                    crudeDebuggerPrint('''axialConstraint.py:89  	                    if len(self.selections) == 4: ''')
                    if len(self.selections) == 4:
                         crudeDebuggerPrint('''axialConstraint.py:90  	                         cName = findUnusedObjectName('axialConstraint') ''')
                         cName = findUnusedObjectName('axialConstraint')
                         crudeDebuggerPrint('''axialConstraint.py:91  	                         debugPrint(2, "creating %s" % cName ) ''')
                         debugPrint(2, "creating %s" % cName )
                         crudeDebuggerPrint('''axialConstraint.py:92  	                         c = FreeCAD.ActiveDocument.addObject("App::FeaturePython", cName) ''')
                         c = FreeCAD.ActiveDocument.addObject("App::FeaturePython", cName)
                         crudeDebuggerPrint('''axialConstraint.py:93  	                         AxialConstraint(c, *self.selections) ''')
                         AxialConstraint(c, *self.selections)
                         crudeDebuggerPrint('''axialConstraint.py:94  	                         ViewProviderAxialConstraint(c.ViewObject) ''')
                         ViewProviderAxialConstraint(c.ViewObject)
                         crudeDebuggerPrint('''axialConstraint.py:95  	                         FreeCADGui.Selection.removeObserver(self.observer) ''')
                         FreeCADGui.Selection.removeObserver(self.observer)         
         
class AxialConstraintCommand:
    def Activated(self):
        crudeDebuggerPrint('''axialConstraint.py:99  	        AxialConstraintSelecter() ''')
        AxialConstraintSelecter()
    def GetResources(self): 
        crudeDebuggerPrint('''axialConstraint.py:101  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'axialConstraint.svg' ) , 
            'MenuText': 'Add Axial Constraint', 
            'ToolTip': 'Add an Axial Constraint between two objects'
            } 

crudeDebuggerPrint('''axialConstraint.py:107  	FreeCADGui.addCommand('addAxialConstraint', AxialConstraintCommand()) ''')
FreeCADGui.addCommand('addAxialConstraint', AxialConstraintCommand())