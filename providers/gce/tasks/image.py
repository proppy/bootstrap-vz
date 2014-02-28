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
		import datetime
		image_name = info.manifest.image['name'].format(**info.manifest_vars)
		filename = '{image_name}.{ext}'.format(
			image_name=image_name,
			ext=info.volume.extension)
		distribution = 'debian'
		lsb_release = '7'
#		distribution = log_check_call(['/usr/sbin/chroot', info.root,
#			'/usr/bin/lsb_release', '-d', '-s'])
#		lsb_release = log_check_call(['/usr/sbin/chroot', info.root,
#			'/usr/bin/lsb_release', '-r', '-s'])
		today = datetime.datetime.today()
		name_suffix = today.strftime('%Y%m%d')
		tarball_name = '{distribution}-{lsb_release}-{release}-v{name_suffix}.tar.gz'.format(
			distribution=distribution,
			lsb_release=lsb_release,
			release=info.manifest.system['release'],
			name_suffix=name_suffix)
		tarball_path = os.path.join(info.manifest.bootstrapper['workspace'], tarball_name)
		log_check_call(['/bin/tar', '--sparse',
			'-C', info.manifest.bootstrapper['workspace'],
			'-caf', tarball_path, filename])
