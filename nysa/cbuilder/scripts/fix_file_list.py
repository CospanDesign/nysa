import os

""" @package docstring
Python DRT interpreter
"""

class FixFileListError(Exception):
    """User gave an incorrect address
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def fix_file_list(file_list_path, project_dir, cbuilder_base):
    """
    Go through the list of files and make the path absolute
    """
    file_list = None
    try:
        f = open(file_list_path)
        file_list = file_list
    except IOError, err:
        raise FixFileListError("filelist.txt was not found: %s" % str(err))
 
    if not os.path.exists(cbuilder_base):
        raise FixFileListError("Cbuilder Dir does not exists: %s" % cbuilder_base)
 
    if not os.path.exists(project_dir):
        raise FixFileListError("Project Dir does not exists: %s" % project_dir)
    
    lines = file_list.read_lines()
    for line in lines:
        path = os.path.join(project_dir, "sim", line)
        if not os.path.exists(path):
            out_line = fix_path(line, project_dir, cbuilder_base)
            print "Changing %s to %s" % (line, out_line)


  


def fix_path(file_line, project_dir, cbuilder_base):
    """fix_path
 
    Currently this only fixes the references to the wishbone master, generic verilog
    or any of the code specifically for simulations
    """
    file_name = os.path.split(file_line)[-1]
    out_line = ""
 
    if file_name == "wishbone_master.v":
        print "Fix reference to wishbone master"
 
    elif file_name == "axi_master.v":
        print "Fix reference to axi master"
 
    print "Fixing path"
    return out_line
