from base import Task
from common import phases
from common.tasks import apt


class InstallRemotePackages(Task):
	description = 'Installing remote packages'
	phase = phases.package_installation
	predecessors = [apt.AptUpgrade]

	def run(self, info):
		if len(info.packages.remote) == 0:
			return
		import os

		packages = []
		for name, target in info.packages.remote.iteritems():
			packages.append('{name}/{target}'.format(name=name, target=target))

		import logging
		msg = ('The following packages will be installed (package/target-release):'
		       '\n{packages}\n').format(packages='\n'.join(packages))
		logging.getLogger(__name__).debug(msg)

		from common.tools import log_check_call
		from subprocess import CalledProcessError
		try:
			env = os.environ.copy()
			env['DEBIAN_FRONTEND'] = 'noninteractive'
			log_check_call(['/usr/sbin/chroot', info.root,
			                '/usr/bin/apt-get', 'install',
			                                    '--no-install-recommends',
			                                    '--assume-yes']
			               + packages,
			               env=env)
		except CalledProcessError as e:
			disk_stat = os.statvfs(info.root)
			root_free_mb = disk_stat.f_bsize * disk_stat.f_bavail / 1024 / 1024
			disk_stat = os.statvfs(os.path.join(info.root, 'boot'))
			boot_free_mb = disk_stat.f_bsize * disk_stat.f_bavail / 1024 / 1024
			free_mb = min(root_free_mb, boot_free_mb)
			if free_mb < 50:
				msg = ('apt exited with a non-zero status, '
				       'this may be because\nthe image volume is '
				       'running out of disk space ({free}MB left)').format(free=free_mb)
				logging.getLogger(__name__).warn(msg)
			raise e


class InstallLocalPackages(Task):
	description = 'Installing local packages'
	phase = phases.package_installation
	predecessors = [apt.AptUpgrade]
	successors = [InstallRemotePackages]

	def run(self, info):
		if len(info.packages.local) == 0:
			return
		from shutil import copy
		from common.tools import log_check_call
		import os

		for package_src in info.packages.local:
			pkg_name = os.path.basename(package_src)
			package_dst = os.path.join('/tmp', pkg_name)
			copy(package_src, os.path.join(info.root, package_dst))

			env = os.environ.copy()
			env['DEBIAN_FRONTEND'] = 'noninteractive'
			log_check_call(['/usr/sbin/chroot', info.root,
			                '/usr/bin/dpkg', '--install', package_dst],
			               env=env)
			os.remove(package_dst)