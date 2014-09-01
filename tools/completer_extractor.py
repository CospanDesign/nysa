import argparse
from string import Template



FILENAME = "completer_template"
DEBUG = True
SUBCOMMANDS_OPTS = False

def _parser2dict(parser):
    #Recursive dictionary extractor"
    cdict = {}
    for a in parser._actions:
        if type(a) is argparse._SubParsersAction:        
            if "subparser" not in cdict:
                cdict["subparser"] = {}
            subparser_dict = a.choices
            for sarg in subparser_dict:
                subparser = subparser_dict[sarg]
                cdict["subparser"][sarg] = _parser2dict(subparser)
            continue

        if "option_strings" in dir(a):
            if "opts" not in cdict:
                cdict["opts"] = []
            cdict["opts"].extend(a.option_strings)

    return cdict

def completer_extractor(parser, name):

    cdict = _parser2dict(parser)
    if "." in name:
        name = name.partition(".")[0]

    if DEBUG:
        print "parser dict: %s" % str(cdict)
    generate_completer(cdict, name)

def generate_completer(cdict, name):
    print "name: %s" % name
    completer_file = FILENAME
    f = open(completer_file)
    completer = Template(f.read())
    f.close()

    completer = completer.safe_substitute(NAME = name)
    completer = Template(completer).safe_substitute(GLOBAL_OPTS = generate_opt_string(cdict))
    completer = Template(completer).safe_substitute(CMDS = generate_sub_commands(cdict["subparser"]))
    
    print "completer:\n%s" % completer
    f = open("%s" % name, "w")
    f.write(completer)
    f.close()


def _generate_sub_commands(cmd_dict, cmd_depth):
    subcommands = ""
    global SUBCOMMANDS_OPTS
    #subcommands += ddepth_str + "%d)\n" % (depth + 2)
    depth_str = "\t\t"
    ddepth_str = "\t\t"
    for d in range(cmd_depth):
        ddepth_str += depth_str 

    subcommands += ddepth_str + "case \"${COMP_WORDS[%s]}\" in\n" % cmd_depth

    for cmd in cmd_dict:
        gcmd = cmd.replace("-", "_")

        if len(cmd_dict[cmd]["opts"]) == 0:
            continue
        SUBCOMMANDS_OPTS = True
        subcommands += ddepth_str + "\t%s)\n" % cmd
        subcommands += ddepth_str + "\t\tlocal %s_opts=\"%s\"\n" % (gcmd, generate_opt_string(cmd_dict[cmd]))
        #print "cmd_dict: %s" % str(cmd_dict[cmd])
        if "subparser" in cmd_dict[cmd]:
            print "subparser!"
            subcommands += _generate_sub_commands(cmd_dict[cmd]["subparser"], cmd_depth + 1)
        subcommands += ddepth_str + "\t\tCOMPREPLY=($(compgen -W \"${%s_opts}\" -- ${cur}))\n" % (gcmd)
        subcommands += ddepth_str + "\t\treturn 0\n"
        subcommands += ddepth_str + "\t\t;;\n"

    subcommands += ddepth_str + "\t*)\n"
    subcommands += ddepth_str + "\t;;\n"
    subcommands += ddepth_str + "esac\n"

    return subcommands

def generate_sub_commands(cmd_dict):

    depth = 0
    depth_str = "\t\t"
    ddepth_str = depth_str + depth_str
    cmd_depth = 1
    global SUBCOMMANDS_OPTS
    
    subcommands = ""
    SUBCOMMANDS_OPTS = False
    subcommands += depth_str + "if [ $COMP_CWORD -gt 1 ]; then\n"
    subcommands += ddepth_str + "#echo \"subcommands!\"\n"
    #Sub Command Start

    subcommands += _generate_sub_commands(cmd_dict, cmd_depth)
    '''
    #subcommands += ddepth_str + "%d)\n" % (depth + 2)
    subcommands += ddepth_str + "case \"${COMP_WORDS[%s]}\" in\n" % cmd_depth

    for cmd in cmd_dict:
        gcmd = cmd.replace("-", "_")

        if len(cmd_dict[cmd]["opts"]) == 0:
            continue
        SUBCOMMANDS_OPTS = True
        subcommands += ddepth_str + "\t%s)\n" % cmd
        subcommands += ddepth_str + "\t\tlocal %s_opts=\"%s\"\n" % (gcmd, generate_opt_string(cmd_dict[cmd]))
        subcommands += ddepth_str + "\t\tCOMPREPLY=($(compgen -W \"${%s_opts}\" -- ${cur}))\n" % (gcmd)
        subcommands += ddepth_str + "\t\treturn 0\n"
        subcommands += ddepth_str + "\t\t;;\n"

    subcommands += ddepth_str + "\t*)\n"
    subcommands += ddepth_str + "\t;;\n"
    subcommands += ddepth_str + "esac\n"
    '''



    #Sub Command End
    #subcommands += ddepth_str + ";;\n"
    #subcommands += depth_str + "\t*)\n"
    #subcommands += depth_str + "\t;;\n"
    subcommands += depth_str + "fi\n"



    if not SUBCOMMANDS_OPTS:
        return ""
    return subcommands
    
def generate_opt_string(cdict):
    opts = cdict["opts"]
    opt_string = ""
    if "subparser" in cdict.keys():
        sub_commands = cdict["subparser"].keys()

        for sub_command in sub_commands:
            opt_string += sub_command
            opt_string += " "
        
    for i in range(len(opts)):
        opt = opts[i]
        opt_string += opt
        if i < (len(opts) - 1):
            opt_string += " "


    return opt_string
