class SParameterFile(SParameters):
    def __init__(self,name,Z0=None,callback=None,**kwargs):
        self.m_sToken='S'
        self.m_Z0=Z0
        self.m_P=int(str.lower(name).split('.')[-1].split('s')[1].split('p')[0])
        freqMul = 1e6
        complexType = 'MA'
        Z0=50.
        sp=True
        self.m_f=[]
        numeric_chunks=[]
        for lineIndex,line in enumerate(spfile):
            line_no_comment = line.split('!')[0]
            stripped = line_no_comment.lstrip()
            if len(stripped)>0:
                if stripped[:1] == '#':
                    lineList = stripped.lower().split()
                    if 'hz' in lineList: freqMul = 1.0
                    if 'khz' in lineList: freqMul = 1e3
                    if 'mhz' in lineList: freqMul = 1e6
                    if 'ghz' in lineList: freqMul = 1e9
                    if 'ma' in lineList: complexType = 'MA'
                    if 'ri' in lineList: complexType = 'RI'
                    if 'db' in lineList: complexType = 'DB'
                    if 'r' in lineList:
                        Z0=float(lineList[lineList.index('r')+1])
                    if not self.m_sToken.lower() in lineList:
                        sp=False
                else:
                    nums = np.fromstring(line_no_comment, sep=' ')
                    if nums.size:
                        numeric_chunks.append(nums)
        if not sp: return
        if self.m_Z0==None: self.m_Z0=Z0
        numbers = np.concatenate(numeric_chunks)\
            if len(numeric_chunks)>0 else np.array([],dtype=float)
        P=self.m_P
        values_per_freq = 1 + P*P*2
        values = numbers.reshape((-1, values_per_freq))
        f = values[:, 0] * freqMul
        raw_pairs = values[:, 1:].reshape((-1, P, P, 2))

        if complexType == 'RI':
            m_d_np = raw_pairs[..., 0] + 1j * raw_pairs[..., 1]
        else:
            angles = np.exp(1j * np.deg2rad(raw_pairs[..., 1]))
            if complexType == 'MA':
                m_d_np = raw_pairs[..., 0] * angles
            elif complexType == 'DB':
                m_d_np = np.power(10.0, raw_pairs[..., 0] / 20.0) * angles

        if P == 2:
            m_d_np = m_d_np.transpose((0, 2, 1))

        self.m_d=m_d_np.tolist()
        if Z0 != self.m_Z0:
            for fi in range(len(self.m_d)):
                self.m_d[fi]=ReferenceImpedance(self.m_d[fi],self.m_Z0,Z0)
        self.m_f=GenericFrequencyList(f.tolist())
