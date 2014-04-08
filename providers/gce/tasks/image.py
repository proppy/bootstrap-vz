from base import Task
from common.tasks import loopback
from common import phases
from common.tasks import apt
from common.tools import log_check_call
import os.path

class CreateTarball(Task):
	description = 'Creating tarball with image'
	phase = phases.image_registration
	predecessors = [loopback.MoveImage]

	@classmethod
	def run(cls, info):
		import datetime
		image_name = info.manifest.image['name'].format(**info.manifest_vars)
		filename = '{image_name}.{ext}'.format(
			image_name=image_name,
			ext=info.volume.extension)
		today = datetime.datetime.today()
		name_suffix = today.strftime('%Y%m%d')
		image_name = '{lsb_distribution}-{lsb_release}-{release}-v{name_suffix}'.format(
			lsb_distribution=info.gce['lsb_distribution'],
			lsb_release=info.gce['lsb_release'],
			release=info.manifest.system['release'],
			name_suffix=name_suffix)
		info.gce['image_name'] = image_name
		tarball_name = '{image_name}.tar.gz'.format(image_name=image_name)
		tarball_path = os.path.join(info.manifest.bootstrapper['workspace'], tarball_name)
		info.gce['tarball_name'] = tarball_name
		info.gce['tarball_path'] = tarball_path
		log_check_call(['/bin/tar', '--sparse',
			'-C', info.manifest.bootstrapper['workspace'],
			'-caf', tarball_path, filename])

class RegisterImage(Task):
	description = 'Registering image with GCE'
	phase = phases.image_registration
	predecessors = [CreateTarball]

	@classmethod
	def run(cls, info):
		image_description = info.gce['lsb_description']
		if 'description' in info.manifest.image:
			image_description = info.manifest.image['description']
		if 'gcs_destination' in info.manifest.image:
			log_check_call(['gsutil', 'cp',
				info.gce['tarball_path'],
				info.manifest.image['gcs_destination']+info.gce['tarball_name']])
		if 'gcs_destination' in info.manifest.image and 'gce_project' in info.manifest.image:
			log_check_call(['gcutil', '--project={}'.format(info.manifest.image['gce_project']),
				'addimage', info.gce['image_name'],
				info.manifest.image['gcs_destination']+info.gce['tarball_name'],
				'--destription={}'.format(image_description)])
