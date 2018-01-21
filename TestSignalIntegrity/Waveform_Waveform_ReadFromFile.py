class Waveform(object):
    def ReadFromFile(self,fileName):
        with open(fileName,"rU") as f:
            data=f.readlines()
            HorOffset=float(data[0])
            NumPts=int(float(data[1])+0.5)
            SampleRate=float(data[2])
            Values=[float(data[k+3]) for k in range(NumPts)]
        self.m_t=TimeDescriptor(HorOffset,NumPts,SampleRate)
        self.m_y=Values
        return self
    def WriteToFile(self,fileName):
        with open(fileName,"w") as f:
            td=self.TimeDescriptor()
            f.write(str(td.H)+'\n')
            f.write(str(int(td.K))+'\n')
            f.write(str(td.Fs)+'\n')
            for v in self.Values():
                f.write(str(v)+'\n')
        return self
...
