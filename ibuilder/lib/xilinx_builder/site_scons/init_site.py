def CleanBuild(env, targets):
    import os
    import shutil
    import utils
    if not env.GetOption('clean'):
        return
    # normalize targets to absolute paths
    config = utils.read_config(env)
    base_dir = utils.get_project_base()
    build_dir = utils.get_build_directory(config)
    xmsgs_dir = os.path.join(base_dir, "_xmsgs")

    print "Directories to remove:"
    print "\t%s" % build_dir
    print "\t%s" % xmsgs_dir

    #shutil.rmtree(build_dir)
    #shutil.rmtree(xmsg_dir)
    return 0

def CleanBuildActionFunc(env, targets, action):
    if CleanBuild(env, targets):
        env.Execute(action)

