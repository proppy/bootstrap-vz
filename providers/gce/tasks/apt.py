from base import Task
from common import phases
from common.tasks import apt
from common.tools import log_check_call
import os


class SetPackageRepositories(Task):
	description = 'Adding apt sources'
	phase = phases.preparation
	successors = [apt.AddManifestSources]

	@classmethod
	def run(cls, info):
		sections = 'main'
		if 'sections' in info.manifest.system:
			sections = ' '.join(info.manifest.system['sections'])
		info.source_lists.add('main', 'deb     http://http.debian.net/debian {system.release} '+sections)
		info.source_lists.add('main', 'deb-src http://http.debian.net/debian {system.release} '+sections)
		info.source_lists.add('backports', 'deb     http://http.debian.net/debian {system.release}-backports '+sections)
		info.source_lists.add('backports', 'deb-src http://http.debian.net/debian {system.release}-backports '+sections)
		info.source_lists.add('goog', 'deb http://goog-repo.appspot.com/debian pigeon main')


class PreferKernelsFromBackports(Task):
	description = 'Adding preference for backported kernel, if available'
	phase = phases.package_installation
	predecessors = [apt.WriteSources]

	@classmethod
	def run(cls, info):
		if 'backported_kernel' in info.manifest.system:
			if info.manifest.system['backported_kernel']:
				apt_preferences_path = os.path.join(info.root, 'etc/apt/preferences.d/backports-kernel.pref')
				with open(apt_preferences_path, 'w') as config_file:
					print >>config_file, "Package: linux-image-* initramfs-tools"
					print >>config_file, "Pin: release n=wheezy-backports"
					print >>config_file, "Pin-Priority: 500"


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
