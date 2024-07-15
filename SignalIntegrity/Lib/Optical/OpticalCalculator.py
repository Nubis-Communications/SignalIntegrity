"""
OpticalCalculator.py
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from SignalIntegrity.Lib.ToSI import ToSI

import math

class OpticalParam(dict):
    def __init__(self,name,fixed=False,value=None,unit=None):
        dict.__init__(self,{'name':name,'fixed':fixed,'value':value,'unit':unit})

class OpticalCalculator(dict):
    """Optical Measurements Calculator
    This class enables optical measurements attributed to optical modulators.
    The simplest usage of the optical calculator is like this:

    params = OpticalCalculator('PindBm',7.17,'IILdB',2.0,'ILdB',2.87,'ERdB',4.63).Result()

    This results in params containing a dictionary of calculated results like this:

    params = {'PindBm': 7.17, 'PinW': 0.005212, 'ILdB': 2.87, 'IL': 1.936422, 'ERdB': 4.63, 'ER': 2.904023, 'PHdBm': 4.3,
              'PHW': 0.002692, 'PLdBm': -0.33, 'PLW': 0.000927, 'OMAdBm': 2.466721, 'OMAW': 0.001765, 'TPdB': 4.703279,
              'TP': 2.953438, 'PmaxdBm': 5.17, 'PmaxW': 0.003289, 'PavgdBm': 2.574823, 'PavgW': 0.001809, 'IILdB': 2.0,
              'IIL': 1.584893, 'LossdB': 4.595177, 'Loss': 2.88083, 'MLdB': 2.595177, 'ML': 1.817681}

    These parameters are all of the linear and logarithmic solutions for the optical calculations.  The definitions of
    these parameters can be seen in the image obtained from OpticalCalculator.Picture().

    @image{inline} html OpticalCalculations.png "optical parameter definitions"

    @see Picture
    """
    def __init__(self,*kwargs):
        """Constructor for an optical calculator
        @param *kwargs optional tuple containing keyword/value pairs for optical parameters to add at construction
        If the constructor is called with no arguments, kwargs = (), an empty tuple.  Otherwise the keyword and values
        are added to the optical calculator using the AddParam function.
        @see AddParam
        """
        dict.__init__(self,{})
        self.validunit = {}
        for base_name in self.param_dict.keys():
            param=self.param_dict[base_name]
            self.validunit[param['log']['name']]={'unit':param['log']['unit']}
            self.validunit[param['lin']['name']]={'unit':param['lin']['unit']}
        if kwargs != ():
            if len(kwargs)//2*2 != len(kwargs):
                raise IndexError('optical arguments must come in key/value pairs')
            for kv in range(len(kwargs)//2):
                if not self.AddParam(kwargs[kv*2],kwargs[kv*2+1],True):
                    raise ValueError('optical calculator does not accept : '+str(kwargs[kv*2])+' = '+str(kwargs[kv*2+1]))

    def AddParam(self,name,value=None,fixed=False,calculate=True):
        """Adds a parameter to the optical calculator
        @param name string name of a parameter.  It must be one of the recognized parameter names in the
        calculator, otherwise it will throw an exception.
        @param value float value to assign to the named parameter
        @param fixed bool (optional, defaults to False) whether the parameter is fixed.  If it is fixed, it checks for overconstrained
        parameter addition
        @param calculate bool (optional, defaults to True) whether to try to compute all of the other parameters upon addition.
        @return bool True if the parameter could be added, False if the parameter could not be added, either because the keyword was
        not identified or because the parameter calculation has already been made.
        """
        if calculate: self.CalculateAll()
        if name in self.validunit.keys():
            if name in self.keys():
                if self[name]['value'] != None:
                    return False
            self[name]=OpticalParam(name,fixed,value,unit=self.validunit[name]['unit'])
            if calculate: self.CalculateAll()
            return True
        return False

    def HasParam(self,name):
        """Checks whether the parameter is in the dictionary
        @param name string name of a parameter
        @return bool True or False whether the named parameter exists in its results.
        """
        return name in self.keys()

    def NeedsCalculation(self,name):
        """Checks whether the parameter needs to be calculated
        @param name string name of a parameter
        @return bool True or False whether the named parameter exists in its results.
        if the parameter is not in the dictionary, it adds the parameter to the dictionary.
        """
        if not name in self:
            self.AddParam(name,calculate=False)
            return True
        else:
            if self[name]['value'] == None:
                if not self[name]['fixed']:
                    return True
        return False

    def HasValue(self,name):
        """Checks whether the parameter is in the dictionary and has a value assigned
        @param name string name of a parameter
        @return bool True or False whether the named parameter exists in its results and
        whether the parameter has a value assigned.
        if the parameter is not in the dictionary, it adds the parameter to the dictionary.
        """
        if not self.HasParam(name):
            self.AddParam(name,calculate=False)
            return False
        else:
            if self[name]['value'] != None:
                return True
        return False

    def HasValues(self,name_list):
        """Checks whether all of the parameters in the list are in the dictionary and has a value assigned
        @param name_list list of string names of parameters
        @return bool True or False whether all of the named parameters exist in its results and
        whether the parameters have a value assigned.
        if any parameter is not in the dictionary, it adds that parameter to the dictionary.
        """
        return all([self.HasValue(name) for name in name_list])

    def SetValue(self,name,value):
        """Sets the named parameter to a value
        @return self
        """
        self[name]['value'] = value
        return self

    def GetValue(self,name):
        """Gets a parameter value
        @param name string name of a parameter
        @return float parameter value
        """
        return self[name]['value']

    @staticmethod
    def L2dB(L):
        """Converts a linear ratio to decibels
        @param L float linear value
        @return float value of L in decibels
        """
        return 10.*math.log10(L)

    @staticmethod
    def dB2L(dB):
        """Converts a value in decibels to a linear ratio
        @param dB float decibel value
        @return float value of dB as a linear ratio
        """
        return math.pow(10.,dB/10.)

    @staticmethod
    def W2dBm(W):
        """Converts a value in Watts to dBm
        @param W float value in Watts
        @return float value of W in dBm
        """
        return OpticalCalculator.L2dB(W)+30.

    @staticmethod
    def dBm2W(dBm):
        """Converts a value in dBm to Watts
        @param dBm float value in dBm
        @return float value of dBm in Watts
        """
        return OpticalCalculator.dB2L(dBm-30)

    def LindBdBm(self):
        """Converts all values in the dictionary from their db/dBm value to linear ratios or Watts
        and vice-versa
        @return self
        """
        self.CalcP('PinW', 'PindBm')
        self.CalcP('PmaxW', 'PmaxdBm')
        self.CalcP('PavgW', 'PavgdBm')
        self.CalcP('PHW', 'PHdBm')
        self.CalcP('PLW', 'PLdBm')
        self.CalcP('PLW', 'PLdBm')
        self.CalcP('OMAW', 'OMAdBm')
        self.CalcL('IL', 'ILdB')
        self.CalcL('IIL', 'IILdB')
        self.CalcL('TP', 'TPdB')
        self.CalcL('ER', 'ERdB')
        self.CalcL('Loss','LossdB')
        self.CalcL('ML','MLdB')
        return self

    def CalcL(self,Lname,dBname):
        """Converts the values of given linear ratio and dB names between each other
        if possible.
        """
        if self.NeedsCalculation(Lname) and self.HasValue(dBname):
            self.SetValue(Lname,self.dB2L(self.GetValue(dBname)))
        if self.NeedsCalculation(dBname) and self.HasValue(Lname):
            self.SetValue(dBname,self.L2dB(self.GetValue(Lname)))

    def CalcP(self,Wname,dBmname):
        """Converts the values of given Watts and dBm names between each other
        if possible.
        """
        if self.NeedsCalculation(Wname) and self.HasValue(dBmname):
            self.SetValue(Wname,self.dBm2W(self.GetValue(dBmname)))
        if self.NeedsCalculation(dBmname) and self.HasValue(Wname):
            self.SetValue(dBmname,self.W2dBm(self.GetValue(Wname)))

    def CalcEq(self,name,params,eq):
        """Calculates a parameter value based on one or more other parameters and an equation
        @param name string name of parameter to calculate
        @param params list of string names of other parameters
        @param eq a python equation that is a function of the other parameters to apply
        """
        if self.NeedsCalculation(name):
            if self.HasValues(params):
                self.SetValue(name,eval(eq))
                return True
        return False

    def CalcDiff(self,name,params,only=False):
        """Calculates a parameter value based on the difference between two other parameters
        @param name string name of parameter to calculate
        @param params list of two string names of other parameters
        @param only bool (optional, defaults to False) whether to try to compute other permutations
        if the named parameter is a and the params are b,c then the permutations are:
        * a=b-c
        * b=a+c
        * c=b-a
        If only is False, only a=b-c is computed.
        """
        if self.NeedsCalculation(name):
            if self.HasValues(params):
                self.SetValue(name,self.GetValue(params[0])-self.GetValue(params[1]))
                return True
        elif not only and self.CalcSum(params[0],[name,params[1]],True):
            return True
        elif not only and self.CalcDiff(params[1],[params[0],name],True):
            return True
        return False

    def CalcSum(self,name,params,only=False):
        """Calculates a parameter value based on the sum of two other parameters
        @param name string name of parameter to calculate
        @param params list of two string names of other parameters
        @param only bool (optional, defaults to False) whether to try to compute other permutations
        if the named parameter is a and the params are b,c then the permutations are:
        * a=b+c
        * b=a-c
        * c=a-b
        If only is False, only a=b+c is computed.
        """
        if self.NeedsCalculation(name):
            if self.HasValues(params):
                self.SetValue(name,self.GetValue(params[0])+self.GetValue(params[1]))
                return True
        elif not only and self.CalcDiff(params[0],[name,params[1]],True):
            return True
        elif not only and self.CalcDiff(params[1],[name,params[0]],True):
            return True
        return False

    def CalculateAll(self):
        """Calculates all possible values that can be calculated based on the current population of the dictionary
        """
        self.LindBdBm()
        Added = True
        while Added:
            Added=False 
            if self.CalcDiff('PHdBm',['PindBm','ILdB']):
                Added=True
            elif self.CalcDiff('OMAW',['PHW','PLW']):
                Added=True
            elif self.CalcDiff('TPdB',['PindBm','OMAdBm']):
                Added=True
            elif self.CalcDiff('ERdB',['PHdBm','PLdBm']):
                Added=True
            elif self.CalcDiff('PmaxdBm',['PindBm','IILdB']):
                Added=True
            elif self.CalcEq('PavgW',['PHW','PLW'],'(self.GetValue(params[0])+self.GetValue(params[1]))/2.0'):
                Added=True
            elif self.CalcEq('PHW',['PavgW','PLW'],'2.*self.GetValue(params[0])-self.GetValue(params[1])'):
                Added=True
            elif self.CalcEq('PLW',['PavgW','PHW'],'2.*self.GetValue(params[0])-self.GetValue(params[1])'):
                Added=True
            elif self.CalcDiff('LossdB',['PindBm','PavgdBm']):
                Added=True
            elif self.CalcSum('PmaxdBm',['PavgdBm','MLdB']):
                Added=True
            if Added:
                self.LindBdBm()

    def PrintOne(self,name,Pname,Punit,Lname,Lunit):
        """Prints the dB/dBm value and linear/Watts value of a parameter
        @param name string name of the parameter
        @param Pname string name of the dB/dBm value of the parameter
        @param Punit string unit of the dB/dBm parameter
        @param Lname string name of the linear/W value of the parameter
        @param Lunit string unit of the linear/W parameter
        """
        if self.GetValue(Pname) == None:
            print(f"{name}:          None")
        else:
            print(f"{name}:          {ToSI(round(self.GetValue(Pname),4),Punit)}, {ToSI(round(self.GetValue(Lname),4),Lunit)}")

    param_dict = {'Pin':{'log':{'name':'PindBm','unit':'dBm'},
                   'lin':{'name':'PinW','unit':'W'}},
            'IL':{'log':{'name':'ILdB','unit':'dB'},
                   'lin':{'name':'IL','unit':''}},
            'ER':{'log':{'name':'ERdB','unit':'dB'},
                   'lin':{'name':'ER','unit':''}},
            'PH':{'log':{'name':'PHdBm','unit':'dBm'},
                   'lin':{'name':'PHW','unit':'W'}},
            'PL':{'log':{'name':'PLdBm','unit':'dBm'},
                   'lin':{'name':'PLW','unit':'W'}},
            'OMA':{'log':{'name':'OMAdBm','unit':'dBm'},
                   'lin':{'name':'OMAW','unit':'W'}},
            'TP':{'log':{'name':'TPdB','unit':'dB'},
                   'lin':{'name':'TP','unit':''}},
            'Pmax':{'log':{'name':'PmaxdBm','unit':'dBm'},
                   'lin':{'name':'PmaxW','unit':'W'}},
            'Pavg':{'log':{'name':'PavgdBm','unit':'dBm'},
                   'lin':{'name':'PavgW','unit':'W'}},
            'IIL':{'log':{'name':'IILdB','unit':'dB'},
                   'lin':{'name':'IIL','unit':''}},
            'Loss':{'log':{'name':'LossdB','unit':'dB'},
                   'lin':{'name':'Loss','unit':''}},
            'ML':{'log':{'name':'MLdB','unit':'dB'},
                   'lin':{'name':'ML','unit':''}},
            }

    def Print(self):
        """Prints all of the parameter values
        """
        for param_key in self.param_dict.keys():
            param=self.param_dict[param_key]
            self.PrintOne(param_key,
                          param['log']['name'],
                          param['log']['unit'],
                          param['lin']['name'],
                          param['lin']['unit'])

    def Results(self,log=True,lin=True):
        """returns a dictionary of all of the values
        """
        res_dict={}
        for param_key in self.param_dict.keys():
            param=self.param_dict[param_key]
            if log:
                res_dict[param['log']['name']]=self.GetValue(param['log']['name'])
                if res_dict[param['log']['name']] != None:
                    res_dict[param['log']['name']] = round(res_dict[param['log']['name']],6)
            if lin:
                res_dict[param['lin']['name']]=self.GetValue(param['lin']['name'])
                if res_dict[param['lin']['name']] != None:
                    res_dict[param['lin']['name']] = round(res_dict[param['lin']['name']],6)
        return res_dict

    @staticmethod
    def Picture():
        from PIL import Image
        import os
        return Image.open(os.path.join(os.path.dirname(__file__),'../../Images/OpticalCalculations.png'))