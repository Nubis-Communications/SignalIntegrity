class Waveform(object):
...
    def ReadFromFile(self,fileName):
        try:
            with open(fileName,"rU") as f:
                data=f.readlines()
                HorOffset=float(data[0])
                NumPts=int(data[1])
                SampleRate=float(data[2])
                Values=[float(v) for v in data[3:]]
            self.m_t=TimeDescriptor(HorOffset,NumPts,SampleRate)
            self.m_y=Values
        except IOError:
            raise PySIExceptionWaveformFile(fileName+' not found')
        return self
    def WriteToFile(self,fileName):
        with open(fileName,"w") as f:
            td=self.TimeDescriptor()
            f.write(str(td.H)+'\n')
            f.write(str(int(td.N))+'\n')
            f.write(str(td.Fs)+'\n')
            for v in self.Values():
                f.write(str(v)+'\n')
        return self
...
