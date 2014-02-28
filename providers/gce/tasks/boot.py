from base import Task
from common import phases
from common.tasks import boot
import os.path


class ConfigureGrub(Task):
	description = 'Change grub configuration to allow for ttyS0 output'
	phase = phases.system_modification
	successors = [boot.InstallGrub]

	@classmethod
	def run(cls, info):
		from common.tools import sed_i
		grub_config = os.path.join(info.root, 'etc/default/grub')
		sed_i(grub_config, r'^(GRUB_CMDLINE_LINUX*=".*)"\s*$', r'\1console=ttyS0,38400n8"')
#		sed_i(grub_config, r'^.*(GRUB_TERMINAL=).*$', r'\1"serial --unit=0 --speed=38400 --word=8 --parity=no --stop=1"')
		sed_i(grub_config, r'^.*(GRUB_TIMEOUT=).*$', r'GRUB_TIMEOUT=0')
