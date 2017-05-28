from tool_box import *

def mount_union(ctx):
    cfg = ctx.config()
    union_mntroot = cfg.union_mntroot()
    testdir = cfg.testdir()
    if cfg.testing_none() and not cfg.testing_snapshot():
        lower_mntroot = cfg.lower_mntroot()
        system("mount -o remount,rw " + lower_mntroot)
        system("mount -o bind " + lower_mntroot + " " + union_mntroot)
        ctx.note_upper_fs(lower_mntroot, testdir)

    elif cfg.testing_unionmount():
        system("/root/util-linux-union/mount/mount -i -t tmpfs upper_layer " +
               union_mntroot + " -o union")
        ctx.note_upper_fs(testdir, testdir)

        if ctx.lower_fs() == ctx.upper_fs():
            raise TestError("Upper (" + ctx.upper_fs() + " and lower (" + ctx.lower_fs() +
                            ") shouldn't be the same")

    else:
        lower_mntroot = cfg.lower_mntroot()
        upper_mntroot = cfg.upper_mntroot()
        snapshot_mntroot = cfg.snapshot_mntroot()
        if cfg.is_samefs():
            base_mntroot = cfg.base_mntroot()
            system("mount -o remount,rw " + base_mntroot)
            try:
                os.mkdir(base_mntroot + upper_mntroot)
            except OSError:
                pass
            system("mount -o bind " + base_mntroot + upper_mntroot + " " + upper_mntroot)
        else:
            system("mount " + upper_mntroot + " 2>/dev/null"
                    " || mount -t tmpfs upper_layer " + upper_mntroot)
        upperdir = upper_mntroot + "/" + ctx.curr_layer()
        workdir = upper_mntroot + "/work" + ctx.curr_layer()
        try:
            os.mkdir(upperdir)
            os.mkdir(workdir)
        except OSError:
            system("rm -rf " + upper_mntroot + "/*")
            os.mkdir(upperdir)
            os.mkdir(workdir)

        mntopt = " -overify_lower"
        if cfg.testing_snapshot():
            system("mount -t overlay overlay " + snapshot_mntroot + mntopt +
                   ",lowerdir=" + lower_mntroot + ",upperdir=" + upperdir + ",workdir=" + workdir)
            system("mount -t snapshot snapshot " + union_mntroot +
                    " -oupperdir=" + lower_mntroot + ",snapshot=" + snapshot_mntroot)
            # The snapshot mounted on snapshot_mntroot is the latest snapshot taken.
            # This is a snapshot of beginning of test composed of all the incremental
            # layers since backup base to comapre with full backup at the end of the test:
            mid_layers = cfg.backup_mntroot() + "/base:"
            system("mount -t overlay overlay " + cfg.backup_mntroot() + "/snapshot/" +
                    " -oro,lowerdir=" + mid_layers + snapshot_mntroot)
            ctx.note_mid_layers(mid_layers)
            ctx.note_upper_fs(lower_mntroot, testdir)
        else:
            system("mount -t overlay overlay " + union_mntroot + mntopt +
                   ",lowerdir=" + lower_mntroot + ",upperdir=" + upperdir + ",workdir=" + workdir)
            ctx.note_upper_fs(upper_mntroot, testdir)
        ctx.note_upper_layer(upperdir)
