"""
TestServer.py
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
import os
import json
import time
import http.client

from SignalIntegrity.Server.Api import Api, ApiError
from SignalIntegrity.Server.HttpServer import SignalIntegrityServer

EXAMPLES=os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
    '..','..','..','SignalIntegrity','App','Examples'))

def WaitForJob(api,job,timeout=120.):
    start=time.time()
    while job['state']=='running':
        if time.time()-start>timeout:
            raise AssertionError('calculation did not finish')
        time.sleep(0.05)
        job=api.Dispatch('job',{'id':job['id']})
    return job

class TestServerApiTest(unittest.TestCase):
    def setUp(self):
        self.cwd=os.getcwd()
        self.api=Api()
    def tearDown(self):
        os.chdir(self.cwd)
    def testMethodValidation(self):
        with self.assertRaises(ApiError) as e:
            self.api.Dispatch('bogus',{})
        self.assertEqual(e.exception.status,404)
        with self.assertRaises(ApiError):
            self.api.Dispatch('open',{})
        with self.assertRaises(ApiError):
            self.api.Dispatch('open',{'filename':5})
        with self.assertRaises(ApiError):
            self.api.Dispatch('render',[])
        with self.assertRaises(ApiError):
            self.api.Dispatch('render',{})
        self.assertIn('version',self.api.Dispatch('version',{}))
    def testOpenEditCalculate(self):
        drawing=self.api.Dispatch('open',{'filename':os.path.join(EXAMPLES,'RLC.si')})
        self.assertTrue(drawing['capabilities']['simulate'])
        resistor=[d for d in drawing['devices'] if d['partname']=='Resistor'][0]['index']
        with self.assertRaises(ApiError):
            self.api.Dispatch('select',{'index':'0'})
        self.assertTrue(self.api.Dispatch('select',{'index':resistor})['devices'][resistor]['selected'])
        properties=self.api.Dispatch('setDeviceProperty',{'index':resistor,'keyword':'r','value':'10'})
        self.assertTrue([p for p in properties if p['keyword']=='r'][0]['value'].startswith('10.0'))
        with self.assertRaises(ApiError):
            self.api.Dispatch('moveDevice',{'index':resistor,'dx':True,'dy':0})
        self.api.Dispatch('moveDevice',{'index':resistor,'dx':0,'dy':0})
        self.assertIn('device R1 1 R 10.0',self.api.Dispatch('netlist',{})['netlist'])
        with self.assertRaises(ApiError):
            self.api.Dispatch('setCalculationProperties',{'values':{'EndFrequency':'abc'}})
        job=WaitForJob(self.api,self.api.Dispatch('calculate',{'kind':'simulate'}))
        self.assertEqual(job['state'],'done',job['error'])
        self.assertEqual([w['name'] for w in job['result']['waveforms']],['Vout'])
    def testBusyRejectsEdits(self):
        self.api.Dispatch('open',{'filename':os.path.join(EXAMPLES,'telegrapherFourPort.si')})
        job=self.api.Dispatch('calculate',{'kind':'sparameters'})
        if self.api.activeJob is not None:
            with self.assertRaises(ApiError) as e:
                self.api.Dispatch('render',{})
            self.assertEqual(e.exception.status,409)
        job=WaitForJob(self.api,job)
        self.assertEqual(job['state'],'done',job['error'])
        self.assertEqual(job['result']['sparameters'][0]['ports'],4)
        self.api.Dispatch('render',{})
    def testCalculateErrors(self):
        with self.assertRaises(ApiError):
            self.api.Dispatch('calculate',{'kind':'simulate'})
        self.api.Dispatch('open',{'filename':os.path.join(EXAMPLES,'RLC.si')})
        with self.assertRaises(ApiError):
            self.api.Dispatch('calculate',{'kind':'bogus'})
        job=WaitForJob(self.api,self.api.Dispatch('calculate',{'kind':'sparameters'}))
        self.assertEqual(job['state'],'failed')
        with self.assertRaises(ApiError):
            self.api.Dispatch('job',{'id':12345})
    def testListDirectory(self):
        listing=self.api.Dispatch('listDirectory',{'path':EXAMPLES})
        names=[e['name'] for e in listing['entries']]
        self.assertIn('RLC.si',names)
        self.assertTrue(all(e['directory'] or e['name'].endswith('.si') for e in listing['entries']))
        with self.assertRaises(ApiError):
            self.api.Dispatch('listDirectory',{'path':os.path.join(EXAMPLES,'RLC.si')})
    def testPlotDataAndEyes(self):
        self.api.Dispatch('open',{'filename':os.path.join(EXAMPLES,'HDMICable','PRBSTest.si')})
        job=self.api.Dispatch('calculate',{'kind':'simulate'})
        # polling must not wait for the calculation lock
        self.assertIn(self.api.Dispatch('job',{'id':job['id']})['state'],('running','done'))
        job=WaitForJob(self.api,job)
        self.assertEqual(job['state'],'done',job['error'])
        result=job['result']
        self.assertEqual([e['name'] for e in result['eyes']],['Vdiff','Veq'])
        self.assertTrue(result['eyes'][0]['image'].startswith('data:image/png;base64,'))
        rid=result['resultId']
        full=self.api.Dispatch('plotData',{'resultId':rid,'view':'time','points':500})
        self.assertEqual(len(full['series']),len(result['waveforms']))
        self.assertTrue(all(len(s['x'])<=500 for s in full['series']))
        x0,x1=full['autoscale'][0],full['autoscale'][1]
        zoom=self.api.Dispatch('plotData',{'resultId':rid,'view':'time','indices':[0],'xmin':x0,'xmax':x0+(x1-x0)/1000,'points':20000})
        self.assertEqual(len(zoom['series'][0]['x']),zoom['series'][0]['total'])
        content=self.api.Dispatch('plotData',{'resultId':rid,'view':'content','indices':[0],'points':300})
        self.assertLessEqual(len(content['series'][0]['x']),300)
        for bad in ({'resultId':999,'view':'time'},{'resultId':rid,'view':'bogus'},{'resultId':rid,'view':'time','indices':[99]}):
            with self.assertRaises(ApiError):
                self.api.Dispatch('plotData',bad)
    def testTraversalAndVisibility(self):
        drawing=self.api.Dispatch('open',{'filename':os.path.join(EXAMPLES,'PID','PIDSimulation.si')})
        pid=[d for d in drawing['devices'] if d['ref']=='PID'][0]['index']
        self.assertEqual(self.api.Dispatch('viewActions',{'index':pid}),[{'label':'Open Project','action':'file'}])
        properties=self.api.Dispatch('setPropertyVisibility',{'index':pid,'keyword':'ref','keywordVisible':True})
        self.assertTrue([p for p in properties if p['keyword']=='ref'][0]['keywordVisible'])
        self.assertFalse(self.api.Dispatch('setVariableVisible',{'name':'PID_P','visible':False})[0]['visible'])
        child=self.api.Dispatch('view',{'index':pid,'action':'file'})
        self.assertEqual(child['kind'],'project')
        self.assertEqual(child['drawing']['path'],['PIDSimulation.si','PID.si'])
        with self.assertRaises(ApiError):
            self.api.Dispatch('setVariable',{'name':'P','value':'1'})
        parent=self.api.Dispatch('ascend',{})
        self.assertIn('ref PID',[i['text'] for i in parent['items'] if i['type']=='text'])
        source=[d for d in parent['devices'] if d['ref']=='Vin'][0]['index']
        waveform=self.api.Dispatch('view',{'index':source,'action':'waveform'})
        self.assertEqual(waveform['kind'],'result')
        self.assertEqual(waveform['result']['waveforms'][0]['name'],'Vin')
        self.assertIn('resultId',waveform['result'])
    def testStencilNewAddDelete(self):
        import tempfile, shutil
        directory=tempfile.mkdtemp()
        try:
            catalog=self.api.Dispatch('partCatalog',{})
            self.assertGreater(len(catalog),100)
            self.assertTrue(all(p['preview']['items'] for p in catalog))
            self.assertIs(self.api.Dispatch('partCatalog',{}),catalog)   # cached
            resistor=[p['index'] for p in catalog if p['description']=='Two Port Resistor'][0]
            with self.assertRaises(ApiError):
                self.api.Dispatch('addPart',{'part':resistor,'x':0,'y':0})   # nothing open
            drawing=self.api.Dispatch('new',{'filename':os.path.join(directory,'fresh')})
            self.assertEqual(drawing['devices'],[])
            self.assertTrue(os.path.isfile(os.path.join(directory,'fresh.si')))
            drawing=self.api.Dispatch('addPart',{'part':resistor,'x':100,'y':50.5})
            self.assertEqual(drawing['added'],0)
            self.assertEqual(drawing['devices'][0]['ref'],'R1')
            self.assertTrue(drawing['devices'][0]['selected'])
            drawing=self.api.Dispatch('addPart',{'part':resistor,'x':300,'y':50})
            self.assertEqual([d['ref'] for d in drawing['devices']],['R1','R2'])
            for bad in ({'part':'1','x':0,'y':0},{'part':9999,'x':0,'y':0},{'part':resistor,'x':'a','y':0}):
                with self.assertRaises(ApiError):
                    self.api.Dispatch('addPart',bad)
            drawing=self.api.Dispatch('deleteDevice',{'index':0})
            self.assertEqual([d['ref'] for d in drawing['devices']],['R2'])
            with self.assertRaises(ApiError):
                self.api.Dispatch('deleteDevice',{'index':5})
        finally:
            os.chdir(self.cwd)
            shutil.rmtree(directory,ignore_errors=True)
    def testThemes(self):
        import tempfile, shutil
        from unittest import mock
        from SignalIntegrity.GuiCore import Themes
        directory=tempfile.mkdtemp()
        try:
            with mock.patch.object(Themes,'SettingsFile',return_value=os.path.join(directory,'gui-theme.json')):
                themes=self.api.Dispatch('themes',{})
                self.assertEqual([t['id'] for t in themes[:2]],['builtin:light','builtin:dark'])
                self.assertEqual(self.api.Dispatch('theme',{})['id'],'builtin:light')
                dark=self.api.Dispatch('setTheme',{'id':'builtin:dark'})
                self.assertTrue(dark['palette']['dark'])
                self.assertEqual(set(dark['colorMap']),{'black','blue','salmon','white'})
                self.assertEqual(self.api.Dispatch('theme',{})['id'],'builtin:dark')
                path=os.path.join(directory,'mine.json')
                with open(path,'w') as f:
                    f.write('{"type":"light","colors":{"editor.background":"#fafaf0",},}')
                mine=self.api.Dispatch('setTheme',{'id':path,'name':'Mine'})
                self.assertEqual((mine['name'],mine['palette']['schematicBackground']),('Mine','#fafaf0'))
                with self.assertRaises(ApiError):
                    self.api.Dispatch('setTheme',{'id':os.path.join(directory,'missing.json')})
                self.assertEqual(self.api.Dispatch('theme',{})['id'],path)
                with self.assertRaises(ApiError):
                    self.api.Dispatch('themesInPackage',{'path':os.path.join(directory,'missing.vsix')})
                listing=self.api.Dispatch('listDirectory',{'path':directory,'extensions':['.json','.vsix']})
                self.assertIn('mine.json',[e['name'] for e in listing['entries']])
                self.assertNotIn('mine.json',[e['name'] for e in self.api.Dispatch('listDirectory',{'path':directory})['entries']])
                with self.assertRaises(ApiError):
                    self.api.Dispatch('listDirectory',{'path':directory,'extensions':['.py']})
        finally:
            shutil.rmtree(directory,ignore_errors=True)

class TestServerHttpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cwd=os.getcwd()
        cls.server=SignalIntegrityServer(0,'test-token')
        cls.server.StartInThread()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        os.chdir(cls.cwd)
    def Request(self,method,path,body=None,headers=None):
        connection=http.client.HTTPConnection('127.0.0.1',self.server.port,timeout=60)
        allHeaders={'Content-Type':'application/json','Authorization':'Bearer test-token'}
        allHeaders.update(headers or {})
        allHeaders={k:v for k,v in allHeaders.items() if v is not None}
        connection.request(method,path,None if body is None else json.dumps(body),allHeaders)
        response=connection.getresponse()
        data=response.read()
        connection.close()
        return response.status,data,response
    def Call(self,method,params=None):
        status,data,_=self.Request('POST','/api/'+method,params or {})
        return status,json.loads(data)
    def testStaticFiles(self):
        status,data,response=self.Request('GET','/')
        self.assertEqual(status,200)
        self.assertIn(b'SignalIntegrity',data)
        self.assertIn("default-src 'self'",response.getheader('Content-Security-Policy'))
        self.assertEqual(self.Request('GET','/app.js')[0],200)
        status,data,response=self.Request('GET','/favicon.png')
        self.assertEqual((status,response.getheader('Content-Type'),data[:4]),(200,'image/png',b'\x89PNG'))
        self.assertEqual(self.Request('GET','/../HttpServer.py')[0],404)
        self.assertEqual(self.Request('GET','/%2e%2e/HttpServer.py')[0],404)
    def testAuthorization(self):
        self.assertEqual(self.Request('POST','/api/version',{},{'Authorization':None})[0],401)
        self.assertEqual(self.Request('POST','/api/version',{},{'Authorization':'Bearer wrong'})[0],401)
        self.assertEqual(self.Request('POST','/api/version',{},{'Host':'evil.example:%d'%self.server.port})[0],403)
        self.assertEqual(self.Request('POST','/api/version',{},{'Origin':'http://evil.example'})[0],403)
        self.assertEqual(self.Request('POST','/api/version',{},{'Origin':'http://127.0.0.1:%d'%self.server.port})[0],200)
        self.assertEqual(self.Request('POST','/api/version',{},{'Content-Type':'text/plain'})[0],415)
        self.assertEqual(self.Request('GET','/',None,{'Host':'evil.example'})[0],403)
    def testErrors(self):
        status,body=self.Call('bogus')
        self.assertEqual(status,404)
        connection=http.client.HTTPConnection('127.0.0.1',self.server.port,timeout=60)
        connection.request('POST','/api/version',b'{not json',
            {'Content-Type':'application/json','Authorization':'Bearer test-token'})
        self.assertEqual(connection.getresponse().status,400)
        connection.close()
    def testEndToEnd(self):
        status,body=self.Call('open',{'filename':os.path.join(EXAMPLES,'RLCTest2SP.si')})
        self.assertEqual(status,200,body)
        self.assertTrue(body['result']['capabilities']['sparameters'])
        status,body=self.Call('calculate',{'kind':'sparameters'})
        self.assertEqual(status,200,body)
        job=body['result']
        while job['state']=='running':
            time.sleep(0.05)
            job=self.Call('job',{'id':job['id']})[1]['result']
        self.assertEqual(job['state'],'done',job['error'])
        sp=job['result']['sparameters'][0]
        self.assertEqual(len(sp['traces']),sp['ports']**2)

if __name__ == '__main__':
    unittest.main()
