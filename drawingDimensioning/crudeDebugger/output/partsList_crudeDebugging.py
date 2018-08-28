from crudeDebugger import crudeDebuggerPrint
'''
create parts list
'''

crudeDebuggerPrint('''partsList.py:4  	from dimensioning import * ''')
from dimensioning import *
crudeDebuggerPrint('''partsList.py:5  	from dimensioning import __dir__ # not imported with * directive ''')
from dimensioning import __dir__ # not imported with * directive
crudeDebuggerPrint('''partsList.py:6  	import previewDimension ''')
import previewDimension

crudeDebuggerPrint('''partsList.py:8  	dimensioning = DimensioningProcessTracker() ''')
dimensioning = DimensioningProcessTracker()
crudeDebuggerPrint('''partsList.py:9  	strokeWidth = 0.4 ''')
strokeWidth = 0.4

crudeDebuggerPrint('''partsList.py:11  	fontSize = 4.0 ''')
fontSize = 4.0
crudeDebuggerPrint('''partsList.py:12  	fontColor = 'rgb(0,0,0)' ''')
fontColor = 'rgb(0,0,0)'
crudeDebuggerPrint('''partsList.py:13  	fontPadding = 1.6 ''')
fontPadding = 1.6
crudeDebuggerPrint('''partsList.py:14  	rowHeight = fontSize + 2*fontPadding ''')
rowHeight = fontSize + 2*fontPadding


class PartsList:
    def __init__(self):
        crudeDebuggerPrint('''partsList.py:19  	        self.entries = [] ''')
        self.entries = []
    def addObject(self, obj):
        crudeDebuggerPrint('''partsList.py:21  	        try: ''')
        try:
            crudeDebuggerPrint('''partsList.py:22  	            index = self.entries.index(obj) ''')
            index = self.entries.index(obj)
            crudeDebuggerPrint('''partsList.py:23  	            self.entries[index].count = self.entries[index].count + 1 ''')
            self.entries[index].count = self.entries[index].count + 1
        except ValueError:
            crudeDebuggerPrint('''partsList.py:25  	            self.entries.append(PartListEntry( obj )) ''')
            self.entries.append(PartListEntry( obj ))
    def svg(self, x, y, svgTag='g', svgParms=''):
        crudeDebuggerPrint('''partsList.py:27  	        XML_body = [] ''')
        XML_body = []
        def addLine(x1,y1,x2,y2):
            crudeDebuggerPrint('''partsList.py:29  	            XML_body.append('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,0);stroke-width:%1.2f" />' % (x1, y1, x2, y2, strokeWidth)) ''')
            XML_body.append('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,0);stroke-width:%1.2f" />' % (x1, y1, x2, y2, strokeWidth))
        crudeDebuggerPrint('''partsList.py:30  	        #building table body ''')
        #building table body
        crudeDebuggerPrint('''partsList.py:31  	        width = sum( c.width for c in columns ) ''')
        width = sum( c.width for c in columns )
        crudeDebuggerPrint('''partsList.py:32  	        for i in range(len(self.entries) +2): ''')
        for i in range(len(self.entries) +2):
            crudeDebuggerPrint('''partsList.py:33  	            addLine( x, y + i*rowHeight, x+width, y + i*rowHeight ) ''')
            addLine( x, y + i*rowHeight, x+width, y + i*rowHeight )
        crudeDebuggerPrint('''partsList.py:34  	        y_bottom = y + i*rowHeight ''')
        y_bottom = y + i*rowHeight
        crudeDebuggerPrint('''partsList.py:35  	        addLine( x, y, x, y_bottom ) ''')
        addLine( x, y, x, y_bottom )
        crudeDebuggerPrint('''partsList.py:36  	        columnOffsets = [0] ''')
        columnOffsets = [0]
        crudeDebuggerPrint('''partsList.py:37  	        for c in columns: ''')
        for c in columns:
            crudeDebuggerPrint('''partsList.py:38  	            columnOffsets.append( columnOffsets[-1] + c.width ) ''')
            columnOffsets.append( columnOffsets[-1] + c.width )
            crudeDebuggerPrint('''partsList.py:39  	            addLine( x+columnOffsets[-1], y, x+columnOffsets[-1], y_bottom ) ''')
            addLine( x+columnOffsets[-1], y, x+columnOffsets[-1], y_bottom )
        def addText(row,col,text):
            crudeDebuggerPrint('''partsList.py:41  	            x1 = x + columnOffsets[col] + fontPadding ''')
            x1 = x + columnOffsets[col] + fontPadding
            crudeDebuggerPrint('''partsList.py:42  	            y1 = y + (row+1)*rowHeight - fontPadding ''')
            y1 = y + (row+1)*rowHeight - fontPadding
            crudeDebuggerPrint('''partsList.py:43  	            XML_body.append('<text x="%f" y="%f" fill="%s" style="font-size:%i">%s</text>' % (x1,y1,fontColor,fontSize,text)) ''')
            XML_body.append('<text x="%f" y="%f" fill="%s" style="font-size:%i">%s</text>' % (x1,y1,fontColor,fontSize,text))
        crudeDebuggerPrint('''partsList.py:44  	        for i,c in enumerate(columns): ''')
        for i,c in enumerate(columns):
            crudeDebuggerPrint('''partsList.py:45  	            addText(0,i,c.heading) ''')
            addText(0,i,c.heading)
            crudeDebuggerPrint('''partsList.py:46  	            for j, entry in enumerate(self.entries): ''')
            for j, entry in enumerate(self.entries):
                crudeDebuggerPrint('''partsList.py:47  	                addText( j+1, i,  c.entryFor(j, entry)) ''')
                addText( j+1, i,  c.entryFor(j, entry))

        crudeDebuggerPrint('''partsList.py:49  	        XML = ''' +"'''" +'''<%s  %s > %s </%s> ''' +"'''" +''' % ( svgTag, svgParms, '\n'.join(XML_body), svgTag ) ''')
        XML = '''<%s  %s > %s </%s> ''' % ( svgTag, svgParms, '\n'.join(XML_body), svgTag )
        crudeDebuggerPrint('''partsList.py:50  	        debugPrint(4, 'partList.XML %s' % XML) ''')
        debugPrint(4, 'partList.XML %s' % XML)
        crudeDebuggerPrint('''partsList.py:51  	        return XML ''')
        return XML


