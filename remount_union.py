from tool_box import *

def remount_union(ctx, rotate_upper=False, cycle_mount=False):
    cfg = ctx.config()
    union_mntroot = cfg.union_mntroot()
    lower_mntroot = cfg.lower_mntroot()
    upper_mntroot = cfg.upper_mntroot()
    snapshot_mntroot = cfg.snapshot_mntroot()
    if not ctx.have_more_layers():
        rotate_upper = False
    if not cfg.testing_snapshot() or not ctx.remount():
        cycle_mount = True

    if cfg.testing_overlayfs() or cfg.testing_snapshot():
        if cycle_mount:
            system("umount " + cfg.union_mntroot())
            system("echo 3 > /proc/sys/vm/drop_caches")
            check_not_tainted()

        if rotate_upper:
            # current upper is added to head of overlay mid layers
            mid_layers = ctx.upper_layer() + ":" + ctx.mid_layers()
            upperdir = upper_mntroot + "/" + ctx.next_layer()
            workdir = upper_mntroot + "/work" + ctx.curr_layer()
            os.mkdir(upperdir)
            os.mkdir(workdir)
        else:
            mid_layers = ctx.mid_layers()
            upperdir = ctx.upper_layer()
            workdir = upper_mntroot + "/work" + ctx.curr_layer()

        mntopt = " -overify_lower"
        if cfg.testing_snapshot():
            if rotate_upper or cycle_mount:
                # Unmount old snapshots when mount cycling snapshot mount
                # and when rotating latest snapshot into old snapshot stack
                try:
                    system("umount " + cfg.snapshot_mntroot() + "/*/ 2>/dev/null")
                except RuntimeError:
                    pass
                check_not_tainted()

            curr_snapshot = snapshot_mntroot + "/" + ctx.curr_layer()
            if rotate_upper:
                os.mkdir(curr_snapshot)
                os.mkdir(cfg.backup_mntroot() + "/full/" + ctx.curr_layer())
                # Create a backup copy of lower layer for comparing with snapshotat the end of the test run
                system("cp -a " + lower_mntroot + "/a " + cfg.backup_mntroot() + "/full/" + ctx.curr_layer() + "/")

            snapmntopt = " -o rw"
            # verify_lower on snapshot mount only with single snapshot test
            if ctx.max_layers() == 0:
                snapmntopt = snapmntopt + ",verify_lower"
            if rotate_upper or cycle_mount:
                # This is the latest snapshot of lower_mntroot:
                cmd = "mount -t overlay overlay " + curr_snapshot + mntopt + ",lowerdir=" + lower_mntroot + ",upperdir=" + upperdir + ",workdir=" + workdir
                system(cmd)
                write_file("/dev/kmsg", cmd);

            if cycle_mount:
                # This is the snapshot mount where tests are run
                system("mount -t snapshot snapshot " + union_mntroot + snapmntopt +
                        ",upperdir=" + lower_mntroot + ",snapshot=" + curr_snapshot)
            else:
                # Cycle remount snapshot mount ro/rw to use the new curr_snapshot
                system("mount -t snapshot snapshot " + union_mntroot + " -oremount,ro,snapshot=" + curr_snapshot)
                system("mount -t snapshot snapshot " + union_mntroot + " -oremount,rw")

            if rotate_upper or cycle_mount:
                # Remount latest snapshot readonly
                system("mount " + curr_snapshot + " -oremount,ro")
                mid_layers = ""
                # Mount old snapshots, possibly pushing the rotated previous snapshot into stack
                for i in range(ctx.layers_nr() - 1, -1, -1):
                    mid_layers = upper_mntroot + "/" + str(i) + ":" + mid_layers
                    cmd = "mount -t overlay overlay " + snapshot_mntroot + "/" + str(i) + "/" + " -oro,lowerdir=" + mid_layers + curr_snapshot
                    system(cmd)
                    write_file("/dev/kmsg", cmd);
        else:
            cmd = "mount -t overlay overlay " + union_mntroot + mntopt + ",lowerdir=" + mid_layers + lower_mntroot + ",upperdir=" + upperdir + ",workdir=" + workdir
            system(cmd)
            write_file("/dev/kmsg", cmd);
        ctx.note_mid_layers(mid_layers)
        ctx.note_upper_layer(upperdir)
