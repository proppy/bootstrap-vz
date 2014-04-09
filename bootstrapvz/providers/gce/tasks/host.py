from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import host, network
from bootstrapvz.common.tools import log_check_call
import os.path


class DisableIPv6(Task):
	description = "Disabling IPv6 support"
	phase = phases.system_modification
	predecessors = [network.ConfigureNetworkIF]

	@classmethod
	def run(cls, info):
		network_configuration_path = os.path.join(info.root, 'etc/sysctl.d/70-disable-ipv6.conf')
		with open(network_configuration_path, 'w') as config_file:
			print >>config_file, "net.ipv6.conf.all.disable_ipv6 = 1"


class FixNTPServer(Task):
	description = 'Change NTP to use server located on the host machine instead of Debian pool'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		if 'ntpserver' in info.manifest.system:
			ntpserver = info.manifest.system['ntpserver']
			if len(ntpserver) > 0:
				from bootstrapvz.common.tools import sed_i
				ntp_config_path = os.path.join(info.root, 'etc/ntp.conf')
				server_line = '^\s*server\s'
				sed_i(ntp_config_path, server_line, '#server')
				with open(ntp_config_path, 'w') as config_file:
					print >>config_file, "# Use server located on the host machine to avoid network traffic"
					print >>config_file, "server {ntpserver} iburst".format(ntpserver=ntpserver)


class SetHostname(Task):
	description = "Setting hostname"
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		log_check_call(['/usr/sbin/chroot', info.root,
			'/bin/ln', '-s',
			'/usr/share/google/set-hostname',
			'/etc/dhcp/dhclient-exit-hooks.d/set-hostname'])
