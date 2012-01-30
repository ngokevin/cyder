
import sys
import pdb
def trace():
    tmp = sys.stdout
    sys.stdout = sys.__stdout__
    pdb.set_trace()




