class ErrorTerms(object):
...
    def _EnforceReciprocity(self,A,B):
        P=len(A); Pr=range(P); M=[[None for _ in Pr] for _ in Pr]
        for c in Pr:
            for r in Pr:
                M[r][c]=M[c][r] if r < c else r-c+(0 if c==0 else M[P-1][c-1]+1)
        L=[[0. for c in range(P*(P+1)//2)] for r in range(P*P)]
        b=[None for r in range(P*P)]
        for r in Pr:
            for c in Pr:
                b[r*P+c]=[B[r][c]]
                for p in Pr: L[p*P+r][M[p][c]]=A[c][r]
        sv=(pinv(array(L)).dot(array(b))).tolist()
        S=[[sv[M[r][c]][0] for c in Pr] for r in Pr]
        return S
...
