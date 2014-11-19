from crudeDebugger import crudeDebuggerPrint
'''
Python Code for generating crude debugging functionality for the Dimensioning FreeCAD module.
'''

crudeDebuggerPrint('''crudeDebugger.py:4  	import os, sys ''')
import os, sys

crudeDebuggerPrint('''crudeDebugger.py:6  	__dir__ = os.path.dirname(__file__) ''')
__dir__ = os.path.dirname(__file__)

crudeDebuggerPrint('''crudeDebugger.py:8  	debug_output_directory = os.path.join( __dir__ , 'crudeDebugger_output' ) ''')
debug_output_directory = os.path.join( __dir__ , 'crudeDebugger_output' )
crudeDebuggerPrint('''crudeDebugger.py:9  	if not os.path.exists(debug_output_directory): ''')
if not os.path.exists(debug_output_directory):
    crudeDebuggerPrint('''crudeDebugger.py:10  	    os.mkdir(debug_output_directory) ''')
    os.mkdir(debug_output_directory)
crudeDebuggerPrint('''crudeDebugger.py:11  	sys.path.append(debug_output_directory) ''')
sys.path.append(debug_output_directory)

crudeDebuggerPrint('''crudeDebugger.py:13  	global crudeDebuggerOutputFile ''')
global crudeDebuggerOutputFile
crudeDebuggerPrint('''crudeDebugger.py:14  	crudeDebuggerOutputFile = None ''')
crudeDebuggerOutputFile = None

def crudeDebuggerPrint( txt, epilogue='\n' ):
    crudeDebuggerPrint('''crudeDebugger.py:17  	    global crudeDebuggerOutputFile ''')
    global crudeDebuggerOutputFile
    crudeDebuggerPrint('''crudeDebugger.py:18  	    if crudeDebuggerOutputFile == None: ''')
    if crudeDebuggerOutputFile == None:
        crudeDebuggerPrint('''crudeDebugger.py:19  	        fn =  os.path.join(debug_output_directory, 'output') ''')
        fn =  os.path.join(debug_output_directory, 'output')
        crudeDebuggerPrint('''crudeDebugger.py:20  	        crudeDebuggerOutputFile = open(fn, 'w') ''')
        crudeDebuggerOutputFile = open(fn, 'w')
    crudeDebuggerPrint('''crudeDebugger.py:21  	    crudeDebuggerOutputFile.write(txt+epilogue) ''')
    crudeDebuggerOutputFile.write(txt+epilogue)
    crudeDebuggerPrint('''crudeDebugger.py:22  	    crudeDebuggerOutputFile.flush() ''')
    crudeDebuggerOutputFile.flush()
    

def printingDebugging( pythonFile, debugExt='_crudeDebugging.py'  ):
    crudeDebuggerPrint('''crudeDebugger.py:26  	    #headers = [] #i.e. [class , function, loop, ... #nah no nessary for now ''')
    #headers = [] #i.e. [class , function, loop, ... #nah no nessary for now
    crudeDebuggerPrint('''crudeDebugger.py:27  	    assert pythonFile.endswith('.py') ''')
    assert pythonFile.endswith('.py')
    crudeDebuggerPrint('''crudeDebugger.py:28  	    output = ['from crudeDebugger import crudeDebuggerPrint' ] ''')
    output = ['from crudeDebugger import crudeDebuggerPrint' ]
    crudeDebuggerPrint('''crudeDebugger.py:29  	    insideTextblock = False ''')
    insideTextblock = False
    crudeDebuggerPrint('''crudeDebugger.py:30  	    bracketBalance = 0 ''')
    bracketBalance = 0
    crudeDebuggerPrint('''crudeDebugger.py:31  	    bB2 = 0 #for ''' +"'''" +''' special bracket case ''')
    bB2 = 0 #for ''' special bracket case
    for lineNo, line in enumerate(open(pythonFile)):
        indent = line[: len(line)-len(line.lstrip())]
        prev_bracketBalance = bracketBalance
        bracketBalance = prev_bracketBalance + line.count('(') - line.count(')') + line.count('{') - line.count('}') 
        prev_bB2 = bB2
        bB2 = (prev_bB2 + line.count("'''"))%2
        crudeDebuggerPrint('''crudeDebugger.py:38  	        if len(line.strip()) == 0: ''')
        if len(line.strip()) == 0:
            crudeDebuggerPrint('''crudeDebugger.py:39  	            pass ''')
            pass
        elif line.strip().startswith("'''"):
            insideTextblock = not insideTextblock 
            if insideTextblock:
                pass
        elif insideTextblock:
            pass
        elif any( line.lstrip().startswith(s) for s in ['elif','def','class','else','"',"'"] ):
            pass
        elif prev_bB2 <> 0:
            pass
        elif prev_bracketBalance == 0: #and bracketBalance == 0:
            lineCleaned = line.rstrip().replace("'''", "''' +" + '"' + "'''" + '"' + " +'''")

            output.append('%scrudeDebuggerPrint(%s%s:%i  \t%s %s)' % (indent,"'''", pythonFile, lineNo, lineCleaned, "'''"))
        output.append(line[:-1]) #remove \n caracter

    output_fn = os.path.join(debug_output_directory, pythonFile[:-3] + debugExt)
    f = open(output_fn,'w')
    f.write('\n'.join(output))
    f.close()


        
if __name__ == '__main__':
    print('testing crudeDebugger for Dimensioning module')
    printingDebugging('crudeDebugger.py')