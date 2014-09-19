from numpy import matrix
from numpy import array
import math

# Ports 1 2 3 4 are + - D C
def MixedModeConverter():
    MMCM=matrix([[0,0,1,1],[0,0,-1,1],[1,-1,0,0],[1,1,0,0]])/math.sqrt(2.0)
    return array(MMCM).tolist()
