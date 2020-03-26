class ErrorTerms(object):
...
    def TransferThruCalibration(self):
        didOne=True
        while didOne:
            didOne=False
            for otherPort in range(self.numPorts):
                for drivenPort in range(self.numPorts):
                    if (otherPort == drivenPort):
                        continue
                    if ((self[otherPort][drivenPort][1]==None) and
                        (self[otherPort][drivenPort][2]==None)):
                        for mid in range(self.numPorts):
                            if ((mid != otherPort) and
                                (mid != drivenPort) and
                                ((self[otherPort][mid][1]!=None) or
                                 (self[otherPort][mid][2]!=None)) and
                                ((self[mid][drivenPort][1]!=None) or
                                 (self[mid][drivenPort][2]!=None))):
                                (_,Etl,_)=self[otherPort][mid]
                                (_,Etr,_)=self[mid][drivenPort]
                                (_,Erm,_)=self[mid][mid]
                                (_,_,Eso)=self[otherPort][otherPort]
                                (Ex,Et,El)=self[otherPort][drivenPort]
                                Et=Etl*Etr/Erm
                                El=Eso
                                self[otherPort][drivenPort]=[Ex,Et,El]
                                didOne=True
                                continue
        return self
...
