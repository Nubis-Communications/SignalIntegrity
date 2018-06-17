class PeeledLaunches(SParameters):
    def __init__(self,sp,timelen):
        spp=[PeeledPortSParameters(sp,p+1,timelen[p]) for p in range(sp.m_P)]
        sddp=DeembedderParser().AddLine('unknown S '+str(sp.m_P))
        for ps in [str(p+1) for p in range(sp.m_P)]:
            sddp.AddLines(['device D'+ps+' 2','connect D'+ps+' 2 S '+ps,
                           'port '+ps+' D'+ps+' 1'])
        sddn=DeembedderNumeric(sddp.SystemDescription()); spd=[]
        for n in range(len(sp)):
            for p in range(sp.m_P): sddn.AssignSParameters('D'+str(p+1),spp[p][n])
            spd.append(sddn.CalculateUnknown(sp[n]))
        SParameters.__init__(self,sp.m_f,spd)