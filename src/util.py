import codecs
from subprocess import Popen, PIPE

mathematicaPath = "/Applications/Mathematica.app/Contents/MacOS/MathKernel"

def writeFile(filename, contents):
    out = codecs.open(filename, encoding='utf-8', mode='w+')
    out.write(contents)
    out.close()

def readFile(filename):
    fileHandle = codecs.open(filename, encoding='utf-8')
    fileContents = unicode(fileHandle.read())
    fileHandle.close()
    return fileContents

def mathematica(string):
    p = Popen([mathematicaPath], stdin=PIPE, stdout=PIPE)
    p.communicate(string)