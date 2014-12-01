
class DimensioningWorkbench (Workbench): 
    import os
    from dimensioning import __dir__
    Icon = os.path.join( __dir__ , 'linearDimension.svg' )
    MenuText = "Drawing Dimensioning"
    def Initialize(self):
        import importlib
        DEBUG=True
        if DEBUG:
            from dimensioning import __dir__, debugPrint
            import crudeDebugger, os
        for module in ['linearDimension', 'deleteDimension', 'circularDimension', 'addText', 'escapeDimensioning', 'angularDimension']:
            if not DEBUG:
                importlib.import_module( module )
            else:
                crudeDebugger.printingDebugging( os.path.join(__dir__, module + '.py') )
                importlib.import_module(  module + '_crudeDebugging')
        commandslist = ["linearDimension", "circularDimension", "angularDimension", "addTextDimensioning", "deleteDimension", "escapeDimensioning"]
        self.appendToolbar("Drawing Dimensioning", commandslist)

Gui.addWorkbench(DimensioningWorkbench())
