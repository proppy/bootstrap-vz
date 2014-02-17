from base import Task
from common import phases
from common.tasks import apt
import os.path
import os
from common.tools import log_check_call


class AddKernel(Task):
	description = 'Add appropriate kernel package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		kernels = {}
		with open('providers/ec2/tasks/packages-kernels.json') as stream:
			import json
			kernels = json.loads(stream.read())
		kernel_package = kernels.get(info.manifest.system['release']).get(info.manifest.system['architecture'])
		info.packages.add(kernel_package)
#		info.exclude_packages.add('isc-dhcp-client')
#		info.exclude_packages.add('isc-dhcp-common')


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
