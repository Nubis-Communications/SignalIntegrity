class SParameterManipulation(object):
    def EnforceReciprocity(self):
        for n in range(len(self.m_d)):
            for r in range(len(self.m_d[n])):
                for c in range(r,len(self.m_d[n])):
                    if c>r:
                        self.m_d[n][r][c]=(self.m_d[n][r][c]+self.m_d[n][c][r])/2.
                        self.m_d[n][c][r]=self.m_d[n][r][c]
        return self
...
