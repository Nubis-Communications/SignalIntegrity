import cmath
import math
# transmission line
#
#           +-----------------------+
#          / \                       \
#         |   |                       |
#   1 ----+-  |     Z    Td           +----- 2
#         |   |                       |
#          \ /                       /
#        +--+-----------------------+--+
#        |                             |
#   3 ---+                             +---- 4
#
#
# is either two or four ports
# ports 1 and 2 are the input and output
# ports 3 and 4 are the outer conductor
# when two ports, ports 3 and 4 are assumed grounded

def TLineFourPort(Zc,gamma,f,Z0):
    a=(Zc-2.*Z0)/(Zc+2.*Z0)
    Y=cmath.exp(-1j*2.*math.pi*f*gamma)
    D=2.*(1-Y*Y*a*a)
    S1=(1.-Y*Y*a*a+a*(1-Y*Y))/D
    S2=(1-a*a)*Y/D
    S3=((1-Y*Y*a*a)-a*(1-Y*Y))/D
    return [[S1,S2,S3,-S2],
            [S2,S1,-S2,S3],
            [S3,-S2,S1,S2],
            [-S2,S3,S2,S1]]