class SParameters(SParameterManipulation):
    def __init__(self,f,data,Z0=50.0):
        self.m_parameterType='S'; self.m_d=data; self.m_Z0=Z0
        self.m_f=FrequencyList(f)
        if not data is None:
            if len(data)>0: self.m_P=len(data[0])
        else:
            mat=self[0]
            if not mat is None: self.m_P=len(mat[0])
    def __getitem__(self,item): return self.m_d[item]
    def __len__(self): return len(self.m_f)
    def f(self): return self.m_f
    def Response(self,ToP,FromP): return [mat[ToP-1][FromP-1] for mat in self]
    def FrequencyResponse(self,ToP,FromP):
        return FrequencyResponse(self.f(),self.Response(ToP,FromP))
    def Text(self,formatString=None):
        lines=[]; freqMul = 1e6; fToken = 'MHz'; cpxType = 'MA'; Z0 = 50.0
        if not formatString is None:
            lineList = str.lower(formatString).split('!')[0].split()
            if len(lineList)>0:
                if 'hz' in lineList: fToken = 'Hz'; freqMul = 1.0
                if 'khz' in lineList: fToken = 'KHz'; freqMul = 1e3
                if 'mhz' in lineList: fToken = 'MHz'; freqMul = 1e6
                if 'ghz' in lineList: fToken = 'GHz'; freqMul = 1e9
                if 'ma' in lineList: cpxType = 'MA'
                if 'ri' in lineList: cpxType = 'RI'
                if 'db' in lineList: cpxType = 'DB'
                if 'r' in lineList: Z0=float(lineList[lineList.index('r')+1])
        for lin in self.header: lines.append(
            ('! '+lin if ((len(lin) > 0) and (lin[0] != '!')) else lin)+'\n')
        lines.append('# '+fToken+' '+self.m_parameterType+' '+cpxType+' R '+str(Z0)+'\n')
        for n in range(len(self.m_f)):
            line=[str(self.m_f[n]/freqMul)]
            mat=self[n]
            if Z0 != self.m_Z0: mat=ReferenceImpedance(mat,Z0,self.m_Z0)
            if self.m_P == 2: mat=array(mat).transpose().tolist()
            def phase(value):
                ph=cmath.phase(val)
                if ph == -math.pi: ph=math.pi
                return ph
            for r in range(self.m_P):
                for c in range(self.m_P):
                    val = mat[r][c]
                    if cpxType == 'MA':
                        line.append(str(round(abs(val),digits)))
                        line.append(str(round(phase(val)*180./math.pi,digits)))
                    elif cpxType == 'RI':
                        line.append(str(round(val.real,digits)))
                        line.append(str(round(val.imag,digits)))
                    elif cpxType == 'DB':
                        line.append(str(round(20*math.log10(abs(val)),digits)))
                        line.append(str(round(phase(val)*180./math.pi,digits)))
            pline = ' '.join(line)+'\n'
            lines.append(pline)
        return lines
    def WriteToFile(self,name,formatString=None):
        lines=self.Text(formatString)
        with open(name,'w') as f:
            f.writelines(lines)
        return self
...
