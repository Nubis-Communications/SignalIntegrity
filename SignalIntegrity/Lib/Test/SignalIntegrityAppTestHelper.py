"""
SignalIntegrityAppTestHelper.py
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
import os

class SignalIntegrityAppTestHelper:
    relearn=True
    plotErrors=False
    forceWritePictures=False
    SPCompareResolution=1e-3
    allowReferenceImpedanceTranslation=True
    diff_projects=True
    def __init__(self,path):
        self.path=path
    def FileNameForTest(self,filename):
        return filename.replace('..', 'Up').replace('/','_').split('.')[0]
    @staticmethod
    def PrintDiffableDictionary(input_value,indent=0):
        lines=[]
        indent_string=' '*indent
        if isinstance(input_value,dict):
            for key in input_value.keys():
                lines.append(indent_string+str(key))
                lines=lines+SignalIntegrityAppTestHelper.PrintDiffableDictionary(input_value[key],indent+4)
        else:
            lines.append(indent_string+str(input_value))
        return lines
    def ProjectChecker(self,pysi,filename):
        import SignalIntegrity.App.Project
        project_dictionary = SignalIntegrity.App.Project.ToDictionary()
        import json
        testFilename=self.FileNameForTest(filename)+'.json'
        if not os.path.exists(testFilename):
            with open(testFilename,'w') as f:
                json.dump(project_dictionary,f)
        with open(testFilename) as f:
            regression = json.load(f)
        lines = self.PrintDiffableDictionary(project_dictionary)
        regression_lines = self.PrintDiffableDictionary(regression)
        same = lines == regression_lines
        if not same and self.diff_projects:
            import difflib
            for line in difflib.unified_diff(
                regression_lines,lines,
                fromfile='regression', tofile='current', lineterm='\n', n=5):
                print(line)
        self.assertTrue(same,filename+': project file changed')
    def PictureChecker(self,pysi,filename,archive=False):
        if not self.checkPictures:
            return
        currentDirectory=os.getcwd()
        os.chdir(self.path+('/'+os.path.splitext(filename)[0]+'_Archive' if archive else ''))
        testFilename=self.FileNameForTest(filename)+'.TpX'
        try:
            from SignalIntegrity.App.TpX import TpX
            from SignalIntegrity.App.TikZ import TikZ
            tpx=pysi.Drawing.DrawSchematic(TpX()).Finish()
            tikz=pysi.Drawing.DrawSchematic(TikZ()).Finish()
            tpx.lineList=tpx.lineList+tikz.lineList
        except:
            self.assertTrue(False,filename + ' couldnt be drawn')
        os.chdir(self.path)
        if not os.path.exists(testFilename) or self.forceWritePictures:
            tpx.WriteToFile(testFilename)
            if not self.relearn:
                self.assertTrue(False, testFilename + ' not found')
        with open(testFilename) as f:
            regression=f.readlines()
        if tpx.lineList==regression:
            os.chdir(currentDirectory)
            return
        # if we get here, we need a more complicated test because ordering may have changed
        self.assertTrue(len(tpx.lineList)==len(regression),testFilename + ' incorrect')
        itemsToCheck=[True for _ in range(len(regression))]
        for tpxline in tpx.lineList:
            foundOne=False
            for k in range(len(regression)):
                if itemsToCheck[k] and not foundOne:
                    if tpxline==regression[k]:
                        itemsToCheck[k] = False
                        foundOne=True
                if foundOne:
                    continue
            self.assertTrue(foundOne,testFilename + ' incorrect')
        print(testFilename+' okay, but in different order')
        os.chdir(currentDirectory)
    def NetListChecker(self,pysi,filename,archive=False):
        currentDirectory=os.getcwd()
        os.chdir(self.path+('/'+os.path.splitext(filename)[0]+'_Archive' if archive else ''))
        testFilename=self.FileNameForTest(filename)+'.net'
        if isinstance(pysi,list):
            netlist=pysi
        else:
            try:
                netlist=pysi.Drawing.schematic.NetList().Text()
            except:
                self.assertTrue(False,filename + ' couldnt produce netlist')
        netlist=[line+'\n' for line in netlist]
        os.chdir(self.path)
        if not os.path.exists(testFilename):
            with open(testFilename,"w") as f:
                for line in netlist:
                    f.write(line)
                if not self.relearn:
                    self.assertTrue(False, testFilename + ' not found')
        with open(testFilename) as f:
            regression=f.readlines()
        self.assertTrue(len(netlist)==len(regression),testFilename + ' incorrect')
        for netline,regressionline in zip(netlist,regression):
            if netline != regressionline:
                if (netline[:len('connect')]=='connect') and (regression[:len('connect')]=='connect'):
                    netconnecttokens=netline[len('connect'):]
                    regressiontokens=regressionline[len('connect'):]
                    if len(netconnecttokens)//2*2!=len(netconnecttokens):
                        self.fail(testFilename + ' incorrect')
                    if len(regressiontokens)//2*2!=len(regressiontokens):
                        self.fail(testFilename + ' incorrect')
                    if len(netconnecttokens)!=len(regressiontokens):
                        self.fail(testFilename + ' incorrect')
                    nets=[(netconnecttokens[i],netconnecttokens[i+1]) for i in range(len(netconnecttokens)/2)]
                    regs=[(regressiontokens[i],regressiontokens[i+1]) for i in range(len(regressiontokens)/2)]
                    itemsToCheck=[True for _ in range(len(regs))]
                    for net in nets:
                        foundOne=False
                        for k in range(len(regs)):
                            if itemsToCheck[k] and not foundOne:
                                if net==regs[k]:
                                    itemsToCheck[k] = False
                                    foundOne=True
                            if foundOne:
                                continue
                        self.assertTrue(foundOne,testFilename + ' incorrect')
                    print(testFilename+' okay, but connections in different order')
        os.chdir(currentDirectory)
    def SParameterRegressionChecker(self,sp,spfilename):
        from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
        currentDirectory=os.getcwd()
        os.chdir(self.path)
        if not os.path.exists(spfilename):
            sp.WriteToFile(spfilename,'R '+str(sp.m_Z0))
            if not self.relearn:
                self.assertTrue(False, spfilename + ' not found')
        regression=SParameterFile(spfilename)
        if (sp.m_Z0 != regression.m_Z0) and self.allowReferenceImpedanceTranslation:
            sp.SetReferenceImpedance(regression.m_Z0)
        SpAreEqual=self.SParametersAreEqual(sp, regression,self.SPCompareResolution)
        if not SpAreEqual:
            if SignalIntegrityAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title(spfilename)
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(regression.m_P):
                    for c in range(regression.m_P):
                        plt.semilogy(regression.f(),[abs(sp[n][r][c]-regression[n][r][c]) for n in range(len(regression))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(regression.m_P):
                    for c in range(regression.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1)+' Magnitude')
                        plt.plot(sp.FrequencyResponse(r+1,c+1).Frequencies(),sp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(regression.FrequencyResponse(r+1,c+1).Frequencies(),regression.FrequencyResponse(r+1,c+1).Values('dB'),label='regression')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1)+' Phase')
                        plt.plot(sp.FrequencyResponse(r+1,c+1).Frequencies(),sp.FrequencyResponse(r+1,c+1).Values('deg'),label='calculated')
                        plt.plot(regression.FrequencyResponse(r+1,c+1).Frequencies(),regression.FrequencyResponse(r+1,c+1).Values('deg'),label='regression')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,spfilename + ' incorrect')
        os.chdir(currentDirectory)
    def CalibrationRegressionChecker(self,cal,calfilename):
        from SignalIntegrity.Lib.Measurement.Calibration.Calibration import Calibration
        currentDirectory=os.getcwd()
        os.chdir(self.path)
        if not os.path.exists(calfilename):
            cal.WriteToFile(calfilename)
            if not self.relearn:
                self.assertTrue(False, calfilename + ' not found')
        regression=Calibration(0,0).ReadFromFile(calfilename,None)

        regressionFixtures=regression.Fixtures()
        calFixtures=cal.Fixtures()
        SpAreEqual=all([self.SParametersAreEqual(calFixture, regressionFixture, 1e-3)
                            for calFixture,regressionFixture in zip(calFixtures,regressionFixtures)])
        self.assertTrue(SpAreEqual,calfilename + ' incorrect')
        os.chdir(currentDirectory)
    def WaveformRegressionChecker(self,wf,wffilename,max_error=0):
        from SignalIntegrity.Lib.TimeDomain.Waveform import Waveform
        wffilename=wffilename.replace('/','_')
        currentDirectory=os.getcwd()
        os.chdir(self.path)
        if not os.path.exists(wffilename):
            wf.WriteToFile(wffilename)
            if not self.relearn:
                self.assertTrue(False, wffilename + ' not found')
        regression=Waveform().ReadFromFile(wffilename)

        if max_error==0:
            same = regression == wf
        else:
            if regression.TimeDescriptor() != wf.TimeDescriptor():
                same = False
            else:
                max_error_calc = max((regression-wf).Values('abs'))
                same=max_error_calc <= max_error
                if not same:
                    print('max error: '+str(max_error_calc))

        if self.plotErrors and not same:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.title(wffilename)
            plt.plot(wf.Times(),wf.Values(),label='calculated')
            plt.plot(regression.Times(),regression.Values(),label='regression')
            plt.xlabel('time (s)')
            plt.ylabel('amplitude (V)')
            plt.legend(loc='upper right')
            plt.grid(True)
            plt.show()

        self.assertTrue(same,wffilename + ' incorrect')
        os.chdir(currentDirectory)
    def ArchiveStart(self,filename,args={},archive=False):
        if archive:
            os.chdir(self.path)
            from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
            app=SignalIntegrityAppHeadless()
            self.assertTrue(app.OpenProjectFile(os.path.realpath(filename),args),filename + ' couldnt be opened')
            self.assertTrue(app.Archive(),filename + ' couldnt be archived')
            self.assertTrue(app.ExtractArchive(os.path.splitext(filename)[0]+'.siz', args))
    def ArchiveCleanup(self,filename,app,archive=False):
        if archive:
            os.chdir(self.path+('/'+os.path.splitext(filename)[0]+'_Archive' if archive else ''))
            self.assertTrue(app.FreshenArchive())
            self.assertTrue(app.UnExtractArchive())
            os.remove(os.path.splitext(filename)[0]+'.siz')
    def Preliminary(self,filename,checkProject=False,checkPicture=True,checkNetlist=True,args={},archive=False):
        self.ArchiveStart(filename, args, archive)
        os.chdir(self.path+('/'+os.path.splitext(filename)[0]+'_Archive' if archive else ''))
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        pysi=SignalIntegrityAppHeadless()
        self.assertTrue(pysi.OpenProjectFile(os.path.realpath(filename),args),filename + ' couldnt be opened')
        #pysi.SaveProject()
        if checkProject:
            self.ProjectChecker(pysi, filename)
        if checkPicture:
            self.PictureChecker(pysi,filename,archive)
        if checkNetlist:
            self.NetListChecker(pysi,filename,archive)
        return pysi
    def SParameterResultsChecker(self,filename,checkProject=False,checkPicture=True,checkNetlist=True,args={},archive=False):
        pysi=self.Preliminary(filename, checkProject, checkPicture, checkNetlist, args, archive)
        result=pysi.CalculateSParameters()
        self.assertNotEqual(result,{},filename+' produced none')
        os.chdir(self.path)
        spfilename=result['file names']
        spfilename=self.FileNameForTest(filename)+'.'+spfilename.split('.')[-1]
        sp=result['s-parameters']
        self.SParameterRegressionChecker(sp, spfilename)
        self.ArchiveCleanup(filename,pysi,archive)
        return result
    def CalibrationResultsChecker(self,filename,checkProject=False,checkPicture=True,checkNetlist=True, args={}):
        pysi=self.Preliminary(filename, checkProject, checkPicture=checkPicture, checkNetlist=checkNetlist, args=args)
        result=pysi.CalculateErrorTerms()
        self.assertNotEqual(result,{},filename+' produced none')
        os.chdir(self.path)
        calfilename=result['file names']
        calfilename=self.FileNameForTest(filename)+'.'+calfilename.split('.')[-1]
        cal=result['error terms']
        self.CalibrationRegressionChecker(cal,calfilename)
        return result
    def SimulationResultsChecker(self,filename,checkProject=False,checkPicture=True,checkNetlist=True,args={}, archive=False, max_wf_error=0):
        pysi=self.Preliminary(filename, checkProject, checkPicture=checkPicture, checkNetlist=checkNetlist, args=args, archive=archive)
        result=pysi.Simulate()
        self.assertNotEqual(result,{},filename+' produced none')
        os.chdir(self.path)
        sourceNames=result['source names']
        outputNames=result['output waveform labels']
        transferMatrices=result['transfer matrices']
        outputWaveforms=result['output waveforms']
        try:
            sp=transferMatrices.SParameters()
            ports=sp.m_P
            if ports == 0:
                raise
        except:
            self.assertTrue(False, filename + 'has no transfer matrices')
        spfilename=self.FileNameForTest(filename)+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        for i in range(len(outputNames)):
            wf=outputWaveforms[i]
            wffilename=self.FileNameForTest(filename)+'_'+outputNames[i]+'.txt'
            self.WaveformRegressionChecker(wf, wffilename, max_wf_error)
        self.ArchiveCleanup(filename,pysi,archive)
        return result
    def SimulationTransferMatricesResultsChecker(self,filename,checkProject=False,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkProject, checkPicture, checkNetlist)
        result=pysi.TransferParameters()
        self.assertNotEqual(result,{},filename+' produced none')
        os.chdir(self.path)
        self.assertEqual(len(result),5,'wrong number of results') # actually three results, but one element is the 'type'
        sourceNames=result['source names']
        outputNames=result['output waveform labels']
        transferMatrices=result['transfer matrices']
        try:
            sp=transferMatrices.SParameters()
            ports=sp.m_P
            if ports == 0:
                raise
        except:
            self.assertTrue(False, filename + 'has no transfer matrices')
        spfilename=self.FileNameForTest(filename)+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        return result
    def ImageRegressionChecker(self,img,filename):
        from PIL import Image
        currentDirectory=os.getcwd()
        os.chdir(self.path)
        if not os.path.exists(filename):
            img.save(filename)
            if not self.relearn:
                self.assertTrue(False, filename + ' not found')
        regression=Image.open(filename)

        def ImageRMSE(imageA, imageB):
            import numpy as np
            import math

            imageA=np.array(imageA)
            imageB=np.array(imageB)
            # the 'Mean Squared Error' between the two images is the
            # sum of the squared difference between the two images;
            # NOTE: the two images must have the same dimension
            err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
            err /= float(imageA.shape[0] * imageA.shape[1])
            # return the MSE, the lower the error, the more "similar"
            # the two images are
            return math.sqrt(err)

        #print(f'RMSE: {ImageRMSE(regression,img)}')
        errorBetweenImages=ImageRMSE(regression,img)
        self.assertTrue(errorBetweenImages<=0.,filename + ' incorrect')
        os.chdir(currentDirectory)
    def NumpyArrayRegressionChecker(self,ary,filename):
        import numpy as np
        currentDirectory=os.getcwd()
        os.chdir(self.path)
        if not os.path.exists(filename):
            np.save(filename,ary,allow_pickle=False)
            if not self.relearn:
                self.assertTrue(False, filename + ' not found')
        regression=np.load(filename)
        #print(np.sum(np.isclose(ary,regression)))
        self.assertTrue(np.allclose(ary,regression),filename + ' incorrect')
        os.chdir(currentDirectory)
    def JsonDictRegressionChecker(self,meas,filename):
        import json
        import numpy as np
        class CustomJSONizer(json.JSONEncoder):
            def default(self, obj):
                return super().encode(bool(obj)) \
                    if isinstance(obj, np.bool_) \
                    else super().default(obj)
        currentDirectory=os.getcwd()
        os.chdir(self.path)
        if not os.path.exists(filename):
            with open(filename,'w') as f:
                json.dump(meas, f, cls=CustomJSONizer)
            if not self.relearn:
                self.assertTrue(False, filename + ' not found')
        meas=json.loads(json.dumps(meas, cls=CustomJSONizer))
        with open(filename) as f:
            regression = json.load(f)

        from typing import Optional, Union
        JsonType = Optional[Union[dict, list, str, float, int]]

        def are_jsons_approx_equal(js1: JsonType, js2: JsonType, precision: int) -> bool:
            """Compares two json objects and returns True if these are approximately equal.

            Float values are rounded to the significant figures specified as `precision`
            when being compared.

            Args:
                js1: json object to compare
                js2: json object to compare
                precision: significant figures applied to float values

            Returns:
                True if two json objects are approximately equal.

            Raises:
                TypeError: if `js1` or `js2` is not a valid json object.
            """
            def _float_to_str_in_json(js,stringList):
                if type(js) in (str, int, bool, type(None)):
                    jsstring=str(js)
                    #print(jsstring)
                    stringList.append(jsstring+'\n')
                    return jsstring
                if type(js) is float:
                    if js<1e-30:
                        js=0.0
                    if js<1e-10:
                        precisionToUse=max(0,precision-2)
                    elif js<1e-4:
                        precisionToUse=max(0,precision-1)
                    else:
                        precisionToUse=precision
                    jsstring=f"{js:.{precisionToUse}e}"
                    #print(jsstring)
                    stringList.append(jsstring+'\n')
                    return jsstring
                if type(js) is list:
                    return [_float_to_str_in_json(x,stringList) for x in js]
                if type(js) is dict:
                    if any([type(key) is not str for key in js.keys()]):
                        raise TypeError("One of key types is not 'str'.")
                    return {key: _float_to_str_in_json(val,stringList) for key, val in js.items()}
                raise TypeError(f"Value of type '{type(js)}' is not a valid json object.")

            stringList1=[]
            new_js1 = _float_to_str_in_json(js1,stringList1)

            stringList2=[]
            new_js2 = _float_to_str_in_json(js2,stringList2)

            if stringList1 != stringList2:
                with open('regressionJson.txt','wt') as f: f.writelines(stringList1)
                with open('currentJson.txt','wt') as f: f.writelines(stringList2)

            return new_js1 == new_js2

        self.assertTrue(are_jsons_approx_equal(regression,meas,2),filename + ' incorrect')
        os.chdir(currentDirectory)

    def SimulationEyeDiagramResultsChecker(self,filename,checkProject=False,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkProject, checkPicture, checkNetlist)
        result=pysi.Simulate(EyeDiagrams=True)
        self.assertNotEqual(result,{},filename+' produced none')
        os.chdir(self.path)
        sourceNames=result['source names']
        outputNames=result['output waveform labels']
        transferMatrices=result['transfer matrices']
        outputWaveforms=result['output waveforms']
        eyeDiagramNames=result['eye diagram labels']
        eyeDiagrams=result['eye diagrams']
        eyeDiagramImages=[ed.Image() for ed in eyeDiagrams]
        eyeDiagramBitmaps=[ed.BitMap() for ed in eyeDiagrams]
        eyeDiagramMeasurements=[ed.Measurements() for ed in eyeDiagrams]
        try:
            sp=transferMatrices.SParameters()
            ports=sp.m_P
            if ports == 0:
                raise
        except:
            self.assertTrue(False, filename + 'has no transfer matrices')
        spfilename=self.FileNameForTest(filename)+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        for i in range(len(outputNames)):
            wf=outputWaveforms[i]
            wffilename=self.FileNameForTest(filename)+'_'+outputNames[i]+'.txt'
            self.WaveformRegressionChecker(wf, wffilename)
        for i in range(len(eyeDiagramNames)):
            eyeDiagramImage=eyeDiagramImages[i]
            eyeDiagramImageFileName=self.FileNameForTest(filename)+'_'+eyeDiagramNames[i]+'.png'
            self.ImageRegressionChecker(eyeDiagramImage,eyeDiagramImageFileName)
            eyeDiagramBitmap=eyeDiagramBitmaps[i]
            eyeDiagramBitmapFileName=self.FileNameForTest(filename)+'_'+eyeDiagramNames[i]+'.npy'
            self.NumpyArrayRegressionChecker(eyeDiagramBitmap,eyeDiagramBitmapFileName)
            eyeDiagramMeasurement=eyeDiagramMeasurements[i]
            eyeDiagramMeasurementFileName=self.FileNameForTest(filename)+'_'+eyeDiagramNames[i]+'.json'
            self.JsonDictRegressionChecker(eyeDiagramMeasurement,eyeDiagramMeasurementFileName)
        return result
    def VirtualProbeResultsChecker(self,filename,checkProject=False,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkProject, checkPicture, checkNetlist)
        result=pysi.VirtualProbe()
        self.assertNotEqual(result,{},filename+' produced none')
        os.chdir(self.path)
        measNames=result['source names']
        outputNames=result['output waveform labels']
        transferMatrices=result['transfer matrices']
        outputWaveforms=result['output waveforms']
        try:
            sp=transferMatrices.SParameters()
            ports=sp.m_P
            if ports == 0:
                raise
        except:
            self.assertTrue(False, filename + 'has no transfer matrices')
        spfilename=self.FileNameForTest(filename)+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        for i in range(len(outputNames)):
            wf=outputWaveforms[i]
            wffilename=self.FileNameForTest(filename)+'_'+outputNames[i]+'.txt'
            self.WaveformRegressionChecker(wf, wffilename)
    def DeembeddingResultsChecker(self,filename,checkProject=False,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkProject, checkPicture, checkNetlist)
        result=pysi.Deembed()
        self.assertNotEqual(result,{},filename+' produced none')
        os.chdir(self.path)
        spfilenames=result['unknown names']
        spfilenames=[self.FileNameForTest(filename)+'_'+spf for spf in spfilenames]
        sps=result['s-parameters']
        for i in range(len(spfilenames)):
            sp=sps[i]
            spfilename=spfilenames[i]+'.s'+str(sp.m_P)+'p'
            self.SParameterRegressionChecker(sp, spfilename)
        return result
