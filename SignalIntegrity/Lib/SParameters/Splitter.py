import SignalIntegrity.Lib as si
import matplotlib.pyplot as plt
import math
import cmath
import numpy as np

class CTwoPortSplitter:
    def __init__(self,CombinedFilename,timeForLeft,port1,port2,ResultFilename,AssumeFullSymmetry = True,timeForRight = 0.0,ResultFilenameRight=''):
        self.m_sp = si.sp.SParameterFile(CombinedFilename)
        self.m_Tl = timeForLeft
        self.m_Tr = timeForRight
        self.m_Z0 = 50.0
        
        if AssumeFullSymmetry:
            self.SplitLarryMethodAssumingFullSymmetry(port1,port2,ResultFilename,ResultFilenameRight)
        else:
            self.SplitLarryMethodAssumingSameLoss(port1,port2,ResultFilename,ResultFilenameRight)
      
        #0. SL11 from chopped impulse response 
        #1. SL11 + SL22*S21 = S11
        #2. SL21^2/(1 - SL22 ^2) = S21
                
        
        print 'done'

    def SplitLarryMethodAssumingFullSymmetry(self,port1, port2, ResultFilenameLeft,ResultFilenameRight):
        
        S11 =  self.m_sp.FrequencyResponse(port1,port1)
        S21 = self.m_sp.FrequencyResponse(port2,port1)
        S22 =  self.m_sp.FrequencyResponse(port2,port2)
        S12 = self.m_sp.FrequencyResponse(port1,port2)
        
         # make it reciprocal
        S21reciprocalList = [(S21.Values()[n] + S12.Values()[n])*0.5 for n in range(len(S21))]
        
        f = S11.Frequencies()
        S21angle = np.unwrap(np.angle(np.array(S21reciprocalList)))
        diffangle = [S21angle[n] - S21angle[n-1] for n in range(1,len(f))]
        df = f[1]-f[0]
        GD = [-d/(2*math.pi*df) for d in diffangle]
        Gdelay = np.mean(GD[1000:2000])
        
        if(False):
            plt.plot(GD)
            plt.plot([Gdelay for n in range(len(GD))])
            plt.show()
            print Gdelay

        ip = si.ImpedanceProfile.ImpedanceProfileWaveform(self.m_sp,port1,method = 'estimated',includePortZ=False)
        
        Zline = ip.Values()[-1]
        plt.plot(ip.Times(),ip.Values())
        plt.show()
        
        Sr = [si.cvt.ReferenceImpedance(S=[[S11[n],S21reciprocalList[n]],[S21reciprocalList[n],S22[n]]], Z0f=Zline) for n in range(len(S11))]

        self.m_spOriginal = self.m_sp
         
        self.m_Tl = 2.0*self.m_Tl
        self.m_sp = si.sp.SParameters(S11.Frequencies(),Sr)
         
        self.SplitImpulseResponseAssumingFullSymmetry(1,2,'')
        
        Slr = [si.cvt.ReferenceImpedance(S=[[self.m_SL[n][0][0],self.m_SL[n][0][1]],[self.m_SL[n][1][0],self.m_SL[n][1][1]]], Z0f=self.m_Z0,Z0i=Zline) for n in range(len(S11))]
         
        si.sp.SParameters(S11.Frequencies(),Slr).WriteToFile(ResultFilenameLeft)
        
    def SplitLarryMethodAssumingSameLoss(self,port1, port2, ResultFilenameLeft,ResultFilenameRight):
        
        S11 =  self.m_sp.FrequencyResponse(port1,port1)
        S21 = self.m_sp.FrequencyResponse(port2,port1)
        S22 =  self.m_sp.FrequencyResponse(port2,port2)
        S12 = self.m_sp.FrequencyResponse(port1,port2)
        
         # make it reciprocal
        S21reciprocalList = [(S21.Values()[n] + S12.Values()[n])*0.5 for n in range(len(S21))]
        
        f = S11.Frequencies()
        S21angle = np.unwrap(np.angle(np.array(S21reciprocalList)))
        diffangle = [S21angle[n] - S21angle[n-1] for n in range(1,len(f))]
        df = f[1]-f[0]
        GD = [-d/(2*math.pi*df) for d in diffangle]
        Gdelay = np.mean(GD[1000:2000])
        
        if(False):
            plt.plot(GD)
            plt.plot([Gdelay for n in range(len(GD))])
            plt.show()
            print Gdelay

        ip = si.ImpedanceProfile.ImpedanceProfileWaveform(self.m_sp,port1,method = 'estimated',includePortZ=False)
        
        Zline = ip.Values()[-1]
        if(False):
            plt.plot(ip.Times(),ip.Values())
            plt.show()
        
        Sr = [si.cvt.ReferenceImpedance(S=[[S11[n],S21reciprocalList[n]],[S21reciprocalList[n],S22[n]]], Z0f=Zline) for n in range(len(S11))]

        self.m_spOriginal = self.m_sp
         
        self.m_Tl = 2.0*self.m_Tl
        self.m_Tr = 2.0*self.m_Tr
        
        #self.m_sp = si.sp.SParameters(S11.Frequencies(),Sr)
         
        self.SplitImpulseResponseAssumingIdenticalLosses(1,2,'','')
        
        Slr = [si.cvt.ReferenceImpedance(S=[[self.m_SL[n][0][0],self.m_SL[n][0][1]],[self.m_SL[n][1][0],self.m_SL[n][1][1]]], Z0f=self.m_Z0,Z0i=Zline) for n in range(len(S11))]
        
        SRr = [si.cvt.ReferenceImpedance(S=[[self.m_SR[n][0][0],self.m_SR[n][0][1]],[self.m_SR[n][1][0],self.m_SR[n][1][1]]], Z0f=self.m_Z0,Z0i=Zline) for n in range(len(S11))]
         
        si.sp.SParameters(S11.Frequencies(),Slr).WriteToFile(ResultFilenameLeft)
        
        si.sp.SParameters(S11.Frequencies(),SRr).WriteToFile(ResultFilenameRight)
        
    def SplitImpulseResponseAssumingFullSymmetry(self,port1,port2,Resultfilename):
       
        ir = self.m_sp.FrequencyResponse(port1,port1).ImpulseResponse()
        
        bPlot = True
        if bPlot:
            plt.plot(ir.Times(),ir.Values())
            plt.title('impulse response')
            
        f=self.m_sp.f()
        ts11L = ir.Values()
        for n in range(len(ir)):
            if(ir.Times()[n] > self.m_Tl):
                ts11L[n] = 0.0       
        
        
        if bPlot:
            plt.plot(ir.Times(),ts11L)
            plt.title('impulse response')
            plt.show()
        
        irS11L = si.td.wf.ImpulseResponse(t = ir.td,td = ts11L)
        S11Lfr = irS11L.FrequencyResponse().Resample(f)
     
         
        S11 = self.m_sp.FrequencyResponse(port1,port1)
        S21 = self.m_sp.FrequencyResponse(port2,port1)
         
        S22L = [(S11[n] - S11Lfr[n])/S21[n] for n in range(len(S11))]
         
        S21L_2 = [S21[n]*(1 - S22L[n]*S22L[n]) for n in range(len(S11))]
        p = np.angle(np.array(S21L_2))
        uwp = np.unwrap(p)
         
        S21L = [np.sqrt(abs(S21L_2[n]))*np.exp(1j*uwp[n]/2) for n in range(len(S21L_2))]
         
        bPlot = False
        if bPlot:
            plt.plot(S11Lfr.Frequencies(),S11Lfr.Values('dB'))
            #plt.plot(S11Lfr.Frequencies(),S11LdB)
            plt.plot(self.m_sp.f(),self.m_sp.FrequencyResponse(1,1).Values('dB'))
            plt.title('frequency response')
            plt.show()
         
         
        mat = [[[S11Lfr.Values()[n],S21L[n]],[S21L[n],S22L[n]]] for n in range(len(S21L))] 
       
        self.m_SL = si.sp.SParameters(S11Lfr.Frequencies(),mat)
        
        if(len(Resultfilename) > 0):        
            self.m_SL.WriteToFile(Resultfilename)
        
    def SplitImpulseResponseAssumingIdenticalLosses(self,port1,port2,Resultfilename,ResultfilenameRight):
        
        ir = self.m_sp.FrequencyResponse(port1,port1).ImpulseResponse()
        ir.WriteToFile("c:\\temp\\py_tdinput_11.txt")
        
        bPlot = False
        if bPlot:
            plt.plot(ir.Times(),ir.Values())
            plt.title('impulse response')
            
        f=self.m_sp.f()
        ts11L = ir.Values()
        for n in range(len(ir)):
            if(ir.Times()[n] > self.m_Tl):
                ts11L[n] = 0.0       
        
        
        if bPlot:
            plt.plot(ir.Times(),ts11L)
            plt.title('impulse response')
            plt.show()
        
        irS11L = si.td.wf.ImpulseResponse(t = ir.td,td = ts11L)
        irS11L.WriteToFile("c:\\temp\py_t11.txt")
        S11Lfr = irS11L.FrequencyResponse().Resample(f)
     
        ir2 = self.m_sp.FrequencyResponse(port2,port2).ImpulseResponse()
        ir.WriteToFile("c:\\temp\\py_tdinput_22.txt")
        
        if bPlot:
            plt.plot(ir2.Times(),ir2.Values())
            plt.title('impulse response 2')
            
        ts22R = ir2.Values()
        for n in range(len(ir2)):
            if(ir2.Times()[n] > self.m_Tr):
                ts22R[n] = 0.0       
        
        
        if bPlot:
            plt.plot(ir2.Times(),ts22R)
            plt.title('impulse response 2')
            plt.show()
        
        irS22R = si.td.wf.ImpulseResponse(t = ir2.td,td = ts22R)
        irS22R.WriteToFile("c:\\temp\\py_t22r.txt")
        S22Rfr = irS22R.FrequencyResponse().Resample(f)
        
         
        S11 = self.m_sp.FrequencyResponse(port1,port1)
        S22 = self.m_sp.FrequencyResponse(port2,port2)
        S21 = self.m_sp.FrequencyResponse(port2,port1)
         
        S22L = [(S22[n] - S22Rfr[n])/S21[n] for n in range(len(S11))]
        S11R = [(S11[n] - S11Lfr[n])/S21[n] for n in range(len(S11))]
        si.fd.FrequencyResponse(f,S22L).WriteToFile("c:\\temp\\py_S22L.txt")
        si.fd.FrequencyResponse(f,S11R).WriteToFile("c:\\temp\\py_S11R.txt")
         
        S21L_2 = [S21[n]*(1 - S22L[n]*S11R[n]) for n in range(len(S11))]
        si.fd.FrequencyResponse(f,S21L_2).WriteToFile("c:\\temp\\py_S21LSquared.txt")
        p = np.angle(np.array(S21L_2))
        uwp = np.unwrap(p)
         
        S21L = [np.sqrt(abs(S21L_2[n]))*np.exp(1j*uwp[n]/2) for n in range(len(S21L_2))]
         
      
        if bPlot:
            plt.plot(S11Lfr.Frequencies(),S11Lfr.Values('dB'))
            #plt.plot(S11Lfr.Frequencies(),S11LdB)
            plt.plot(self.m_sp.f(),self.m_sp.FrequencyResponse(1,1).Values('dB'))
            plt.title('frequency response')
            plt.show()
         
         
        mat = [[[S11Lfr.Values()[n],S21L[n]],[S21L[n],S22L[n]]] for n in range(len(S21L))] 
       
        self.m_SL = si.sp.SParameters(S11Lfr.Frequencies(),mat)
        
        if(len(Resultfilename) > 0):        
            self.m_SL.WriteToFile(Resultfilename)
        
        matR = [[[S11R[n],S21L[n]],[S21L[n],S22Rfr.Values()[n]]] for n in range(len(S21L))] 
       
        self.m_SR = si.sp.SParameters(S11Lfr.Frequencies(),matR)
        
        if(len(ResultfilenameRight) > 0):        
            self.m_SR.WriteToFile(ResultfilenameRight)

    def SplitAssumingFullSymmetry(self,port1,port2,ResultFilename):
        
        ip = si.ImpedanceProfile.ImpedanceProfileWaveform(self.m_sp,port1,method = 'estimated',includePortZ=False)
        
        t = ip.Times()
        ipLeft = range(len(t))
        for n in range(len(t)):
            if(t[n] > self.m_Tl):
                ipLeft[n] = self.m_Z0
            else:
                ipLeft[n] = ip[n]
        
        bPlot = True
        
        if bPlot:
            plt.plot(t,ip)
            plt.plot(t,ipLeft)
            plt.title('compare impedance profile')
            plt.show()
        
        #convert ipLeft to rho
        rhoS11 = [(z-self.m_Z0)/(z+self.m_Z0) for z in ipLeft]
        
        if bPlot:
            plt.plot(t,rhoS11)
            plt.title('rho from ip')
            plt.show()
        
        rhoWf = si.td.wf.Waveform(ip.td,rhoS11)
        
        diffrhowWf = [(rhoWf[n] - rhoWf[n-1]) if n>0 else rhoWf[n] for n in range(len(rhoWf)) ]
        
        irS11L = si.td.wf.ImpulseResponse(ip.td,diffrhowWf)
        
        if bPlot:
            plt.plot(irS11L.Times(),irS11L)
            plt.title('impulse response')
            plt.show()
        
        
        S11Lfr = irS11L.FrequencyResponse().Resample(self.m_sp.f())
        
        # I believe S11Lfr is the S11L - I don't have to do the math shown below
        S11L = [s*2.0 - 1.0 for s in S11Lfr.Values()]
        
        S11LdB = [20.0*math.log10(abs(s)) for s in S11L]
        
        S11 = self.m_sp.FrequencyResponse(port1,port1)
        S21 = self.m_sp.FrequencyResponse(port2,port1)
        
        S22L = [(S11[n] - S11Lfr[n])/S21[n] for n in range(len(S11))]
        
        S21L_2 = [S21[n]*(1 - S22L[n]*S22L[n]) for n in range(len(S11))]
        p = np.angle(np.array(S21L_2))
        uwp = np.unwrap(p)
        
        S21L = [np.sqrt(abs(S21L_2[n]))*np.exp(1j*uwp[n]/2) for n in range(len(S21L_2))]
        
        bPlot = False
        if bPlot:
            plt.plot(S11Lfr.Frequencies(),S11Lfr.Values('dB'))
            #plt.plot(S11Lfr.Frequencies(),S11LdB)
            plt.plot(self.m_sp.f(),self.m_sp.FrequencyResponse(1,1).Values('dB'))
            plt.title('frequency response')
            plt.show()
        
        
        mat = [[[S11Lfr.Values()[n],S21L[n]],[S21L[n],S22L[n]]] for n in range(len(S21L))] 
        self.m_SL = si.sp.SParameters(S11Lfr.Frequencies(),mat)
        
        if(len(ResultFilename) > 0):        
            self.m_SL.WriteToFile(ResultFilename)
    
    def SplitAssumingS21LSameAsS21R(self,port1,port2,timeForRight, ResultFilename,ResultFilenameRight):
        
        ip = si.ImpedanceProfile.ImpedanceProfileWaveform(self.m_sp,port1,method = 'estimated',includePortZ=False)
        
        t = ip.Times()
        ipLeft = range(len(t))
        for n in range(len(t)):
            if(t[n] > self.m_Tl):
                ipLeft[n] = self.m_Z0
            else:
                ipLeft[n] = ip[n]
        
        ip2 = si.ImpedanceProfile.ImpedanceProfileWaveform(self.m_sp,port2,method = 'estimated',includePortZ=False)
        
        t = ip2.Times()
        ipRight = range(len(t))
        for n in range(len(t)):
            if(t[n] > timeForRight):
                ipRight[n] = self.m_Z0
            else:
                ipRight[n] = ip2[n]
                
        bPlot = False
        
        if bPlot:
            plt.plot(t,ip)
            plt.plot(t,ipLeft)
            plt.title('compare impedance profile')
            plt.show()
        
        #convert ipLeft to rho
        rhoS11 = [(z-self.m_Z0)/(z+self.m_Z0) for z in ipLeft]
        
        rhoS22 = [(z-self.m_Z0)/(z+self.m_Z0) for z in ipRight]
        
        if bPlot:
            plt.plot(t,rhoS11)
            plt.title('rho from ip')
            plt.show()
        
        rhoWf = si.td.wf.Waveform(ip.td,rhoS11)
        rhoWf2 = si.td.wf.Waveform(ip2.td,rhoS22)
        
        diffrhowWf = [(rhoWf[n] - rhoWf[n-1]) if n>0 else rhoWf[n] for n in range(len(rhoWf)) ]
        diffrhowWf2 = [(rhoWf2[n] - rhoWf2[n-1]) if n>0 else rhoWf2[n] for n in range(len(rhoWf2)) ]

        
        irS11L = si.td.wf.ImpulseResponse(ip.td,diffrhowWf)
        irS11R = si.td.wf.ImpulseResponse(ip2.td,diffrhowWf2)
        
        if bPlot:
            plt.plot(irS11L.Times(),irS11L)
            plt.title('impulse response')
            plt.show()
        
        
        S11Lfr = irS11L.FrequencyResponse().Resample(self.m_sp.f())
        S11Rfr = irS11R.FrequencyResponse().Resample(self.m_sp.f())
                
        S11 = self.m_sp.FrequencyResponse(port1,port1)
        S21 = self.m_sp.FrequencyResponse(port2,port1)
        S22 = self.m_sp.FrequencyResponse(port2,port2)
        
        S22R = [(S11[n] - S11Lfr[n])/S21[n] for n in range(len(S11))]
        S22L = [(S22[n] - S11Rfr[n])/S21[n] for n in range(len(S11))]
        
        S21L_2 = [S21[n]*(1 - S22L[n]*S22R[n]) for n in range(len(S11))]
        p = np.angle(np.array(S21L_2))
        uwp = np.unwrap(p)
        
        S21L = [np.sqrt(abs(S21L_2[n]))*np.exp(1j*uwp[n]/2) for n in range(len(S21L_2))]
        
        bPlot = False
        if bPlot:
            plt.plot(S11Lfr.Frequencies(),S11Lfr.Values('dB'))
            #plt.plot(S11Lfr.Frequencies(),S11LdB)
            plt.plot(self.m_sp.f(),self.m_sp.FrequencyResponse(1,1).Values('dB'))
            plt.title('frequency response')
            plt.show()
        
        
        matL = [[[S11Lfr.Values()[n],S21L[n]],[S21L[n],S22L[n]]] for n in range(len(S21L))] 
        self.m_SL = si.sp.SParameters(S11Lfr.Frequencies(),matL)
        
        if(len(ResultFilename) > 0):
            self.m_SL.WriteToFile(ResultFilename)

        matR = [[[S11Rfr.Values()[n],S21L[n]],[S21L[n],S22R[n]]] for n in range(len(S21L))] 
        self.m_SR = si.sp.SParameters(S11Rfr.Frequencies(),matR)
        
        if(len(ResultFilenameRight) > 0):
            self.m_SR.WriteToFile(ResultFilenameRight)

