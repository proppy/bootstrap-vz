from base import Task
from common import phases
from common.tasks import apt
import os.path
import os
from common.tools import log_check_call


class DefaultPackages(Task):
	description = 'Adding image packages required for GCE'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('python')
		info.packages.add('sudo')
		info.packages.add('ntp')
		info.packages.add('lsb-release')
		info.packages.add('acpi-support-base')
		info.packages.add('openssh-client')
		info.packages.add('openssh-server')
		info.packages.add('dhcpd')
# Excluded in EC2, should we exclude them?
#		info.exclude_packages.add('isc-dhcp-client')
#		info.exclude_packages.add('isc-dhcp-common')

		kernels = {}
		with open('providers/ec2/tasks/packages-kernels.json') as stream:
			import json
			kernels = json.loads(stream.read())
		kernel_package = kernels.get(info.manifest.system['release']).get(info.manifest.system['architecture'])
		info.packages.add(kernel_package)


class GooglePackages(Task):
	description = 'Adding image packages required for GCE from Google repositories'
	phase = phases.preparation
	predecessors = [DefaultPackages]

	@classmethod
	def run(cls, info):
		info.packages.add('google-compute-daemon')
		info.packages.add('google-startup-scripts')
		info.packages.add('python-gcimagebundle')
		info.packages.add('gcutil')


class InstallGSUtil(Task):
	description = 'Install gsutil, not yet packaged'
	phase = phases.package_installation

	@classmethod
	def run(cls, info):
		log_check_call(['/usr/bin/wget', 'http://storage.googleapis.com/pub/gsutil.tar.gz'])
		gsutil_directory = os.path.join(info.root, 'usr/local/share/google')
		gsutil_binary = os.path.join(os.path.join(info.root, 'usr/local/bin'), 'gsutil')
		os.makedirs(gsutil_directory)
		log_check_call(['/bin/tar', 'xaf', 'gsutil.tar.gz', '-C', gsutil_directory])
		log_check_call(['/bin/ln', '-s', '../share/google/gsutil/gsutil', gsutil_binary])
