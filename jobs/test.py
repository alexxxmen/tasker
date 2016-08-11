from roller import fh
from utils import Logger

from jobs import _Job

class TestJob(_Job):
	def _execute(self, **kwargs):
		self.log.debug("Started job execution")
		self.log.info("In Test Job!!!")
		self.log.debug("kwargs: %s" % kwargs)
		self.log.debug("Finished job execution")