class CTestImpulseResponse:
    def __init__(self,sparameterfilename,port1=1,port2=2):
        self.m_sp = si.sp.SParameterFile(sparameterfilename)
        fr = self.m_sp.FrequencyResponse(port2,port1)
        ir = fr.ImpulseResponse()
        ir.WriteToFile(r'c:\temp\ir21.txt')
                 
#assume symmetry for CPW board
# below lines worked and produced good results for CPW fixture        
o = CTwoPortSplitter(r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\second_fixture\3B_4A\resultAfterGatingConnector1234causal_ModeConverted.s4p',157.27e-12,port1 = 1, port2 = 2,ResultFilename = r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\second_fixture\3B_4A\SL_Differential_usingImpulsResponseChop.s2p',AssumeFullSymmetry=False,timeForRight = 157.27e-12,ResultFilenameRight=r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\second_fixture\3B_4A\SR_Differential_usingImpulsResponseChop.s2p' )
o = CTwoPortSplitter(r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\second_fixture\3B_4A\resultAfterGatingConnector1234causal_ModeConverted.s4p',157.47e-12,port1 = 3, port2 = 4,ResultFilename = r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\second_fixture\3B_4A\SL_CommonMode_usingImpulsResponseChop.s2p',AssumeFullSymmetry=False,timeForRight = 157.47e-12,ResultFilenameRight=r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\second_fixture\3B_4A\SR_CommonMode_usingImpulsResponseChop.s2p'  )

# # tip/amplifier connector fixture
# o = CTwoPortSplitter(r'H:\Projects\Probes\xena\larryMeasurement\CPW\GateConnectors\resultAfterGatingConnector1234Causal_ModeConverted.s4p',127.95e-12,port1 = 1, port2 = 2,ResultFilename = r'H:\Projects\Probes\xena\larryMeasurement\CPW\GateConnectors\EyeBallLength\SL_Differential_usingImpulsResponseChop.s2p',AssumeFullSymmetry=False,timeForRight = 127.7e-12,ResultFilenameRight=r'H:\Projects\Probes\xena\larryMeasurement\CPW\GateConnectors\EyeBallLength\SR_Differential_usingImpulsResponseChop.s2p' )
# o = CTwoPortSplitter(r'H:\Projects\Probes\xena\larryMeasurement\CPW\GateConnectors\resultAfterGatingConnector1234Causal_ModeConverted.s4p',128e-12,port1 = 3, port2 = 4,ResultFilename = r'H:\Projects\Probes\xena\larryMeasurement\CPW\GateConnectors\EyeBallLength\SL_CommonMode_usingImpulsResponseChop.s2p',AssumeFullSymmetry=False,timeForRight = 127.75e-12,ResultFilenameRight=r'H:\Projects\Probes\xena\larryMeasurement\CPW\GateConnectors\EyeBallLength\SR_CommonMode_usingImpulsResponseChop.s2p'  )

#o = CTwoPortSplitter(r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\MadeByLarry\Test\PyMixedMode.s4p',121.25225e-12,port1 = 1, port2 = 2,ResultFilename = r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\MadeByLarry\Test\PyMixedMode_SL_Differential_usingImpulsResponseChop.s2p',AssumeFullSymmetry=False,timeForRight = 121.25225e-12,ResultFilenameRight=r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\MadeByLarry\Test\PyMixedMode_SR_Differential_usingImpulsResponseChop.s2p' )
o = CTestImpulseResponse(sparameterfilename=r'H:\Projects\Probes\xena\ProductionFixtureMeasurements\MadeByLarry\Test\PyMixedMode.s4p')
        
        
