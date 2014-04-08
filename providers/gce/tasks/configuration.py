from base import Task
from common import phases
from common.tools import log_check_call

class GatherReleaseInformation(Task):
	description = 'Gathering release information about created image'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		lsb_distribution = log_check_call(['/usr/sbin/chroot', info.root,
			'/usr/bin/lsb_release', '-i', '-s'])
		lsb_description = log_check_call(['/usr/sbin/chroot', info.root,
			'/usr/bin/lsb_release', '-d', '-s'])
		lsb_release = log_check_call(['/usr/sbin/chroot', info.root,
			'/usr/bin/lsb_release', '-r', '-s'])
		info.gce['lsb_distribution'] = lsb_distribution[0]
		info.gce['lsb_description'] = lsb_description[0]
		info.gce['lsb_release'] = lsb_release[0]
