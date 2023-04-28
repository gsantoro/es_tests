from enum import Enum

import structlog


class LogLevel(str, Enum):
    critical = "CRITICAL"
    fatal = "FATAL"
    error = "ERROR"
    warning = "WARNING"
    warn = "WARN"
    info = "INFO"
    debug = "DEBUG"
    notset = "NOTSET"
    
    @staticmethod
    def to_int(level: "LogLevel") -> int:
        if level == LogLevel.notset:
            return 0
        if level == LogLevel.debug:
            return 10
        if level == LogLevel.info:
            return 20
        if level == LogLevel.warn or level == LogLevel.warning:
            return 30
        if level == LogLevel.error:
            return 40
        if level == LogLevel.critical or level == LogLevel.fatal:
            return 50
        

class LogRenderer(str, Enum):
    console = "CONSOLE"
    json = "JSON"
    
    @staticmethod
    def to_processor(renderer: "LogRenderer") :
        if renderer == LogRenderer.console:
            return structlog.dev.ConsoleRenderer()
        
        return structlog.processors.JSONRenderer()
        
