import unittest
import SignalIntegrity as si
from numpy import empty
import os
from TestHelpers import *

class TestResponse(unittest.TestCase,SParameterCompareHelper):
    def testResampleResponseCompareSpline(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        newf=si.sp.EvenlySpacedFrequencyList(100*100e6,100)
        tdsp=si.sp.File('TestDut.s4p')
        tdspres1=si.sp.ResampledSParameters(tdsp,newf)

        tdresp = [[tdsp.Response(o+1,i+1) for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]
        tdrespf = tdsp.f()

        tdrespres = [[si.sp.ResampledFrequencyResponse(si.sp.FrequencyResponse(tdrespf,tdresp[o][i]),newf)
            for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]

        tddres2=[empty((tdsp.m_P,tdsp.m_P)).tolist() for np in range(len(newf))]
        for np in range(len(newf)):
            for o in range(len(tdrespres)):
                for i in range(len(tdrespres[0])):
                    tddres2[np][o][i]=tdrespres[o][i][np]

        tdspres2 = si.sp.SParameters(newf,tddres2)

##        tdspres1.WriteToFile('tdspres1spline.s4p')
##        tdspres2.WriteToFile('tdspres2spline.s4p')
        self.assertTrue(self.SParametersAreEqual(tdspres1,tdspres2,0.001),self.id()+'result not same')
    def testResampleResponseCompareCZT(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        newf=si.sp.EvenlySpacedFrequencyList(100*100e6,100)
        tdsp=si.sp.File('TestDut.s4p')
        tdspres1=si.sp.ResampledSParameters(tdsp,newf,method='czt',adjustDelay=False)

        tdresp = [[tdsp.Response(o+1,i+1) for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]
        tdrespf = tdsp.f()

        tdrespres = [[si.sp.ResampledFrequencyResponse(si.sp.FrequencyResponse(tdrespf,tdresp[o][i]),newf,method='czt',adjustDelay=True)
            for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]

        tddres2=[empty((tdsp.m_P,tdsp.m_P)).tolist() for np in range(len(newf))]
        for np in range(len(newf)):
            for o in range(len(tdrespres)):
                for i in range(len(tdrespres[0])):
                    tddres2[np][o][i]=tdrespres[o][i][np]

        tdspres2 = si.sp.SParameters(newf,tddres2)

##        tdspres1.WriteToFile('tdspres1czt.s4p')
##        tdspres2.WriteToFile('tdspres2czt.s4p')
        self.assertTrue(self.SParametersAreEqual(tdspres1,tdspres2,0.001),self.id()+'result not same')
    def testResampleResponseCompareCZT2(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        newf=si.sp.EvenlySpacedFrequencyList(100*100e6,100)
        tdsp=si.sp.File('TestDut.s4p')
        tdspres1=si.sp.ResampledSParameters(tdsp,newf,method='czt')

        tdresp = [[tdsp.Response(o+1,i+1) for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]
        tdrespf = tdsp.f()

        tdrespres = [[si.sp.FrequencyResponse(tdrespf,tdresp[o][i]).Resample(newf,method='czt')
            for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]

        tddres2=[empty((tdsp.m_P,tdsp.m_P)).tolist() for np in range(len(newf))]
        for np in range(len(newf)):
            for o in range(len(tdrespres)):
                for i in range(len(tdrespres[0])):
                    tddres2[np][o][i]=tdrespres[o][i][np]

        tdspres2 = si.sp.SParameters(newf,tddres2)

##        tdspres1.WriteToFile('tdspres1czt2.s4p')
##        tdspres2.WriteToFile('tdspres2czt2.s4p')
        self.assertTrue(self.SParametersAreEqual(tdspres1,tdspres2,0.001),self.id()+'result not same')
    def testArrayOfMatrices(self):
        data=si.sp.ArrayOfMatrices([[[1,2],[3,4]],[[5,6],[7,8]],[[9,10],[11,12]]])
        data2=si.sp.MatrixOfArrays(data)
        data3=si.sp.ArrayOfMatrices(data2)
        f=[1,2,3]
        f2=si.sp.FrequencyList(f)
        f3=si.sp.FrequencyList(f2)
        pass
    def testResampleResponseCompareSpline2(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        newf=si.sp.EvenlySpacedFrequencyList(100*100e6,100)
        tdsp=si.sp.File('TestDut.s4p')
        tdspres1=si.sp.ResampledSParameters(tdsp,newf,way='newway')

        tdresp = si.sp.ArrayOfMatrices(tdsp.Data()).MatrixOfArrays()
        tdrespf = tdsp.f()

        for r in range(tdresp.NumRows()):
            for c in range(tdresp.NumCols()):
                tdresp.SetArray(r,c,si.sp.ResampledFrequencyResponse(si.sp.FrequencyResponse(tdrespf,tdresp.GetArray(r,c)),newf).Response())

        tddres2=tdresp.ArrayOfMatrices()

        tdspres2 = si.sp.SParameters(newf,tddres2)

##        tdspres1.WriteToFile('tdspres1spline2.s4p')
##        tdspres2.WriteToFile('tdspres2spline2.s4p')
        self.assertTrue(self.SParametersAreEqual(tdspres1,tdspres2,0.001),self.id()+'result not same')

    def testResampleResponseCompareSpline3(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        newf=si.sp.EvenlySpacedFrequencyList(100*100e6,100)
        tdsp=si.sp.File('TestDut.s4p')
        tdspres1=si.sp.ResampledSParameters(tdsp,newf)

        tdresp = si.sp.ArrayOfMatrices(tdsp.Data())
        tdrespf = tdsp.f()

        tddres2=si.sp.EmptyArrayOfMatrices(4,4,len(newf))

        for r in range(tdresp.NumRows()):
            for c in range(tdresp.NumCols()):
                tddres2.SetArray(r,c,si.sp.ResampledFrequencyResponse(si.sp.FrequencyResponse(tdrespf,tdresp.GetArray(r,c)),newf).Response())

        tdspres2 = si.sp.SParameters(newf,tddres2)

##        tdspres1.WriteToFile('tdspres1spline3.s4p')
##        tdspres2.WriteToFile('tdspres2spline3.s4p')
        self.assertTrue(self.SParametersAreEqual(tdspres1,tdspres2,0.001),self.id()+'result not same')
    def testResampleResponseFilter(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        filtersp=si.sp.File('filter.s2p')
        filtersp=si.sp.ResampledSParameters(filtersp,si.sp.EvenlySpacedFrequencyList(2e9,200),method='spline')
        filterres=si.sp.ResampledSParameters(filtersp,si.sp.EvenlySpacedFrequencyList(2e9,4000),method='czt')
        if not os.path.exists('filterres.s2p'):
            filterres.WriteToFile('filterres.s2p')
        regression=si.sp.File('filterres.s2p')
        self.assertTrue(self.SParametersAreEqual(filterres,regression,0.001),self.id()+'result not same')

if __name__ == '__main__':
    unittest.main()