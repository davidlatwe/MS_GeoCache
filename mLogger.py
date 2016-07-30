# -*- coding:utf-8 -*-
import logging
import colorlog

THEME = {logging.CRITICAL: ' [FATAL] ',
		 logging.ERROR:    '   [X]   ',
		 logging.WARNING:  '   [!]   ',
		 logging.INFO:     '    i    ',
		 logging.DEBUG:    '   ...   ',
		 'nextLine':	   '         '}

class MLog:
	def __init__(self, loggerName, noColor= None, lvl=logging.DEBUG):
		if not noColor:
			f = ' %(log_color)s%(styledname)-8s%(reset)s| %(log_color)s%(message)s%(reset)s'
			self.formatter = colorlog.ColoredFormatter(f,
				log_colors={
					'DEBUG':    'cyan',
					'INFO':     'green',
					'WARNING':  'yellow',
					'ERROR':    'red',
					'CRITICAL': 'bold_red',
				})
		else:
			f = ' %(styledname)s| %(message)s'
			self.formatter = logging.Formatter(f)
		self._lvl = lvl
		self.stream = logging.StreamHandler()
		self.stream.setLevel(self._lvl)
		self.stream.setFormatter(self.formatter)
		self.logger = logging.getLogger(loggerName)
		for handler in self.logger.handlers:
			self.logger.removeHandler(handler)
		self.logger.setLevel(self._lvl)
		self.logger.addHandler(self.stream)
		self.logger.propagate = 0
		self.theme = THEME

	def critical(self, message, *args, **kwargs):
		for i, line in enumerate(str(message).splitlines()):
			self.logger.critical(line,
								 extra={"styledname": self.theme[logging.CRITICAL if i == 0 else 'nextLine']},
								 *args, **kwargs)
	crit = c = fatal = critical
	def error(self, message, *args, **kwargs):
		for i, line in enumerate(str(message).splitlines()):
			self.logger.error(line,
							  extra={"styledname": self.theme[logging.ERROR if i == 0 else 'nextLine']},
							  *args, **kwargs)
	err = e = error
	def warn(self, message, *args, **kwargs):
		for i, line in enumerate(str(message).splitlines()):
			self.logger.warn(line,
							 extra={"styledname": self.theme[logging.WARNING if i == 0 else 'nextLine']},
							 *args, **kwargs)
	warning = w = warn
	def info(self, message, *args, **kwargs):
		for i, line in enumerate(str(message).splitlines()):
			self.logger.info(line,
							 extra={"styledname": self.theme[logging.INFO if i == 0 else 'nextLine']},
							 *args, **kwargs)
	inf = nfo = i = info
	def debug(self, message, *args, **kwargs):
		for i, line in enumerate(str(message).splitlines()):
			self.logger.debug(line,
							  extra={"styledname": self.theme[logging.DEBUG if i == 0 else 'nextLine']},
							  *args, **kwargs)
	dbg = d = debug

	 # other convenience functions to set the global logging level
	def _parse_level(self, lvl):
		if lvl == logging.CRITICAL or lvl in ("critical", "crit", "c", "fatal"):
			return logging.CRITICAL
		elif lvl == logging.ERROR or lvl in ("error", "err", "e"):
			return logging.ERROR
		elif lvl == logging.WARNING or lvl in ("warning", "warn", "w"):
			return logging.WARNING
		elif lvl == logging.INFO or lvl in ("info", "inf", "nfo", "i"):
			return logging.INFO
		elif lvl == logging.DEBUG or lvl in ("debug", "dbg", "d"):
			return logging.DEBUG
		else:
			raise TypeError("Unrecognized logging level: %s" % lvl)

	def setLevel(self, lvl=None):
		'''Get or set the logging level.'''
		if not lvl:
			return self._lvl
		self._lvl = self._parse_level(lvl)
		self.stream.setLevel(self._lvl)
		self.logger.setLevel(self._lvl)