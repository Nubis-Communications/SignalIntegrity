'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Measurement.Calibration.CalibrationMeasurements import Calibration

class SParametersCalculation(SParameters):
    def __init__(self,rawSParameters,calMeasurements):
        self.sm=rawSParameters
        self.ET=calMeasurements.ErrorTerms()
        fList=self.sraw.m_f
        for n in range(len(fList)):
            ET=self.ETMatrix(n)
            SM=self.sm[n]
            SC.append(self.CalcSParams(ET,SM))
    def ETMatrix(self,n):
        N=self.sm.m_P
        EtMatrix=[[[0.0 for _ in range(3)] for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for m in range(N):
                box=self.ET[i][m][n]
                if i==m:    
                    Ed=box[0][0]
                    Er=box[0][1]
                    Es=box[1][1]
                    EtMatrix[i][m]=[Ed,Er,Es]
                else:
                    Ex=0
                    Et=box[1][0]
                    El=box[0][0]
                    EtMatrix[i][m]=[Ex,Et,El]
        return EtMatrix
    def CalcSParams(self,ET,SM):
        N=len(ET)
        Ap=[[0. for _ in range(N)] for _ in range(N)]
        Bp=[[0. for _ in range(N)] for _ in range(N)]
        for m in range(N):
            E = [[0. for _ in range(4*N)] for _ in range(4*N)]
            e=[[0] for _ in range(4*N)]
            b=[[0] for _ in range()]
        