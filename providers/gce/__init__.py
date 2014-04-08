import tasks.apt
import tasks.boot
import tasks.configuration
import tasks.image
import tasks.host
import tasks.packages
from common.tasks import volume
from common.tasks import loopback
from common.tasks import partitioning
from common.tasks import filesystem
from common.tasks import bootstrap
from common.tasks import security
from common.tasks import network
from common.tasks import initd
from common.tasks import cleanup
from common.tasks import workspace
import plugins.cloud_init.tasks
import providers.ec2.tasks.network

def initialize():
	pass


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(tasklist, manifest):
	import common.task_sets
	tasklist.update(common.task_sets.base_set)
	tasklist.update(common.task_sets.volume_set)
	tasklist.update(common.task_sets.mounting_set)
	tasklist.update(common.task_sets.get_apt_set(manifest))
	tasklist.update(common.task_sets.locale_set)

	tasklist.update(common.task_sets.bootloader_set.get(manifest.system['bootloader']))

	if manifest.volume['partitions']['type'] != 'none':
		tasklist.update(common.task_sets.partitioning_set)

	tasklist.update([
			plugins.cloud_init.tasks.AddBackports,
			loopback.Create,
			tasks.apt.SetPackageRepositories,
			tasks.apt.PreferKernelsFromBackports,
			tasks.apt.ImportGoogleKey,
			tasks.packages.DefaultPackages,
			tasks.packages.GooglePackages,
			tasks.packages.InstallGSUtil,

			tasks.configuration.GatherReleaseInformation,

			security.EnableShadowConfig,
	                network.RemoveDNSInfo,
	                network.RemoveHostname,
	                network.ConfigureNetworkIF,
			tasks.host.FixNTPServer,
			tasks.host.DisableIPv6,
			tasks.host.SetHostname,
			tasks.boot.ConfigureGrub,
			initd.AddSSHKeyGeneration,
			initd.InstallInitScripts,
			tasks.apt.CleanGoogleRepositoriesAndKeys,

			loopback.MoveImage,
			tasks.image.CreateTarball,
			tasks.image.RegisterImage,
			])

	tasklist.update(common.task_sets.get_fs_specific_set(manifest.volume['partitions']))

	if 'boot' in manifest.volume['partitions']:
		tasklist.update(common.task_sets.boot_partition_set)


def resolve_rollback_tasks(tasklist, manifest, counter_task):
	counter_task(loopback.Create, volume.Delete)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(filesystem.MountRoot, filesystem.UnmountRoot)
	counter_task(volume.Attach, volume.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
