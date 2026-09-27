class ParserDevice(object):
    def __init__(self,devicename,ports,arginname,defaults,frequencyDependent,func):
        self.devicename=devicename
        self.ports=ports
        self.arginname=arginname
        defaults['z0']=50.
        self.defaults=defaults
        self.frequencyDependent=frequencyDependent
        self.func=func

