'''
Python Code for generating crude debugging functionality for the Dimensioning FreeCAD module.
'''

import os, sys

__dir__ = os.path.dirname(__file__)

debug_output_directory = os.path.join( __dir__ , 'crudeDebugger_output' )
if not os.path.exists(debug_output_directory):
    os.mkdir(debug_output_directory)
sys.path.append(debug_output_directory)

global crudeDebuggerOutputFile
crudeDebuggerOutputFile = None

def crudeDebuggerPrint( txt, epilogue='\n' ):
    global crudeDebuggerOutputFile
    if crudeDebuggerOutputFile == None:
        fn =  os.path.join(debug_output_directory, 'output')
        crudeDebuggerOutputFile = open(fn, 'w')
    crudeDebuggerOutputFile.write(txt+epilogue)
    crudeDebuggerOutputFile.flush()
    

def printingDebugging( pythonFile, debugExt='_crudeDebugging.py'  ):
    #headers = [] #i.e. [class , function, loop, ... #nah no nessary for now
    assert pythonFile.endswith('.py')
    output = ['from crudeDebugger import crudeDebuggerPrint' ]
    insideTextblock = False
    bracketBalance = 0
    bB2 = 0 #for ''' special bracket case
    for lineNo, line in enumerate(open(pythonFile)):
        indent = line[: len(line)-len(line.lstrip())]
        prev_bracketBalance = bracketBalance
        bracketBalance = prev_bracketBalance + line.count('(') - line.count(')') + line.count('{') - line.count('}') + line.count('[') - line.count(']') 
        prev_bB2 = bB2
        bB2 = (prev_bB2 + line.count("'''"))%2
        if len(line.strip()) == 0:
            pass
        elif line.strip().startswith("'''"):
            insideTextblock = not insideTextblock 
            if insideTextblock:
                pass
        elif insideTextblock:
            pass
        elif any( line.lstrip().startswith(s) for s in ['elif','def','class','else','except','"',"'"] ):
            pass
        elif prev_bB2 <> 0:
            pass
        elif prev_bracketBalance == 0: #and bracketBalance == 0:
            lineCleaned = line.rstrip().replace("'''", "''' +" + '"' + "'''" + '"' + " +'''")

            output.append('%scrudeDebuggerPrint(%s%s:%i  \t%s %s)' % (indent,"'''", os.path.basename(pythonFile), lineNo, lineCleaned, "'''"))
        output.append(line[:-1]) #remove \n caracter

    output_fn = os.path.join(debug_output_directory, os.path.basename(pythonFile[:-3]) + debugExt)
    f = open(output_fn,'w')
    f.write('\n'.join(output))
    f.close()


        
if __name__ == '__main__':
    print('testing crudeDebugger for Dimensioning module')
    printingDebugging('crudeDebugger.py')
