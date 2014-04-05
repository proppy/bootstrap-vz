from base import Task
from common import phases
import os.path


class FixNTPServer(Task):
	description = 'Change NTP to use server located on the host machine instead of Debian pool'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		if 'ntpserver' in info.manifest.system:
			ntpserver = info.manifest.system['ntpserver']
			if len(ntpserver) > 0:
				from common.tools import sed_i
				ntp_config_path = os.path.join(info.root, 'etc/ntp.conf')
				server_line = '^\s*server\s'
				sed_i(ntp_config_path, server_line, '#server')
				with open(ntp_config_path, 'w') as config_file:
					print >>config_file, "# Use server located on the host machine to avoid network traffic"
					print >>config_file, "server {ntpserver} iburst".format(ntpserver=ntpserver)
