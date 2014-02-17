from base import Task
from common import phases
from common.tasks import apt
from common.tools import log_check_call
import os


class ImportGoogleKey(Task):
	description = 'Adding Google key'
	phase = phases.package_installation
	predecessors = [apt.InstallTrustedKeys]
	successors = [apt.WriteSources]

	@classmethod
	def run(cls, info):
		key_file = os.path.join(info.root, 'google.gpg.key')
		log_check_call(['/usr/bin/wget', 'https://goog-repo.appspot.com/debian/key/public.gpg.key', '-O', key_file])
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/apt-key', 'add', 'google.gpg.key'])
		os.remove(key_file)
