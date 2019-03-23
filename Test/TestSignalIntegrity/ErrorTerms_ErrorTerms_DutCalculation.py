class ErrorTerms(object):
...
    def DutCalculation(self,sRaw,pl=None):
        if pl is None: pl = [p for p in range(len(sRaw))]
        B=[[(sRaw[r][c]-self[pl[r]][pl[c]][0])/self[pl[r]][pl[c]][1]
            for c in range(len(sRaw))] for r in  range(len(sRaw))]
        A=[[B[r][c]*self[pl[r]][pl[c]][2]+(1 if r==c else 0) for c in range(len(sRaw))]
           for r in range(len(sRaw))]
        S=(matrix(B)*matrix(A).getI()).tolist()
        return S