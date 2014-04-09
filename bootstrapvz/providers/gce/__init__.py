import tasks.apt
import tasks.boot
import tasks.configuration
import tasks.image
import tasks.host
import tasks.packages
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import partitioning
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import bootstrap
from bootstrapvz.common.tasks import security
from bootstrapvz.common.tasks import network
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tasks import cleanup
from bootstrapvz.common.tasks import workspace
import bootstrapvz.plugins.cloud_init.tasks

def initialize():
	pass


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)


def resolve_tasks(tasklist, manifest):
	import bootstrapvz.common.task_sets
	tasklist.update(bootstrapvz.common.task_sets.base_set)
	tasklist.update(bootstrapvz.common.task_sets.volume_set)
	tasklist.update(bootstrapvz.common.task_sets.mounting_set)
	tasklist.update(bootstrapvz.common.task_sets.get_apt_set(manifest))
	tasklist.update(bootstrapvz.common.task_sets.locale_set)

	tasklist.update(bootstrapvz.common.task_sets.bootloader_set.get(manifest.system['bootloader']))

	if manifest.volume['partitions']['type'] != 'none':
		tasklist.update(bootstrapvz.common.task_sets.partitioning_set)

	tasklist.update([
			bootstrapvz.plugins.cloud_init.tasks.AddBackports,
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

	tasklist.update(bootstrapvz.common.task_sets.get_fs_specific_set(manifest.volume['partitions']))

	if 'boot' in manifest.volume['partitions']:
		tasklist.update(bootstrapvz.common.task_sets.boot_partition_set)


def resolve_rollback_tasks(tasklist, manifest, counter_task):
	counter_task(loopback.Create, volume.Delete)
	counter_task(filesystem.CreateMountDir, filesystem.DeleteMountDir)
	counter_task(partitioning.MapPartitions, partitioning.UnmapPartitions)
	counter_task(filesystem.MountRoot, filesystem.UnmountRoot)
	counter_task(volume.Attach, volume.Detach)
	counter_task(workspace.CreateWorkspace, workspace.DeleteWorkspace)
