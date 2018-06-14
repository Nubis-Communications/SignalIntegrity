def DeembedLaunch(sp,timelen):
    spp=[si.ip.ImpedanceProfileWaveform(sp,port=p+1,
        method='estimated',adjustForDelay=False,includePortZ=False).
            PeeledSParameters(timelen, sp.f())
                for p in range(2)]
    sddn=si.sd.DeembedderNumeric(si.p.DeembedderParser().AddLines(['unknown S 2',
        'device D1 2','device D2 2','connect D1 2 S 1','connect D2 2 S 2',
        'port 1 D1 1 2 D2 1']).SystemDescription())
    spd=[]
    for n in range(len(sp)):
        for p in range(2):
            sddn.AssignSParameters('D'+str(p+1),spp[p][n])
        spd.append(sddn.CalculateUnknown(sp[n]))
    return si.sp.SParameters(sp.f(),spd)
def ZZZDeembedLaunch():
    # ZZZ to make sure it occurs last, since it depends on other measurement
    sp=si.sp.SParameterFile('cableForRLGC.s2p',66e-12)
    dsp=self.DeembedLaunch(sp,66e-12)
    self.SParameterRegressionChecker(dsp, 'TestImpedanceProfile_testPeelCableforRLGC_deembedded.s2p')
def WriteDeembedLaunch():
    self.WriteCode(os.path.basename(__file__).split('.')[0]+'.py', 'DeembedLaunch', [], printFuncName=True)
_name__ == "__main__":
unittest.main()