class ErrorTerms(object):
...
    def DutCalculation(self,sRaw,pl=None,reciprocal=False):
        P=len(sRaw); Pr=range(P)
        if pl is None: pl = [p for p in Pr]
        B=[[(sRaw[r][c]-self[pl[r]][pl[c]][0])/self[pl[r]][pl[c]][1]
            for c in Pr] for r in  Pr]
        A=[[B[r][c]*self[pl[r]][pl[c]][2]+(1 if r==c else 0) for c in Pr] for r in Pr]
        if not reciprocal: S=(array(B).dot(pinv(array(A)))).tolist()
        else: S=self._EnforceReciprocity(A,B)
        return S
...
    def DutUnCalculation(self,S,pl=None):
        if pl is None: pl = [p for p in range(len(S))]
        Sp=[[None for c in range(len(S))] for r in range(len(S))]
        Si=pinv(array(S))
        for c in range(len(S)):
            E=self.Fixture(c,pl)
            Em=[[array(E[0][0]),array(E[0][1])],[array(E[1][0]),array(E[1][1])]]
            col=(Em[0][0].dot(Em[1][0])+Em[0][1].dot(
                pinv(Si-Em[1][1])).dot(Em[1][0])).tolist()
            for r in range(len(S)): Sp[r][c]=col[r][c]
        return Sp
