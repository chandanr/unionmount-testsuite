from tool_box import *

def remount_union(ctx, rotate_upper=False):
    cfg = ctx.config()
    union_mntroot = cfg.union_mntroot()
    lower_mntroot = cfg.lower_mntroot()
    snapshot_mntroot = cfg.snapshot_mntroot()

    if cfg.testing_snapshot():
        system("umount " + cfg.backup_mntroot() + "/snapshot/")
        check_not_tainted()
        system("umount " + snapshot_mntroot)
        check_not_tainted()

    if cfg.testing_overlayfs() or cfg.testing_snapshot():
        system("umount " + cfg.union_mntroot())
        system("echo 3 > /proc/sys/vm/drop_caches")
        check_not_tainted()

        upper_mntroot = cfg.upper_mntroot()
        if rotate_upper and ctx.have_more_layers():
            # current upper is added to head of overlay mid layers or
            # to tail of snapshot mid layers
            if cfg.testing_snapshot():
                mid_layers = ctx.mid_layers() + ctx.upper_layer() + ":"
            else:
                mid_layers = ctx.upper_layer() + ":" + ctx.mid_layers()
            upperdir = upper_mntroot + "/" + ctx.next_layer()
            workdir = upper_mntroot + "/work" + ctx.curr_layer()
            os.mkdir(upperdir)
            os.mkdir(workdir)
        else:
            mid_layers = ctx.mid_layers()
            upperdir = ctx.upper_layer()
            workdir = upper_mntroot + "/work" + ctx.curr_layer()

        mntopt = " -orw"
        if cfg.testing_snapshot():
            # This is the latest snapshot of lower_mntroot:
            cmd = "mount -t overlay overlay " + snapshot_mntroot + mntopt + ",lowerdir=" + lower_mntroot + ",upperdir=" + upperdir + ",workdir=" + workdir
            system(cmd)
            if cfg.is_verbose():
                write_kmsg(cmd);
            system("mount -t snapshot snapshot " + union_mntroot +
                    " -oupperdir=" + lower_mntroot + ",snapshot=" + snapshot_mntroot)
            # The snapshot mounted on snapshot_mntroot is the latest snapshot taken.
            # This is a snapshot of beginning of test composed of all the incremental
            # layers since backup base to comapre with full backup at the end of the test:
            cmd = "mount -t overlay overlay " + cfg.backup_mntroot() + "/snapshot/" + " -oro,lowerdir=" + mid_layers + snapshot_mntroot
        else:
            cmd = "mount -t overlay overlay " + union_mntroot + mntopt + ",lowerdir=" + mid_layers + lower_mntroot + ",upperdir=" + upperdir + ",workdir=" + workdir
        system(cmd)
        if cfg.is_verbose():
            write_kmsg(cmd);
        ctx.note_mid_layers(mid_layers)
        ctx.note_upper_layer(upperdir)
