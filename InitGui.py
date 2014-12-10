
class DimensioningWorkbench (Workbench): 
    import os
    from dimensioning import __dir__
    Icon = os.path.join( __dir__ , 'linearDimension.svg' )
    MenuText = 'Drawing Dimensioning'
    def Initialize(self):
        import importlib
        DEBUG=False
        if DEBUG:
            from dimensioning import __dir__, debugPrint
            import crudeDebugger, os
        for module in ['linearDimension', 'deleteDimension', 'circularDimension', 'textAdd', 'textEdit', 'textMove','escapeDimensioning', 'angularDimension', 'partsList','radiusDimension']:
            if not DEBUG:
                importlib.import_module( module )
            else:
                crudeDebugger.printingDebugging( os.path.join(__dir__, module + '.py') )
                importlib.import_module(  module + '_crudeDebugging')
        commandslist = ['linearDimension', 'circularDimension', 'radiusDimension', 'angularDimension', 'textAddDimensioning','textEditDimensioning', 'textMoveDimensioning', 'deleteDimension', 'escapeDimensioning', 'addPartsList']
        self.appendToolbar('Drawing Dimensioning', commandslist)

Gui.addWorkbench(DimensioningWorkbench())
