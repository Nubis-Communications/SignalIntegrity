class SParameterManipulation(object):
    def _LargestSingularValues(self):
        return [linalg.svd(m,full_matrices=False,compute_uv=False)[0]
            for m in self.m_d]
    def EnforcePassivity(self,maxSingularValue=1.):
        for n in range(len(self.m_d)):
            (u,s,vh)=linalg.svd(self.m_d[n],full_matrices=1,compute_uv=1)
            for si in range(len(s)): s[si]=min(maxSingularValue,s[si])
            self.m_d[n]=dot(u,dot(diag(s),vh)).tolist()
        return self
...
