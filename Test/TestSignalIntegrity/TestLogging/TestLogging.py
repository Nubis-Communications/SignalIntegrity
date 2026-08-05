"""
TestLogging.py
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
import logging
import tempfile
import shutil

from SignalIntegrity.Lib.Log import (LogConfiguration,Logger,Categories,Levels,
                                     ParseString,DefaultConfiguration,RootLoggerName)

class TestLoggingTest(unittest.TestCase):
    def setUp(self):
        self.saved=LogConfiguration.Snapshot()
        self.savedSource=LogConfiguration._source
        LogConfiguration._source='default'
        LogConfiguration.Configure(DefaultConfiguration(),source='api')
        LogConfiguration._source='default'

    def tearDown(self):
        LogConfiguration._source='default'
        LogConfiguration.Configure(self.saved,source='api')
        LogConfiguration._source=self.savedSource

    def LevelOf(self,category):
        return logging.getLogger(RootLoggerName+'.'+category).level

    def testEverythingOffByDefault(self):
        for category in Categories:
            self.assertFalse(Logger(category).isEnabledFor(logging.ERROR),
                             category+' should be off by default')

    def testCategoryFiltering(self):
        LogConfiguration.Configure({'Enabled':True,'Level':'DEBUG',
                                    'Categories':{'Cache':True}})
        self.assertTrue(Logger('Cache').isEnabledFor(logging.DEBUG))
        for category in Categories:
            if category != 'Cache':
                self.assertFalse(Logger(category).isEnabledFor(logging.ERROR),
                                 category+' should still be off')

    def testCommonDepthAppliesToEveryEnabledCategory(self):
        LogConfiguration.Configure({'Enabled':True,'Level':'WARNING',
                                    'Categories':{'*':True}})
        for category in Categories:
            self.assertTrue(Logger(category).isEnabledFor(logging.WARNING))
            self.assertFalse(Logger(category).isEnabledFor(logging.INFO))

    def testEnabledIsAMasterSwitch(self):
        LogConfiguration.Configure({'Enabled':True,'Level':'DEBUG','Categories':{'*':True}})
        LogConfiguration.Configure({'Enabled':False})
        for category in Categories:
            self.assertFalse(Logger(category).isEnabledFor(logging.ERROR))
        # the per category settings survive the master switch
        self.assertTrue(LogConfiguration.Snapshot()['Categories']['Cache'])

    def testPartialConfigurationMerges(self):
        LogConfiguration.Configure({'Enabled':True,'Level':'INFO','Categories':{'Cache':True}})
        LogConfiguration.Configure({'Categories':{'Archive':True}})
        configuration=LogConfiguration.Snapshot()
        self.assertTrue(configuration['Categories']['Cache'])
        self.assertTrue(configuration['Categories']['Archive'])
        self.assertEqual(configuration['Level'],'INFO')

    def testSnapshotRoundTrip(self):
        LogConfiguration.Configure({'Enabled':True,'Level':'DEBUG','Categories':{'Cache':True}})
        configuration=LogConfiguration.Snapshot()
        LogConfiguration.Configure(DefaultConfiguration())
        LogConfiguration.Configure(configuration)
        self.assertEqual(LogConfiguration.Snapshot(),configuration)

    def testUnknownCategoryRaises(self):
        with self.assertRaises(ValueError):
            LogConfiguration.Configure({'Categories':{'NoSuchCategory':True}})
        with self.assertRaises(ValueError):
            LogConfiguration.Configure({'NoSuchKey':True})

    def testScopedRestores(self):
        before=LogConfiguration.Snapshot()
        with LogConfiguration.Scoped({'Enabled':True,'Level':'DEBUG','Categories':{'*':True}}):
            self.assertTrue(Logger('Cache').isEnabledFor(logging.DEBUG))
        self.assertEqual(LogConfiguration.Snapshot(),before)
        self.assertFalse(Logger('Cache').isEnabledFor(logging.ERROR))

    def testSourcePrecedence(self):
        LogConfiguration.Configure({'Enabled':True,'Categories':{'Cache':True}},source='cli')
        # the preferences must not be able to undo what the command line asked for
        applied=LogConfiguration.Configure({'Enabled':False,'Categories':{'Cache':False}},
                                          source='preferences')
        self.assertFalse(applied)
        self.assertTrue(LogConfiguration.Snapshot()['Categories']['Cache'])
        # but a script (the highest precedence) can
        applied=LogConfiguration.Configure({'Categories':{'Cache':False}},source='api')
        self.assertTrue(applied)
        self.assertFalse(LogConfiguration.Snapshot()['Categories']['Cache'])

    def testHandlersAreNotDuplicated(self):
        root=logging.getLogger(RootLoggerName)
        LogConfiguration.Configure({'Enabled':True,'Console':True,'Categories':{'*':True}})
        count=len(root.handlers)
        for _ in range(10):
            LogConfiguration.Configure({'Enabled':True,'Console':True,'Categories':{'*':True}},
                                       source='api')
        self.assertEqual(len(root.handlers),count,
                         'handlers must not accumulate when the configuration is re-applied')

    def testParseString(self):
        self.assertEqual(ParseString('DEBUG:Cache'),
                         {'Enabled':True,'Level':'DEBUG','Categories':{'*':False,'Cache':True}})
        self.assertEqual(ParseString('INFO'),
                         {'Enabled':True,'Level':'INFO','Categories':{'*':True}})
        self.assertEqual(ParseString('Cache,Archive'),
                         {'Enabled':True,'Categories':{'*':False,'Cache':True,'Archive':True}})
        self.assertEqual(ParseString('{"Enabled": true}'),{'Enabled':True})
        self.assertEqual(ParseString(''),{})
        with self.assertRaises(ValueError):
            ParseString('VERBOSE:Cache')
        with self.assertRaises(ValueError):
            ParseString('DEBUG:NoSuchCategory')

    def testContextStack(self):
        self.assertEqual(LogConfiguration.ContextStack(),[])
        with LogConfiguration.Context('Top'):
            self.assertEqual(LogConfiguration.ContextStack(),['Top'])
            with LogConfiguration.Context('Child'):
                self.assertEqual(LogConfiguration.ContextStack(),['Top','Child'])
            self.assertEqual(LogConfiguration.ContextStack(),['Top'])
        self.assertEqual(LogConfiguration.ContextStack(),[])

    def testContextUnwoundOnException(self):
        try:
            with LogConfiguration.Context('Top'):
                raise ValueError('failed')
        except ValueError:
            pass
        self.assertEqual(LogConfiguration.ContextStack(),[])

    def testLoggingToFile(self):
        directory=tempfile.mkdtemp()
        try:
            fileName=os.path.join(directory,'si.log')
            LogConfiguration.Configure({'Enabled':True,'Level':'DEBUG','Console':False,
                                        'File':True,'FileName':fileName,
                                        'Categories':{'Cache':True}})
            Logger('Cache').debug('written to the file')
            Logger('Archive').debug('must not be written to the file')
            # the log file must not follow the current directory around, since the
            # current directory changes as sub-projects are opened.
            here=os.getcwd()
            try:
                os.chdir(directory)
                Logger('Cache').debug('written after a directory change')
            finally:
                os.chdir(here)
            LogConfiguration.Configure({'File':False})
            with open(fileName,'r') as f:
                text=f.read()
            self.assertTrue('written to the file' in text)
            self.assertTrue('written after a directory change' in text)
            self.assertFalse('must not be written' in text)
        finally:
            shutil.rmtree(directory,ignore_errors=True)

    def testWorkerConfiguration(self):
        LogConfiguration.Configure({'Enabled':True,'Level':'DEBUG','Categories':{'Cache':True}})
        self.assertIsNone(LogConfiguration.WorkerConfiguration(),
                          'workers must not log unless the Parallel category is on')
        LogConfiguration.Configure({'Categories':{'Parallel':True}})
        configuration=LogConfiguration.WorkerConfiguration()
        self.assertFalse(configuration['Console'])
        self.assertTrue(configuration['File'])
        self.assertTrue(str(os.getpid()) in configuration['FileName'])

    def testEveryCategoryHasADescription(self):
        for category in Categories:
            self.assertTrue(isinstance(Categories[category],str) and Categories[category] != '')
        self.assertEqual(Levels,['ERROR','WARNING','INFO','DEBUG'])

class TestLoggingPreferencesTest(unittest.TestCase):
    def testPreferencesRoundTripAndMigration(self):
        import sys
        appDirectory=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  '..','..','..','SignalIntegrity','App')
        sys.path=[os.path.abspath(appDirectory)]+sys.path
        from SignalIntegrity.App.Preferences import Preferences
        saved=LogConfiguration.Snapshot()
        savedSource=LogConfiguration._source
        directory=tempfile.mkdtemp()
        try:
            fileName=os.path.join(directory,'preferences.xml')
            preferences=Preferences(fileName)
            preferences['Logging.Enabled']=True
            preferences['Logging.Categories.Cache']=True
            preferences.SaveToFile()
            preferences=Preferences(fileName)
            self.assertTrue(preferences['Logging.Enabled'])
            self.assertTrue(preferences['Logging.Categories.Cache'])
            self.assertEqual(preferences['Logging'].Dictionary()['Categories']['Cache'],True)
            # the old style single cache logging bool must migrate to the category
            preferences['Logging.Enabled']=False
            preferences['Logging.Categories.Cache']=False
            preferences['Cache.Logging']=True
            preferences.SaveToFile()
            preferences=Preferences(fileName)
            self.assertTrue(preferences['Logging.Enabled'])
            self.assertTrue(preferences['Logging.Categories.Cache'])
            self.assertEqual(preferences['Logging.Level'],'DEBUG')
            self.assertFalse(preferences['Cache.Logging'])
        finally:
            shutil.rmtree(directory,ignore_errors=True)
            LogConfiguration._source='default'
            LogConfiguration.Configure(saved,source='api')
            LogConfiguration._source=savedSource

if __name__ == "__main__":
    unittest.main()
