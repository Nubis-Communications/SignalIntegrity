class ParserArgs():
    def AssignArguments(self,args):
        self.m_vars=dict()
        if args is None:
            self.m_args=[]
        else:
            args=LineSplitter(args)
            self.m_args = dict([('$'+args[i]+'$',args[i+1])
                for i in range(0,len(args),2)])
    def ReplaceArgs(self,lineList):
        replacedOne=False
        for i in range(len(lineList)):
            if lineList[i] in self.m_vars:
                replacedOne=True
                lineList[i] = self.m_vars[lineList[i]]
        if replacedOne:
            lineList=' '.join(lineList).split()
        return lineList
    def ProcessVariables(self,lineList):
        if lineList[0] == 'var':
            variables=dict([(lineList[i*2+1],lineList[i*2+2])
                for i in range((len(lineList)-1)//2)])
            for key in self.m_args:
                if key in variables:
                    variables[key]=self.m_args[key]
            self.m_vars=dict(list(self.m_vars.items())+list(variables.items()))
            return True
        else:
            return False
