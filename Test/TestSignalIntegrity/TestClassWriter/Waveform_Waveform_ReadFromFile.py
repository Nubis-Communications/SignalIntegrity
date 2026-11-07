class Waveform(list):
    def ReadFromFile(self,fileName):
        with open(fileName,'rU' if sys.version_info.major < 3 else 'r') as f:
            data=f.readlines()
            HorOffset=float(data[0])
            NumPts=int(float(data[1])+0.5)
            SampleRate=float(data[2])
            Values=[float(data[k+3]) for k in range(NumPts)]
        self.td=TimeDescriptor(HorOffset,NumPts,SampleRate)
        list.__init__(self,Values)
        return self
    def WriteToFile(self,fileName):
        with open(fileName,"w") as f:
            td=self.td
            f.write(str(td.H)+'\n')
            f.write(str(int(td.K))+'\n')
            f.write(str(td.Fs)+'\n')
            for v in self:
                f.write(str(v)+'\n')
        return self
...
