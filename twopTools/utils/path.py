import os

def list_subdirs(rootdir, givepath=False):
    """ List subdirectories in a root directory.
    """
    paths = []; names = []
    for item in os.scandir(rootdir):
        if os.path.isdir(item):
            if item.name[0]!='.':
                paths.append(item.path)
                names.append(item.name)
    if givepath:
        return paths
    elif not givepath:
        return names