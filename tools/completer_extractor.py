import argparse
from string import Template



FILENAME = "completer_template"

def completer_extractor(parser, name):
    completer_dict = {"opts": [],
                      "subparser":{}} 

    print "parser: %s" % str(parser)
    for a in parser._actions:
        if type(a) is argparse._SubParsersAction:
            subparser_dict = a.choices
            for sarg in subparser_dict:
                sub_argument = subparser_dict[sarg]

                completer_dict["subparser"][sarg] = {"opts":[]}
                for sa in sub_argument._actions:
                    completer_dict["subparser"][sarg]["opts"].extend(sa.option_strings)
            continue


        if "option_strings" in dir(a):
            completer_dict["opts"].extend(a.option_strings)


    if "." in name:
        name = name.partition(".")[0]
    generate_completer(completer_dict, name)
    print "parser dict: %s" % str(completer_dict)

def generate_completer(completer_dict, name):
    print "name: %s" % name
    completer_file = FILENAME
    f = open(completer_file)
    completer = Template(f.read())
    f.close()


    completer = completer.safe_substitute(NAME = name)
    completer = Template(completer).safe_substitute(GLOBAL_OPTS = generate_opt_string(completer_dict))
    completer = Template(completer).safe_substitute(CMDS = generate_sub_commands(completer_dict["subparser"]))
    
    print "completer:\n%s" % completer
    f = open("%s" % name, "w")
    f.write(completer)
    f.close()



def generate_sub_commands(command_dict):
    subcommands = ""
    subcommands_opts = False
    subcommands += "\t\tcase \"${prev}\" in\n"
    for cmd in command_dict:
        gcmd = cmd.replace("-", "_")
        if len(command_dict[cmd]["opts"]) == 0:
            continue
        subcommands_opts = True
        subcommands += "\t\t\t%s)\n" % cmd
        subcommands += "\t\t\t\tlocal %s_opts=\"%s\"\n" % (gcmd, generate_opt_string(command_dict[cmd]))
        subcommands += "\t\t\t\tCOMPREPLY=($(compgen -W \"${%s_opts}\" -- ${cur}))\n" % (gcmd)
        subcommands += "\t\t\t\treturn 0\n"
        subcommands += "\t\t\t\t;;\n"

    subcommands += "\t\t\t*)\n"
    subcommands += "\t\t\t;;\n"
    subcommands += "\t\tesac\n"

    if not subcommands_opts:
        return ""
    return subcommands
    
def generate_opt_string(completer_dict):
    opts = completer_dict["opts"]
    opt_string = ""
    if "subparser" in completer_dict.keys():
        sub_commands = completer_dict["subparser"].keys()

        for sub_command in sub_commands:
            opt_string += sub_command
            opt_string += " "
        
    for i in range(len(opts)):
        opt = opts[i]
        opt_string += opt
        if i < (len(opts) - 1):
            opt_string += " "


    return opt_string
