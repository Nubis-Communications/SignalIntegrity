def Matrix2LaTeX(M):
    R = len(M)
    C = len(M[0])
    line='\\left(\\begin{array}{'+'c'*C+'}'
    for r in range(R):
        if r > 0:
            line = line + '\\\\'
        for c in range(C):
            if c>0:
                line=line+' & '
            val = M[r][c]
            if isinstance(val,int):
                data = str(val)
            elif isinstance(val,float):
                data = str(val)
            elif isinstance(val,complex):
                data = str(val.real)+'j'+float(val.imag)
            else:
                data = val
                subscripted=data.split('_')
                if len(subscripted) == 2:
                    data=subscripted[0]+'_{'+subscripted[1]+'}'
            line=line+data
    line = line + '\\end{array}\\right)'
    return line

import unittest

class TestMatrix2LaTeX(unittest.TestCase):
    def testSimple(self):
        print Matrix2LaTeX([[1,2,3],[4,5,6],[7,8,9]])
        pass
    def testSubscripted(self):
        print Matrix2LaTeX([['S_11','S_12'],['S_21','S_22']])
        pass

if __name__ == '__main__':
    unittest.main()

