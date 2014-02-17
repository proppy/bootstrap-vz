from base import Task
from common import phases
import os.path


class FixNTPServer(Task):
	description = 'Change NTP to use server located on the host machine instead of Debian pool'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from common.tools import sed_i
#		import re
#		regex = re.compile('^server\s+')
		ntp_config_path = os.path.join(info.root, 'etc/ntp.conf')
		server_line = '^\s*server\s'
		sed_i(ntp_config_path, server_line, '#server')
#		with open(ntp_config_path) as config_file:
#			config_lines = config_file.readlines()
		with open(ntp_config_path, 'w') as config_file:
#			for line in config_lines:
#				if regex.match(line) is None:
#					print >>config_file, line
			print >>config_file, "# Use server located on the host machine to avoid network traffic"
			print >>config_file, "server metadata.google.internal iburst"
