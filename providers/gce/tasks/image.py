from base import Task
from common.tasks import loopback
from common import phases
from common.tasks import apt
from common.tools import log_check_call
import os.path

class CreateTarball(Task):
	description = 'Create tarball with image'
	phase = phases.image_registration
	predecessors = [loopback.MoveImage]

	@classmethod
	def run(cls, info):
		image_name = info.manifest.image['name'].format(**info.manifest_vars)
		filename = '{image_name}.{ext}'.format(image_name=image_name, ext=info.volume.extension)
		log_check_call(['/bin/tar', '--sparse', '-C', info.manifest.bootstrapper['workspace'], '-caf', 'image.tar.gz', filename])
