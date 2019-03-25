class ErrorTerms(object):
...
    def ExCalibration(self,b2a1,n,m):
        [_,Et,El]=self[n][m]
        Ex=b2a1
        self[n][m]=[Ex,Et,El]
        return self
...