class PartListEntry:
    def __init__(self, obj):
        crudeDebuggerPrint('''partsList.py:56  	        self.obj = obj ''')
        self.obj = obj
        crudeDebuggerPrint('''partsList.py:57  	        self.count = 1 ''')
        self.count = 1
        crudeDebuggerPrint('''partsList.py:58  	        self.sourceFile = obj.sourceFile ''')
        self.sourceFile = obj.sourceFile
        crudeDebuggerPrint('''partsList.py:59  	        self.name = os.path.basename( obj.sourceFile ) ''')
        self.name = os.path.basename( obj.sourceFile )
    def __eq__(self, b):
        crudeDebuggerPrint('''partsList.py:61  	        return  self.sourceFile == b.sourceFile ''')
        return  self.sourceFile == b.sourceFile

class PartListColumn:
    def __init__(self, heading, width, entryFor):
        crudeDebuggerPrint('''partsList.py:65  	        self.heading = heading ''')
        self.heading = heading
        crudeDebuggerPrint('''partsList.py:66  	        self.width = width ''')
        self.width = width
        crudeDebuggerPrint('''partsList.py:67  	        self.entryFor = entryFor ''')
        self.entryFor = entryFor

crudeDebuggerPrint('''partsList.py:69  	columns = [ ''')
columns = [
    PartListColumn('part', 20, lambda ind,entry: '%i' % (ind+1)),
    PartListColumn('sourceFile', 80, lambda ind,entry: '%s' % os.path.basename(entry.sourceFile).replace('.fcstd','')),
    PartListColumn('quantity', 40, lambda ind,entry: '%i' % entry.count),
    ]
        

def clickEvent( x, y):
    crudeDebuggerPrint('''partsList.py:77  	    viewName = findUnusedObjectName('dimPartsList') ''')
    viewName = findUnusedObjectName('dimPartsList')
    crudeDebuggerPrint('''partsList.py:78  	    XML = dimensioning.partsList.svg(x,y) ''')
    XML = dimensioning.partsList.svg(x,y)
    crudeDebuggerPrint('''partsList.py:79  	    return viewName, XML ''')
    return viewName, XML

def hoverEvent( x, y):
    crudeDebuggerPrint('''partsList.py:82  	    return dimensioning.partsList.svg( x, y, **dimensioning.svg_preview_KWs ) ''')
    return dimensioning.partsList.svg( x, y, **dimensioning.svg_preview_KWs )

class AddPartsList:
    def Activated(self):
        crudeDebuggerPrint('''partsList.py:86  	        V = getDrawingPageGUIVars() #needs to be done before dialog show, else Qt active is dialog and not freecads ''')
        V = getDrawingPageGUIVars() #needs to be done before dialog show, else Qt active is dialog and not freecads
        crudeDebuggerPrint('''partsList.py:87  	        dimensioning.activate( V ) ''')
        dimensioning.activate( V )
        crudeDebuggerPrint('''partsList.py:88  	        P = PartsList() ''')
        P = PartsList()
        crudeDebuggerPrint('''partsList.py:89  	        for obj in App.ActiveDocument.Objects: ''')
        for obj in App.ActiveDocument.Objects:
            crudeDebuggerPrint('''partsList.py:90  	            if 'importPart' in obj.Content: ''')
            if 'importPart' in obj.Content:
                crudeDebuggerPrint('''partsList.py:91  	                debugPrint(3, 'adding %s to parts list' % obj.Name) ''')
                debugPrint(3, 'adding %s to parts list' % obj.Name)
                crudeDebuggerPrint('''partsList.py:92  	                P.addObject(obj) ''')
                P.addObject(obj)
        crudeDebuggerPrint('''partsList.py:93  	        dimensioning.partsList = P ''')
        dimensioning.partsList = P
        crudeDebuggerPrint('''partsList.py:94  	        P.svg(0,0) #calling here as once inside previewRect, error trapping difficult... ''')
        P.svg(0,0) #calling here as once inside previewRect, error trapping difficult...
        crudeDebuggerPrint('''partsList.py:95  	        previewDimension.initializePreview( V, clickEvent, hoverEvent ) ''')
        previewDimension.initializePreview( V, clickEvent, hoverEvent )
        
    def GetResources(self): 
        crudeDebuggerPrint('''partsList.py:98  	        tip = 'create a parts list from the objects imported using the assembly 2 workbench' ''')
        tip = 'create a parts list from the objects imported using the assembly 2 workbench'
        crudeDebuggerPrint('''partsList.py:99  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'partsList.svg' ) , 
            'MenuText': tip, 
            'ToolTip': tip
            } 
crudeDebuggerPrint('''partsList.py:104  	FreeCADGui.addCommand('addPartsList', AddPartsList()) ''')
FreeCADGui.addCommand('addPartsList', AddPartsList())

