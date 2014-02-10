#-*- coding: utf-8 -*-

import logging
from logging.handlers import SysLogHandler
from twisted.python import log

class SimpleLogger:
    _loggers = {}

    def __init__(self, logName="SimpleLogger", logFormat="%(name)s: [%(levelname)s] %(message)s"):
        """
        @param loggerName: identifier for root logger logger.
        @type loggerName: C{str}
        """
        # set name for root logger
        self.root_logger_name = logName

        # configure root logger
        self.setLevelLogger(logFormat=logFormat)


    def setLevelLogger(self, logLevel="NOTSET", logName = None, logFormat = logging.BASIC_FORMAT, syslogFacility = None):
        # CRITICAL = 50
        # DEBUG = 10
        # ERROR = 40
        # FATAL = 50
        # INFO = 20
        # NOTSET = 0
        # WARN = 30
        # WARNING = 30

        # get mapped value for logging level
        log_level = getattr(logging, logLevel, logging.NOTSET)   # default = NOTSET

        # identify logger
        log_name = self._loggers.get(log_level, logName)

        # get reference to existing logger (maybe root) or create one
        logger = logging.getLogger(log_name)

        # logName == None means root logger. set root logger name
        if logName is None:
            log_name = self.root_logger_name
            logger.name = log_name

        # define syslog facility
        log_facility = SysLogHandler.facility_names.get(syslogFacility, 1)  # default = user

        # build & configure handler
        log_handler = SysLogHandler(address='/dev/log', facility=log_facility)
        log_handler.setLevel(log_level)
        log_handler.setFormatter(logging.Formatter(logFormat))

        logger.setLevel(log_level)
        logger.addHandler(log_handler)
        logger.propagate = False

        self._loggers[log_level] = log_name


    def log(self, msg, logLevel = logging.DEBUG):
        if isinstance(logLevel, basestring):
            logLevel = getattr(logging, logLevel, logging.DEBUG)

        # use level logger if exists. otherwise we shoud use root logger
        log_name = self._loggers.get(logLevel, None)

        # get specific logger
        logger = logging.getLogger(log_name)

        # log it
        logger.log(logLevel, msg)


class SimpleTwistedLogger(SimpleLogger):
    def emit(self, eventDict):
        text = ""
        log_lvl = eventDict.get("logLevel", logging.DEBUG)

        if eventDict["isError"]:
            log_lvl = logging.ERROR
            if 'failure' in eventDict:
                text = ((eventDict.get('why') or 'Unhandled Error')
                    + '\n' + eventDict['failure'].getTraceback())
            else:
                text = " ".join([str(m) for m in eventDict["message"]]) + "\n"
        else:
            text += " ".join(map(str, eventDict["message"])) + "\n"
        
        self.log(text, log_lvl)


    def start(self):
        log.addObserver(self.emit)


    def stop(self):
        log.removeObserver(self.emit)

