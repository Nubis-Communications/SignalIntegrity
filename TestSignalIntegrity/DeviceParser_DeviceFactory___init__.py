class DeviceFactory(object):
    def __init__(self):
        self.deviceList=[
        ParserDevice('file',None,True,{'':None},True,"File(arg['']).Resample(f)"),
        ParserDevice('c',1,True,{'':None},True,"TerminationC(f,float(arg['']))"),
        ParserDevice('c',2,True,{'':None},True,"SeriesC(f,float(arg['']))"),
        ParserDevice('l',1,True,{'':None},True,"TerminationL(f,float(arg['']))"),
        ParserDevice('l',2,True,{'':None},True,"SeriesL(f,float(arg['']))"),
        ParserDevice('r',1,True,{'':None},False,"TerminationZ(float(arg['']))"),
        ParserDevice('r',2,True,{'':None},False,"SeriesZ(float(arg['']))"),
        ParserDevice('shunt','2-4',True,{'':None},False,
                     "ShuntZ(ports,float(arg['']))"),
        ParserDevice('m',4,True,{'':None},True,"Mutual(f,float(arg['']))"),
        ParserDevice('ground',1,False,{},False,"Ground()"),
        ParserDevice('open',1,False,{},False,"Open()"),
        ParserDevice('thru',2,False,{},False,"Thru()"),
        ParserDevice('termination',None,False,{},False,
                     "zeros(shape=(ports,ports)).tolist()"),
        ParserDevice('tee',None,False,{},False,"Tee(ports)"),
        ParserDevice('mixedmode',4,True,{'':'power'},False,
                     "(MixedModeConverterVoltage() if arg[''] == 'voltage'\
                      else MixedModeConverter())"),
        ParserDevice('idealtransformer',4,True,{'':1.},False,
                     "IdealTransformer(float(arg['']))"),
        ParserDevice('voltagecontrolledvoltagesource',4,True,{'':None},False,
                     "VoltageControlledVoltageSource(float(arg['']))"),
        ParserDevice('currentcontrolledcurrentsource',4,True,{'':None},False,
                     "CurrentControlledCurrentSource(float(arg['']))"),
        ParserDevice('currentcontrolledvoltagesource',4,True,{'':None},False,
                     "CurrentControlledVoltageSource(float(arg['']))"),
        ParserDevice('voltagecontrolledcurrentsource',4,True,{'':None},False,
                     "VoltageControlledCurrentSource(float(arg['']))"),
        ParserDevice('voltageamplifier','2-4',False,{'gain':None,'zo':0,'zi':1e8,
                    'z0':50.},False,"VoltageAmplifier(ports,float(arg['gain']),\
                     float(arg['zi']),float(arg['zo']))"),
        ParserDevice('currentamplifier','2-4',False,{'gain':None,'zo':1e8,'zi':0,
                    'z0':50.},False,"CurrentAmplifier(ports,float(arg['gain']),\
                    float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transresistanceamplifier','2-4',False,{'gain':None,'zo':0.,
                    'zi':0.,'z0':50.},False,"TransresistanceAmplifier(ports,\
                    float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transconductanceamplifier','2-4',False,{'gain':None,'zo':1e8,
                    'zi':1e8,'z0':50.},False,"TransconductanceAmplifier(ports,\
                    float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('tline','2,4',False,{'zc':50.,'td':0.},True,
                     "TLine(f,ports,float(arg['zc']),float(arg['td']))"),
        ParserDevice('telegrapher',2,False,{'r':0.,'l':0.,'c':0.,'g':0.,'z0':50.,
                    'sect':1},True,"ApproximateTwoPortTLine(f, float(arg['r']),\
                    float(arg['l']),float(arg['g']),float(arg['c']),float(arg['z0']),\
                    int(arg['sect']))"),
        ParserDevice('telegrapher',4,False,{'rp':0.,'lp':0.,'cp':0.,'gp':0.,'rn':0.,
                    'ln':0.,'cn':0.,'gn':0.,'lm':0.,'cm':0.,'gm':0.,'z0':50.,'sect':1},
                     True,"ApproximateFourPortTLine(f, float(arg['rp']),\
                     float(arg['lp']),float(arg['cp']),float(arg['gp']),\
                     float(arg['rn']),float(arg['ln']),float(arg['cn']),\
                     float(arg['gn']),float(arg['lm']),float(arg['cm']),\
                     float(arg['gm']),float(arg['z0']),int(arg['sect']))")
        ]
...
