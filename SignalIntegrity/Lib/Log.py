"""
Log.py

Category based logging for SignalIntegrity.

Logging is organized into a small number of named _categories_.  Each category
is an ordinary Python logger named 'si.<Category>', so anything that knows how
to configure the standard logging module can configure this (including pytest's
caplog and logging.config.dictConfig).

The filter is two dimensional, but deliberately presented simply:

    - each category is individually turned on or off, and
    - a single common _depth_ (ERROR, WARNING, INFO, DEBUG) applies to all
      enabled categories.

Everything is controlled with a single configuration dictionary whose shape is
identical to the Logging section of the preferences file, so the GUI, the
preferences file, the command line, the environment and scripts all drive the
same code path.

@note this module deliberately imports nothing from SignalIntegrity.  It must
remain usable headless (i.e. with no display) and importable from anywhere in
SignalIntegrity.Lib without creating a circular dependency.
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
import logging
import logging.handlers
import platform
import threading

#: name of the root logger of all SignalIntegrity logging.  All categories are
#: children of this logger.
RootLoggerName='si'

#: the logging categories.  The key is the category name (which is what appears
#: in the preferences file, in the dialog and in the log itself) and the value
#: is a description used as the tooltip in the dialog.
#: @remark add a category here and it automatically appears in the preferences
#: file, in the preferences dialog and in the external control string.
Categories={
    'Cache':'results cache checks, hits, misses and writes',
    'Archive':'archiving, extracting and path resolution',
    'SubProject':'opening and solving of hierarchical sub-projects',
    'Calculation':'netlist solving, simulation and s-parameter calculation',
    'Parallel':'parallelized calculations and worker processes',
    'Timing':'execution times of calculations and sub-projects'
    }

#: the allowed depths, shallowest first.  'OFF' is not a depth - it is the state
#: of a category that is turned off.
Levels=['ERROR','WARNING','INFO','DEBUG']

#: the value used as a logger level to mean 'nothing gets through'.
OFF=logging.CRITICAL+1

#: relative precedence of the various sources of configuration.  A source can
#: never be overridden by a source of lower precedence.  This is what stops the
#: preferences file - which is re-read and re-applied by every sub-project - from
#: clobbering a setting made by a script or on the command line.
SourcePrecedence={'default':0,'preferences':1,'environment':2,'cli':3,'api':4}

def LogDirectory():
    """the directory that log files are written to by default.
    @return string absolute path of the directory for log files.
    @remark this mirrors the location of the preferences file, so that on Windows
    the log lands in c:/Nubis/SignalIntegrity and on Linux (and anything else) it
    lands in ~/.signalintegrity.
    """
    if platform.system() == 'Windows':
        directory='c:/Nubis/SignalIntegrity'
    else:
        directory=os.path.join(os.path.expanduser('~'),'.signalintegrity')
    return directory

def DefaultLogFileName():
    """the default log file name.
    @return string absolute path of the default log file.
    """
    return os.path.join(LogDirectory(),'signalintegrity.log').replace('\\','/')

def DefaultConfiguration():
    """the configuration dictionary corresponding to logging being completely off.
    @return dict the default logging configuration.
    """
    return {'Enabled':False,
            'Level':'INFO',
            'Console':True,
            'File':False,
            'FileName':DefaultLogFileName(),
            'MaxFileSizeKB':1024,
            'BackupCount':3,
            'Categories':{category:False for category in Categories}}

def Logger(category):
    """the logger for a category.
    @param category string name of the category (must be a key of Categories).
    @return Logger the logger for this category.
    @remark the returned logger is an ordinary Python logger.  Use lazy
    formatting (i.e. log.debug('%s',thing), not log.debug(f'{thing}')) and guard
    expensive message construction with log.isEnabledFor().
    """
    return logging.getLogger(RootLoggerName+'.'+category)

class _ContextFilter(logging.Filter):
    """Injects the hierarchical sub-project context into every record.
    @remark this is what makes the depth of a sub-project visible in the log.
    """
    def filter(self,record):
        stack=LogConfiguration.ContextStack()
        record.depth=len(stack)
        record.indent='  '*max(len(stack)-1,0)
        record.project=stack[-1] if len(stack)>0 else ''
        record.context=record.indent+(record.project+': ' if record.project != '' else '')
        return True

class LogConfiguration(object):
    """Configures the SignalIntegrity logging categories.

    All state is process wide (i.e. class level), which is exactly what is wanted
    for hierarchical projects: a sub-project solved at any depth inherits the
    logging configuration of the run without anything having to be passed down.
    """
    #: the configuration currently in effect.
    _configuration=DefaultConfiguration()
    #: the precedence of the source that established the current configuration.
    _source='default'
    #: signature of the currently installed handlers, used to make handler
    #: installation idempotent.
    _handlerSignature=None
    #: the handlers this class installed (as opposed to ones a caller added).
    _handlers=[]
    #: extra handlers installed by callers (e.g. a log viewer window).
    _extraHandlers=[]
    #: per thread sub-project context stack.
    _local=threading.local()
    #: format of a log record.
    Format='%(asctime)s %(name)-14s %(levelname)-7s %(context)s%(message)s'
    #: format of the time stamp of a log record.
    DateFormat='%H:%M:%S'

    @staticmethod
    def ContextStack():
        """the sub-project context stack of the calling thread.
        @return list of strings, outermost project first.
        """
        try:
            stack=LogConfiguration._local.stack
        except AttributeError:
            stack=[]
            LogConfiguration._local.stack=stack
        return stack

    @staticmethod
    def PushContext(name):
        """pushes a sub-project onto the logging context.
        @param name string name of the sub-project being entered.
        @return int the depth after pushing, to be passed to PopContext().
        @remark prefer the Context() context manager, which cannot leak.
        """
        stack=LogConfiguration.ContextStack()
        stack.append(str(name))
        return len(stack)

    @staticmethod
    def PopContext(level=None):
        """pops a sub-project off the logging context.
        @param level int (optional) depth returned by the matching PushContext().
        If provided, the stack is unwound to just below this level, which makes
        the context robust to exceptions that skip a pop.
        """
        stack=LogConfiguration.ContextStack()
        if level is None:
            if len(stack)>0:
                stack.pop()
        else:
            del stack[max(level-1,0):]

    @staticmethod
    def Context(name,category='SubProject',timing=True):
        """context manager that logs entry to and exit from a sub-project.
        @param name string name of the sub-project being entered.
        @param category string (optional, defaults to 'SubProject') category that
        the entry and exit are logged to.
        @param timing bool (optional, defaults to True) whether to log the elapsed
        time on exit to the 'Timing' category.
        @return a context manager.
        """
        return _LogContext(name,category,timing)

    @staticmethod
    def Levels():
        """the allowed depths.
        @return list of strings.
        """
        return list(Levels)

    @staticmethod
    def CategoryDescriptions():
        """the categories and what they log.
        @return dict of category name to description.
        """
        return dict(Categories)

    @staticmethod
    def Snapshot():
        """the configuration currently in effect.
        @return dict a copy of the current configuration, in the same form as is
        accepted by Configure().
        @remark snapshot, modify, Configure() is a supported round trip and is how
        Scoped() restores state.
        """
        configuration=dict(LogConfiguration._configuration)
        configuration['Categories']=dict(LogConfiguration._configuration['Categories'])
        return configuration

    @staticmethod
    def Configure(configuration=None,source='api',**kwargs):
        """configures logging.
        @param configuration dict (optional) configuration dictionary.  It may be
        partial - anything not mentioned keeps its current value.  It may also be
        a string in the external control form (see ParseString()).
        @param source string (optional, defaults to 'api') what is asking, one of
        'default', 'preferences', 'environment', 'cli' or 'api'.  A request from a
        source of lower precedence than the one currently in effect is ignored.
        @param kwargs any configuration key may also be supplied as a keyword.
        @return bool whether the configuration was applied.
        """
        if SourcePrecedence.get(source,0) < SourcePrecedence.get(LogConfiguration._source,0):
            return False
        if isinstance(configuration,str):
            configuration=ParseString(configuration)
        merged=LogConfiguration.Snapshot()
        for provided in [configuration,kwargs]:
            if not provided:
                continue
            for key,value in provided.items():
                if key == 'Categories':
                    for category,enabled in value.items():
                        if category == '*':
                            for name in merged['Categories']:
                                merged['Categories'][name]=enabled
                        elif category in Categories:
                            merged['Categories'][category]=enabled
                        else:
                            raise ValueError('unknown logging category: '+str(category))
                elif key in merged:
                    merged[key]=value
                else:
                    raise ValueError('unknown logging configuration key: '+str(key))
        if merged['Level'] not in Levels:
            merged['Level']=DefaultConfiguration()['Level']
        LogConfiguration._configuration=merged
        LogConfiguration._source=source
        LogConfiguration._Apply()
        return True

    @staticmethod
    def Initialize(**kwargs):
        """convenience wrapper around Configure() that turns logging on.
        @param kwargs any configuration key (Level, Console, File, FileName ...).
        @return bool whether the configuration was applied.
        """
        kwargs.setdefault('Enabled',True)
        return LogConfiguration.Configure(**kwargs)

    @staticmethod
    def Scoped(configuration=None,**kwargs):
        """context manager applying a configuration and restoring the previous one.
        @param configuration dict (optional) configuration to apply, see Configure().
        @param kwargs any configuration key may also be supplied as a keyword.
        @return a context manager.
        @remark this is the right way for a script or a test to be verbose around
        one calculation only.
        """
        return _ScopedConfiguration(configuration,kwargs)

    @staticmethod
    def AddHandler(handler):
        """adds a handler to the SignalIntegrity root logger.
        @param handler Handler the handler to add.
        @return the handler added.
        @remark this is how an embedding application (or the log viewer window)
        captures the log without going through the console or a file.
        """
        if handler not in LogConfiguration._extraHandlers:
            LogConfiguration._extraHandlers.append(handler)
            handler.addFilter(_ContextFilter())
            logging.getLogger(RootLoggerName).addHandler(handler)
        return handler

    @staticmethod
    def RemoveHandler(handler):
        """removes a handler previously added with AddHandler().
        @param handler Handler the handler to remove.
        """
        if handler in LogConfiguration._extraHandlers:
            LogConfiguration._extraHandlers.remove(handler)
            try:
                logging.getLogger(RootLoggerName).removeHandler(handler)
            except Exception:
                pass

    @staticmethod
    def _Apply():
        """installs the current configuration.
        @remark handler installation is idempotent.  This matters because every
        sub-project re-reads and re-applies the preferences, and installing the
        handlers again each time would multiply every log line by the depth of the
        project hierarchy.
        """
        configuration=LogConfiguration._configuration
        root=logging.getLogger(RootLoggerName)
        root.propagate=False
        root.setLevel(logging.DEBUG)
        LogConfiguration._InstallHandlers(configuration)
        enabled=configuration['Enabled']
        commonLevel=getattr(logging,configuration['Level'],logging.INFO)
        for category in Categories:
            setting=configuration['Categories'].get(category,False)
            if not enabled or not setting:
                level=OFF
            elif isinstance(setting,str):
                level=OFF if setting == 'OFF' else getattr(logging,setting,commonLevel)
            else:
                level=commonLevel
            logging.getLogger(RootLoggerName+'.'+category).setLevel(level)

    @staticmethod
    def _InstallHandlers(configuration):
        """installs the console and file handlers if the destinations changed.
        @param configuration dict the configuration being applied.
        """
        enabled=bool(configuration['Enabled'])
        fileName=configuration['FileName'] if (enabled and configuration['File']) else None
        if not fileName is None:
            # resolved once, and absolutely, because the current directory changes
            # as sub-projects are opened.
            fileName=os.path.abspath(fileName).replace('\\','/')
        signature=(enabled and bool(configuration['Console']),fileName,
                   configuration['MaxFileSizeKB'],configuration['BackupCount'])
        if signature == LogConfiguration._handlerSignature:
            return
        root=logging.getLogger(RootLoggerName)
        for handler in LogConfiguration._handlers:
            try:
                root.removeHandler(handler)
                handler.close()
            except Exception:
                pass
        LogConfiguration._handlers=[]
        formatter=logging.Formatter(LogConfiguration.Format,LogConfiguration.DateFormat)
        handlers=[]
        if configuration['Console'] and enabled:
            handlers.append(logging.StreamHandler())
        if not fileName is None:
            handlers.append(LogConfiguration._FileHandler(fileName,configuration))
        for handler in handlers:
            if handler is None:
                continue
            handler.setFormatter(formatter)
            handler.addFilter(_ContextFilter())
            root.addHandler(handler)
            LogConfiguration._handlers.append(handler)
        if len(root.handlers) == 0:
            root.addHandler(logging.NullHandler())
        LogConfiguration._handlerSignature=signature

    @staticmethod
    def _FileHandler(fileName,configuration):
        """creates the rotating file handler.
        @param fileName string absolute path of the log file.
        @param configuration dict the configuration being applied.
        @return Handler the file handler, or None if the file could not be opened.
        @remark on Windows a log file held open by another instance cannot be
        rotated, so a handler on a process specific file name is used instead.
        """
        try:
            os.makedirs(os.path.dirname(fileName),exist_ok=True)
        except Exception:
            pass
        for name in [fileName,LogConfiguration._ProcessSpecificFileName(fileName)]:
            try:
                return logging.handlers.RotatingFileHandler(name,
                    maxBytes=int(configuration['MaxFileSizeKB'])*1024,
                    backupCount=int(configuration['BackupCount']),
                    delay=True,encoding='utf-8')
            except Exception:
                continue
        return None

    @staticmethod
    def _ProcessSpecificFileName(fileName):
        """a log file name unique to this process.
        @param fileName string the desired log file name.
        @return string the log file name with the process id inserted.
        """
        base,extension=os.path.splitext(fileName)
        return base+'_'+str(os.getpid())+extension

    @staticmethod
    def WorkerConfiguration():
        """the configuration to hand to a worker process.
        @return dict the configuration for worker processes, or None if workers
        should not log.
        @remark workers only log when the 'Parallel' category is on, because the
        interleaved output of several workers is otherwise unreadable.  Workers
        log to a process specific file so that they do not fight over the log.
        """
        configuration=LogConfiguration.Snapshot()
        if not configuration['Enabled'] or not configuration['Categories'].get('Parallel',False):
            return None
        configuration['Console']=False
        if not configuration['File']:
            configuration['File']=True
            configuration['FileName']=DefaultLogFileName()
        configuration['FileName']=LogConfiguration._ProcessSpecificFileName(
            os.path.abspath(configuration['FileName']).replace('\\','/'))
        return configuration

    @staticmethod
    def ConfigureWorker(configuration):
        """configures logging in a worker process.
        @param configuration dict configuration produced by WorkerConfiguration().
        @remark this is needed because worker processes are spawned (not forked) on
        Windows and therefore inherit nothing from the parent process.
        """
        if configuration is None:
            return
        try:
            LogConfiguration._source='default'
            LogConfiguration.Configure(configuration,source='api')
        except Exception:
            pass

    @staticmethod
    def ConfigureFromEnvironment(source='environment'):
        """configures logging from the environment, if it says anything.
        @param source string (optional, defaults to 'environment') the source to
        attribute the configuration to.
        @return bool whether anything was configured.
        @remark SIGNALINTEGRITY_LOG holds the categories and depth (for example
        'DEBUG:Cache,SubProject' or 'INFO:*') and SIGNALINTEGRITY_LOG_FILE holds
        the log file name.
        """
        specification=os.environ.get('SIGNALINTEGRITY_LOG',None)
        fileName=os.environ.get('SIGNALINTEGRITY_LOG_FILE',None)
        if (specification is None) and (fileName is None):
            return False
        try:
            configuration=ParseString(specification) if specification else {'Enabled':True}
            if fileName:
                configuration['File']=True
                configuration['FileName']=fileName
            return LogConfiguration.Configure(configuration,source=source)
        except Exception:
            return False

def ParseString(specification):
    """parses the external control form of a logging configuration.
    @param specification string of the form '[<depth>][:<category>[,<category>...]]'
    where depth is one of ERROR, WARNING, INFO or DEBUG and the categories are the
    ones to turn on ('*' or an omitted list meaning all of them).  A JSON object is
    also accepted, in which case it is used as the configuration dictionary directly.
    @return dict the configuration dictionary.
    """
    specification=(specification or '').strip()
    if specification == '':
        return {}
    if specification[0] == '{':
        import json
        return json.loads(specification)
    configuration={'Enabled':True}
    if ':' in specification:
        level,categories=specification.split(':',1)
    elif specification.upper() in Levels:
        level,categories=specification,'*'
    else:
        level,categories='',specification
    level=level.strip().upper()
    if level != '':
        if level not in Levels:
            raise ValueError('unknown logging depth: '+level)
        configuration['Level']=level
    categories=categories.strip()
    if categories in ['','*']:
        configuration['Categories']={'*':True}
    else:
        wanted=[category.strip() for category in categories.split(',') if category.strip() != '']
        for category in wanted:
            if category not in Categories:
                raise ValueError('unknown logging category: '+category)
        configuration['Categories']={'*':False}
        configuration['Categories'].update({category:True for category in wanted})
    return configuration

class _LogContext(object):
    """implementation of LogConfiguration.Context()"""
    def __init__(self,name,category,timing):
        self.name=name
        self.category=category
        self.timing=timing
        self.level=None
        self.startTime=None
    def __enter__(self):
        import time
        Logger(self.category).info('+%s',self.name)
        self.level=LogConfiguration.PushContext(self.name)
        self.startTime=time.time()
        return self
    def __exit__(self,exceptionType,exceptionValue,traceback):
        import time
        elapsed=time.time()-(self.startTime if not self.startTime is None else time.time())
        LogConfiguration.PopContext(self.level)
        # the exit is always logged to the same category as the entry, so that the
        # entries and exits in the log always pair up.  The elapsed time is a
        # separate concern and goes to the timing category.
        Logger(self.category).info('-%s',self.name)
        if self.timing:
            Logger('Timing').info('%s took %.3f s',self.name,elapsed)
        return False

class _ScopedConfiguration(object):
    """implementation of LogConfiguration.Scoped()"""
    def __init__(self,configuration,kwargs):
        self.configuration=configuration
        self.kwargs=kwargs
        self.saved=None
        self.savedSource=None
    def __enter__(self):
        self.saved=LogConfiguration.Snapshot()
        self.savedSource=LogConfiguration._source
        LogConfiguration.Configure(self.configuration,**self.kwargs)
        return self
    def __exit__(self,exceptionType,exceptionValue,traceback):
        LogConfiguration._source='default'
        LogConfiguration.Configure(self.saved,source='api')
        LogConfiguration._source=self.savedSource
        return False

# the root logger of all SignalIntegrity logging never propagates to the root
# logger of the application embedding SignalIntegrity, and always has a handler,
# so that importing SignalIntegrity can never produce 'no handlers' warnings or
# hijack the logging configuration of the embedding application.
logging.getLogger(RootLoggerName).propagate=False
logging.getLogger(RootLoggerName).addHandler(logging.NullHandler())
LogConfiguration._Apply()
