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
