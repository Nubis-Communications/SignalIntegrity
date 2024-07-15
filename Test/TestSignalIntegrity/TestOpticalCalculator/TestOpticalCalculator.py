"""
TestOptimization.py
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

import unittest
import SignalIntegrity.Lib as si

class TestOpticalCalculatorTest(unittest.TestCase):

    def testOpticalCalculator(self):
        oc=si.opt.OpticalCalculator('PindBm',7.17,'IILdB',2.0,'ILdB',2.87,'ERdB',4.63)
        oc.Print()
    
        import itertools
        requiredList=[si.opt.OpticalCalculator.param_dict[param_key]['log']['name']
                      for param_key in si.opt.OpticalCalculator.param_dict.keys()]
        requiredList+=[si.opt.OpticalCalculator.param_dict[param_key]['lin']['name']
                      for param_key in si.opt.OpticalCalculator.param_dict.keys()]  
        combs = list(itertools.combinations(requiredList, 4))
    
        # remove all combinations specifying PH and PL
        # combs_to_keep = []
        # for comb in combs:
        #     if 'PHdBm' in comb:
        #         continue
        #     if 'PLdBm' in comb:
        #         continue
        #     combs_to_keep.append(comb)
        # combs=combs_to_keep
    
        number_total=0
        number_correct=0
        number_incorrect=0
        valid_combinations=[]
        for combination in combs:
            oc2=si.opt.OpticalCalculator()
            overconstrained=False
            for item in combination:
                overconstrained = overconstrained or not oc2.AddParam(item,oc.GetValue(item),fixed=True)
            if overconstrained:
                correct=False
            else:
                print('\n')
                print(combination)
                oc2.Print()
                if all([oc2.Results()[key] != None for key in oc2.Results().keys()]): # all of the values were found
                    if oc.Results() != oc2.Results():
                        pass
                    self.assertEqual(oc.Results(), oc2.Results(), 'an optical calculation is incorrect')
                correct = oc.Results() == oc2.Results()
            print(correct)
            number_total+=1
            if correct:
                number_correct+=1
                valid_combinations.append(combination)
            else:
                number_incorrect+=1
        print('done')
    
        print(f'total: {number_total} -- correct={number_correct}, incorrect={number_incorrect}')
        self.assertEqual(number_total, 10626, 'total incorrect')
        self.assertEqual(number_correct, 2688, 'number of correct calculations incorrect')
        self.assertEqual(number_incorrect, 7938, 'number of incorrect calculations incorrect')
    def testOpticalCalculatorKeywordPairError(self):
        with self.assertRaises(IndexError):
            oc=si.opt.OpticalCalculator('PindBm',7.17,'IILdB',2.0,'ILdB',2.87,'ERdB')
    def testOpticalCalculatorIncorrectKey(self):
        with self.assertRaises(ValueError):
            oc=si.opt.OpticalCalculator('PindBmxxx',7.17)
    def testOpticalCalculatorPicture(self):
        picture = si.opt.OpticalCalculator.Picture()
        import matplotlib.pyplot as plt
        plt.axis('off')
        plt.imshow(picture)

        showit=False
        if showit:
            plt.show()

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
