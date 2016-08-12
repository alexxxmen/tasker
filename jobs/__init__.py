# -*- coding:utf-8 -*-
from roller import fh
from utils import Logger

log = Logger("General", fh)

class _Job(object):
	def __init__(self):
		self.log = Logger(self.__class__.__name__, fh)
		self.log.debug("Job is created")

	def execute(self, **kwargs):
		try:
			self._execute(**kwargs)
		except:
			self.log.exception("Error during job execution")
			# TODO add sending error email

	def _execute(self, **kwargs):
		raise NotImplementedError("%s._execute" % self.__class__.__name__)

	@classmethod
	def run(cls, **kwargs):
		log.debug("in _Job.run!")
		return cls().execute(**kwargs)
