# PySI Tests


Testing of PySI is accomplished through the use of the unittest framework.  There are a variety of unit tests along with regression results in [Test](https://github.com/TeledyneLeCroy/PySI/tree/master/Test).

There are two directories containing tests for testing of different things:

* [TestSignalIntegrity](https://github.com/TeledyneLeCroy/PySI/tree/master/Test/TestSignalIntegrity) - for testing of the SignalIntegrity Library
* [TestPySIApp](https://github.com/TeledyneLeCroy/PySI/tree/master/Test/TestPySIApp) - for testing of the PySIApp application

The [SignalIntegrity](https://github.com/TeledyneLeCroy/PySI/tree/master/SignalIntegrity) package contains the library for scripted applications and is the back-end for all of the underlying calculations performed by the [PySIApp](https://github.com/TeledyneLeCroy/PySI/tree/master/PySIApp) GUI based application.

For the most part, the [PySIApp](https://github.com/TeledyneLeCroy/PySI/tree/master/PySIApp) GUI based application is tested by hand, insofar as the GUI is concerned, but the [TestPySIApp](https://github.com/TeledyneLeCroy/PySI/tree/master/Test/TestPySIApp) tests a _headless_ version of PySIApp that can also be used within a scripted environment.  In other words, the headless version can be utilized to load a project file and obtain whatever results that project file produces.  This is a big aid to scripted applications and [TestPySIApp](https://github.com/TeledyneLeCroy/PySI/tree/master/Test/TestPySIApp) tests this headless application.

The [Test](https://github.com/TeledyneLeCroy/PySI/tree/master/Test) directory contains four scripts (two for Linux and two for Windows).  The Linux scripts are _bash_ scripts and have the extension '.sh'.  The Windows scripts are batch files and have the extension '.bat'.  These two sets of scripts are:

* CoverageTest - the main coverage test that runs all of the unit tests for the [SignalIntegrity](https://github.com/TeledyneLeCroy/PySI/tree/master/SignalIntegrity) package.
* CoverageTestPySIApp - the coverage test that runs all of the unit tests for the headless PySIApp

These tests are invoked like either:

    bash CoverageTest.sh

or:

    CoverageTest.bat

depending on your platform.

When the coverage test runs,  it shows something like: 

`C:\Work\PySI\Test>CoverageTest`
`F...................................................................................................x........x...........................................................................................................................................................................................................................................................................................................E.....................................................................x....................................................................................................................................................................................................................................................................................................................................................................................................`
`======================================================================`
`ERROR: testRLGCFit2 (TestRLGCLevMar.TestRLGCLevMar)`
`----------------------------------------------------------------------`
`Traceback (most recent call last):`
  `File "C:\Work\PySI\TestSignalIntegrity\TestRLGCLevMar.py", line 448, in testRLGCFit2`
    `raise`
`TypeError: exceptions must be old-style classes or derived from BaseException, not NoneType`

`======================================================================`
`FAIL: testFiles (TestHeaders.Test)`
`----------------------------------------------------------------------`
`Traceback (most recent call last):`
  `File "C:\Work\PySI\TestSignalIntegrity\TestHeaders.py", line 198, in testFiles`
    `self.assertFalse(errors,'there were license errors')`
`AssertionError: there were license errors`

`----------------------------------------------------------------------`
`Ran 868 tests in 356.698s`

`FAILED (failures=1, errors=1, expected failures=3)`
`Press any key to continue . . .`

The batch or bash file that does this waits at this point and allows the user to examine the failures.  Here, the test ran 868 tests in 356 seconds, had one failure and one error.  You could then run those unit tests independently to debug things.

**do not press the enter key right away on Linux machines as the coverage report will be loading in the browser.  On Windows machines, you must press enter to get the browser to load**

After the test runs, a browser will open with the actual coverage report.  the coverage report is browsable html and will let you see the code coverage for every module.

After you are done browsing the coverage report, close the browser, and press enter in the command window where you executed the script.  Pressing enter will delete the html coverage report - this report should not be checked in to the system.

In this way, you run the unit tests to see if everything is okay, and examine code coverage.  If you added code, you should try to include tests that get it such that all of your code is covered.

In the coverage report, two directories worth of code are shown:

* [PySIApp](https://github.com/TeledyneLeCroy/PySI/tree/master/PySIApp) - this cannot be tested with 100 percent coverage, but the file [PySIAppHeadless](https://github.com/TeledyneLeCroy/PySI/blob/master/PySIApp/PySIAppHeadless.py) should be tested at 100 percent coverage by [CoverageTestPySIApp.sh](https://github.com/TeledyneLeCroy/PySI/blob/master/Test/CoverageTestPySIApp.sh) or [CoverageTestPySIApp.bat](https://github.com/TeledyneLeCroy/PySI/blob/master/Test/CoverageTestPySIApp.bat).  Any other  coverage here is considered a bonus.
* the [SignalIntegrity](https://github.com/TeledyneLeCroy/PySI/tree/master/SignalIntegrity) package - This should be tested at 100 percent coverage.

The coverage of the test code is not currently shown.
