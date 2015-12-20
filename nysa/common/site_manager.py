import os
import sys
import urllib
import urllib2
import json
import site
import shutil
import csv
import zipfile
import tempfile
import datetime
import subprocess
import importlib
import inspect
from cookielib import CookieJar
from urllib2 import build_opener, HTTPCookieProcessor
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

SITE_PATH = os.path.join(site.USER_BASE, "nysa")
VERSION_PATH = os.path.join(SITE_PATH, "versions.json")
PATHS_PATH = os.path.join(SITE_PATH, "paths.json")
BOARD_ID_PATH = os.path.join(SITE_PATH, "board_id.json")
#REMOTE_PACKAGE_URL = "http://www.cospandesign.com/nysa/packages"
BOARD_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1dif3JBFwjEiNVn5hNxr2ZQ58ypy1LqTsKIlVk3pWVtE/export?format=csv"
VERILOG_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1fyr9G2sVVa1bOi3Rtg9uGz0KELReo8buoTrP8DQfNTA/export?format=csv"
EXAMPLE_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1GUzVnXB6StrfuYKXzCwm1_E4CBtUDDj5a-C-Fi5IQOc/export?format=csv"
BOARD_PACKAGE_PATH = os.path.join(SITE_PATH, "boards")
COCOTB_URL = "https://github.com/potentialventures/cocotb.git"

VERILOG_PACKAGE_PATH = os.path.join(SITE_PATH, "verilog")
COCOTB_PATH = os.path.join(SITE_PATH, "cocotb")
DEFAULT_BOARD_BRANCH = "master"

NYSA_MODULE_LOC = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
USER_BASE = "nysa_base"
DEFAULT_USER_BASE = os.path.join(os.path.expanduser("~"), "Projects", USER_BASE)

paths_dict = None

USER_BASE_VERILOG_DIR = "verilog"
USER_BASE_EXAMPLES_DIR = "examples"
USER_BASE_DEV_DIR = "dev"
USER_BASE_APP_DIR = "apps"
USER_BASE_IBUILDER_DIR = "user_ibuilder_projects"
USER_BASE_CBUILDER_DIR = "user_cbuilder_projects"

def get_python_install_dir():
    p = None
    if os.name == "nt":
        from distutils.sysconfig import get_python_lib
        return get_python_lib()
    try:
        p = site.getsitepackages()[0]
    except AttributeError as e:
        from distutils.sysconfig import get_python_lib
        p = get_python_lib()
    return p

def get_paths_path():
    return PATHS_PATH

def get_site_path():
    return SITE_PATH

def get_versions_path():
    return VERSION_PATH

def get_board_package_path():
    return BOARD_PACKAGE_PATH

def get_verilog_package_path():
    return VERILOG_PACKAGE_PATH

def get_board_id_path():
    return BOARD_ID_PATH

class LocalDefinition(Exception):
    pass

class RemoteDefinition(Exception):
    pass

class SiteManagerError(Exception):
    pass

class SiteManager(object):

    def __init__(self, status = None):

        self.s = status

        if not os.path.exists(SITE_PATH):
            os.makedirs(os.path.join(SITE_PATH))

        if not os.path.exists(VERSION_PATH):
            #Doesn't exists, create a reference to it
            f = open(VERSION_PATH, "w")
            f.write("{}")
            f.close()

        self.initialize_paths_dictionary()
        self.initialize_board_id_dictionary()

    def initialize_board_id_dictionary(self):
        if not os.path.exists(get_board_id_path()):
            f = open(get_board_id_path(), "w")
            f.write("{}")
            f.close()

    def initialize_paths_dictionary(self):
        if not os.path.exists(get_paths_path()):
            #Doesn't exists, create a reference to it
            f = open(get_paths_path(), "w")
            f.write("{}")
            f.close()

        paths_dict = None
        try:
            f = open(get_paths_path(), "r")
            paths_dict = json.load(f)
            f.close()
        except ValueError as e:
            f = open(get_paths_path(), "w")
            f.write("{}")
            f.close()
            f = open(get_paths_path(), "r")
            paths_dict = json.load(f)
            f.close()

        if "boards" not in paths_dict:
            paths_dict["boards"] = {}
        if "verilog" not in paths_dict:
            paths_dict["verilog"] = {}

        paths_dict["nysa"] = NYSA_MODULE_LOC
        paths_dict["nysa_user_base"] = DEFAULT_USER_BASE

        f = open(get_paths_path(), "w")
        f.write(json.dumps(paths_dict, sort_keys = True, indent = 2, separators=(",", ": ")))
        f.close()

    def _create_site_dir(self):
        os.makedirs(os.path.join(SITE_PATH))

    def _site_dir_exists(self):
        return os.path.exists(SITE_PATH)

    def _remove_local_site_dir(self):
        shutil.rmtree(SITE_PATH)

    def get_paths_dict(self, force = False):
        global paths_dict
        ##print "pre path dict: %s" % str(paths_dict)
        #if paths_dict is not None or force:
        #    #print "\tGetting cached version"
        #    return paths_dict
        ##print "\tGetting non-cached version"
        f = open(get_paths_path())
        paths_dict = json.load(f)
        f.close()
        return paths_dict

    def get_local_board_names(self):
        paths_dict = self.get_paths_dict()
        return paths_dict["boards"].keys()

    def get_board_directory(self, name):
        paths_dict = self.get_paths_dict()
        name = name.lower()
        if name not in paths_dict["boards"]:
            raise SiteManagerError("Board: %s doesn't exists" % name)
        return paths_dict["boards"][name]["path"]

    def board_exists(self, name):
        paths_dict = self.get_paths_dict()
        for board_name in paths_dict["boards"]:
            if board_name.lower() == name.lower():
                if os.path.exists(paths_dict["boards"][board_name]["path"]):
                    return True
        return False

    def add_board(self, name, timestamp, path):
        paths_dict = self.get_paths_dict(force = True)
        paths_dict["boards"][name] = {}
        paths_dict["boards"][name]["timestamp"] = timestamp
        paths_dict["boards"][name]["path"] = path
        f = open(get_paths_path(), "w")
        f.write(json.dumps(paths_dict, sort_keys = True, indent = 2, separators=(",", ": ")))
        f.close()

    def add_verilog_package(self, name, timestamp, path):
        paths_dict = self.get_paths_dict()
        if self.s: self.s.Debug("\tName: %s" % name)
        if self.s: self.s.Debug("\tTimestamp: %s" % timestamp)
        if self.s: self.s.Debug("\tPath: %s" % path)
        paths_dict["verilog"][name] = {}
        paths_dict["verilog"][name]["timestamp"] = timestamp
        paths_dict["verilog"][name]["path"] = path
        f = open(get_paths_path(), "w")
        f.write(json.dumps(paths_dict, sort_keys = True, indent = 2, separators=(",", ": ")))
        f.close()
        self.get_paths_dict(force = True)

    def get_remote_verilog_dict(self, url = None):
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        resp = opener.open(VERILOG_SPREADSHEET_URL)
        data = resp.read()
        data = data.strip()
        row_data = data.split("\n")
        grid_data = []
        for i in range (len(row_data)):
            grid_data.append([])
            grid_data[i].extend(row_data[i].split(","))

        grid_data.remove(grid_data[0])

        repo_dict = {}
        for row in grid_data:
            name = row[1].lower()
            repo_dict[name] = {}
            repo_dict[name]["timestamp"] = row[0].strip()
            repo_dict[name]["repository"] = row[2].strip()

        return repo_dict

    def get_remote_board_dict(self, url = None):
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        resp = opener.open(BOARD_SPREADSHEET_URL)
        data = resp.read()
        row_data = data.split("\n")
        grid_data = []
        for i in range (len(row_data)):
            grid_data.append([])
            grid_data[i].extend(row_data[i].split(","))

        grid_data.remove(grid_data[0])

        board_dict = {}
        for row in grid_data:
            name = row[1].lower()
            board_dict[name] = {}
            board_dict[name]["timestamp"] = row[0].strip()
            board_dict[name]["repository"] = row[2].strip()
            board_dict[name]["pip"] = row[3].strip()

        return board_dict

    def import_board_package(self, name, url):
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        resp = opener.open(BOARD_SPREADSHEET_URL)
        data = resp.read()

    def remote_board_exists(self, name):
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        resp = opener.open(BOARD_SPREADSHEET_URL)
        data = resp.read()
        data = data.strip()
        row_data = data.split("\n")
        grid_data = []
        for i in range(len(row_data)):
            grid_data.append([])
            grid_data[i].extend(row_data[i].split(","))

        #print "grid data: %s" % str(grid_data)
        for row in grid_data:
            #print "row: %s" % str(row)
            if row[0].strip() == "Timestamp":
                continue
            if row[1].lower() == name.lower():
                return True
        return False

    def install_verilog_module(self, name = None):
        repo_dict = self.get_remote_verilog_dict()

        names = []
        if name is None:
            #All platforms
            names = repo_dict.keys()
            if self.s: self.s.Important("Installing all verilog repositories")

        elif isinstance(name, list):
            print "list: %s" % name

            if len(name) == 0:
                #All of them
                name = repo_dict.keys()
            for n in name:
                if n not in repo_dict.keys():
                    #Check to see if this is a valid platform
                    err_str = "" \
                    "Error %s is not a valid verilog repository!\n" \
                    "Valid repos include:\n"
                    for nm in repo_dict.keys():
                        err_str += "\t%s\n" % nm

                    err_str += "\n"
                    raise SiteManagerError(err_str)
                    
                if self.s: self.s.Debug("Found: %s" % n)
                names.append(n)

        elif name == "all":
            #All platforms
            names = repo_dict.keys()
            if self.s: self.s.Important("Installing all repository")

        else:
            if name not in repo_dict.keys():
                #Check to see if this is a valid platform
                err_str = "" \
                "Error %s is not a valid repository!\n" \
                "Valid platforms include:\n"
                for n in repo_dict.keys():
                    err_str += "\t%s\n" % n

                err_str += "\n"
                raise SiteManagerError(err_str)

            names = [name]

        now = datetime.datetime.now()
        timestamp = now.strftime("%x %X")
        name = None
        for name in names:
            if self.s: self.s.Important("Installing verilog repo: %s" % name)
            self.update_verilog_package(name)

    def install_remote_board_package(self, name = None, branch = DEFAULT_BOARD_BRANCH):
        install_dir = get_python_install_dir()

        #get the online board dictionary
        board_dict = self.get_remote_board_dict()

        names = []
        if name is None:
            #All platforms
            names = board_dict.keys()
            if self.s: self.s.Important("Installing all platforms")

        elif isinstance(name, list):
            print "list: %s" % name

            if len(name) == 0:
                #All of them
                name = board_dict.keys()
            for n in name:
                if n not in board_dict.keys():
                    #Check to see if this is a valid platform
                    err_str = "" \
                    "Error %s is not a valid platform!\n" \
                    "Valid platforms include:\n"
                    for nm in board_dict.keys():
                        err_str += "\t%s\n" % nm

                    err_str += "\n"
                    raise SiteManagerError(err_str)

                names.append(n)

        elif name == "all":
            #All platforms
            names = board_dict.keys()
            if self.s: self.s.Important("Installing all platforms")

        else:
            if name not in board_dict.keys():
                #Check to see if this is a valid platform
                err_str = "" \
                "Error %s is not a valid platform!\n" \
                "Valid platforms include:\n"
                for n in board_dict.keys():
                    err_str += "\t%s\n" % n

                err_str += "\n"
                raise SiteManagerError(err_str)

            names = [name]
            if self.s: self.s.Important("Installing %s" % name)

        now = datetime.datetime.now()
        timestamp = now.strftime("%x %X")
        name = None

        for name in names:
            if self.s: self.s.Important("Installing: %s" % name)
            if len(board_dict[name]["pip"]) == 0:
                board_dict[name]["pip"] = "git+" + board_dict[name]["repository"] + ".git"
            if self.s: self.s.Important("Installing from URL: %s" % (board_dict[name]["pip"]))

            v = None
            if os.name == "nt" or ("Anaconda" in sys.version):
                v = subprocess.call(["pip", "install", "--upgrade", board_dict[name]["pip"]])
            else:
                v = subprocess.call(["sudo", "pip", "install", "--upgrade", board_dict[name]["pip"]])

            self.add_board(name, timestamp, install_dir)
            if self.s: self.s.Important("Updating path dictionary")
            #check if there is any setup to do
            import_str = "%s.nysa_platform" % name
            #package = importlib.import_module(import_str)
            #platform = package.nysa_platform
            platform = importlib.import_module(import_str)

            pdict = inspect.getmembers(platform)
            from nysa.host.nysa_platform import Platform
            for member_name, obj in pdict:
                if inspect.isclass(obj) and issubclass(obj, Platform) and obj is not Platform:
                    if self.s: self.s.Info("Calling platform specific setup function")
                    p = obj(self.s)
                    p.setup_platform()

        if self.s: self.s.Info("Wrote path dictionary to config file @ %s" % SITE_PATH)

    def get_board_id_dict(self):
        f = open(get_board_id_path(), "r")
        board_id_dict = json.load(f)
        f.close()
        return board_id_dict

    def update_board_id_dict(self, grid_data = None):
        if grid_data is None:
            opener = build_opener(HTTPCookieProcessor(CookieJar()))
            resp = opener.open(BOARD_SPREADSHEET_URL)
            data = resp.read()
            data = data.strip()
            row_data = data.split("\n")
            grid_data = []
            for i in range(len(row_data)):
                grid_data.append([])
                grid_data[i].extend(row_data[i].split(","))

        board_id_dict = self.get_board_id_dict()
        for row in grid_data:
            index = grid_data.index(row)
            if index == 0:
                continue
            name = row[1].lower()
            board_id_dict[name] = index

        f = open(get_board_id_path(), "w")
        f.write(json.dumps(board_id_dict, sort_keys = True, indent = 2, separators=(",", ": ")))
        f.close()

    def get_local_verilog_package_names(self):
        paths_dict = self.get_paths_dict()
        return paths_dict["verilog"].keys()

    def get_local_verilog_paths(self):
        verilog_paths = []
        paths_dict = self.get_paths_dict()

        for vkey in paths_dict["verilog"]:
            verilog_paths.append(paths_dict["verilog"][vkey]["path"])

        return verilog_paths

    def get_local_verilog_package_path(self, name):
        paths_dict = self.get_paths_dict()
        return paths_dict["verilog"][name]["path"]

    def verilog_package_exists(self, name):
        paths_dict = self.get_paths_dict()
        if name in paths_dict["verilog"].keys():
            return True
        return False

    def clean_verilog_package_paths(self):
        paths_dict = self.get_paths_dict()
        del_list = []
        del_found = False
        for vpackage in paths_dict["verilog"]:
            if not os.path.exists(paths_dict["verilog"][vpackage]["path"]):
                del_found = True
                del_list.append(vpackage)

        for vpackage in del_list:
            del(paths_dict["verilog"][vpackage])

        if del_found:
            f = open(get_paths_path(), "w")
            f.write(json.dumps(paths_dict, sort_keys = True, indent = 2, separators=(",", ": ")))
            f.close()
            self.get_paths_dict(force = True)

    def update_verilog_package(self, name = None, branch = ""):
        if name is None:
            name = "nysa-verilog"
        if len(branch) == 0:
            branch = DEFAULT_BOARD_BRANCH

        name = name.lower()

        if self.s: self.s.Debug("Fetching verilog repo spreadsheet data")
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        resp = opener.open(VERILOG_SPREADSHEET_URL)
        data = resp.read()
        data = data.strip()
        row_data = data.split("\n")
        grid_data = []
        result = None
        for i in range(len(row_data)):
            grid_data.append([])
            grid_data[i].extend(row_data[i].split(","))

        #print "grid data: %s" % str(grid_data)
        for row in grid_data:
            index = grid_data.index(row)
            if index == 0:
                continue
            remote_name = row[1].lower()
            if remote_name == name:
                result = row
                #Found the package

        if result is None:
            raise SiteManagerError("Did not find remote verilog package: %s" % name)

        if self.s: self.s.Debug("Found remote verilog package: %s" % name)

        url = result[2].strip()
        print "URL: %s" % url
        timestamp = result[0]
        archive_url = url
        if url.endswith('zip'):
            print "Found zip file URL"
            raise SiteManagerError("Current version of stie manager can only fetch Github URLs")
        elif "github" not in url:
            raise SiteManagerError("Current version of site manager can only fetch Github URLs")

        if "github" in url:
            #if self.s: self.s.Debug("\tGenerting a gitub archive URL!")
            archive_url += "/archive/" +  branch + ".zip" 

        #opener = build_opener(HTTPCookieProcessor(CookieJar()))
        #resp = opener.open(archive_url)
        #data = resp.read()

        if not os.path.exists(get_verilog_package_path()):
            os.makedirs(get_verilog_package_path())

        tempdir = tempfile.mkdtemp()
        #tempdir = get_verilog_package_path()
        temparchive = os.path.join(tempdir, "archive.zip")
        urllib.urlretrieve(archive_url, temparchive)
        #f = open(temparchive, "a")
        #f.write(data)
        #f.close()

        zf = zipfile.ZipFile(temparchive, "a")
        zf.extractall(get_verilog_package_path())
        zf.close()
        shutil.rmtree(tempdir)
        dir_name = "%s-%s" % (url.rpartition("/")[2], branch)

        verilog_dir = os.path.join(get_verilog_package_path(), dir_name)
        if self.s: self.s.Debug("Adding verilog package now")
        self.add_verilog_package(name, timestamp, verilog_dir)
        if self.s: self.s.Debug("Refreshing paths dict")
        self.get_paths_dict(force = True)

    def get_nysa_user_base_directory(self):
        pd = self.get_paths_dict()
        if "nysa_user_base" not in pd:
            raise SiteManagerError("Nysa user base is not set up! run nysa init to initialize a user directory")
        return pd["nysa_user_base"]

    def get_remote_example_dict(self):
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        resp = opener.open(EXAMPLE_SPREADSHEET_URL)
        data = resp.read()
        data = data.strip()
        row_data = data.split("\n")
        grid_data = []
        for i in range (len(row_data)):
            grid_data.append([])
            grid_data[i].extend(row_data[i].split(","))

        grid_data.remove(grid_data[0])

        repo_dict = {}
        for row in grid_data:
            name = row[1].lower()
            repo_dict[name] = {}
            repo_dict[name]["timestamp"] = row[0].strip()
            repo_dict[name]["repository"] = row[2].strip()

        return repo_dict

    def install_examples(self, name, dest, branch = None):
        name = name.lower()
        if branch is None:
            branch = DEFAULT_BOARD_BRANCH

        if self.s: self.s.Debug("Fetching example repo spreadsheet data")
        ex_dict = self.get_remote_example_dict()

        if name not in ex_dict:
            raise SiteManagerError("Did not find remote example package: %s" % name)

        if self.s: self.s.Debug("Found remote example package: %s" % name)
        url = ex_dict[name]["repository"].strip()
        archive_url = None
        branch = "master"
        if url.endswith('zip'):
            print "Found zip file URL"
            raise SiteManagerError("Current version of stie manager can only fetch Github URLs")
        elif "github" not in url:
            raise SiteManagerError("Current version of site manager can only fetch Github URLs")

        if "github" in url:
            archive_url = url + "/archive/%s.zip" % branch

        if not os.path.exists(dest):
            os.makedirs(dest)

        tempdir = tempfile.mkdtemp()
        temparchive = os.path.join(tempdir, "archive.zip")
        urllib.urlretrieve(archive_url, temparchive)

        zf = zipfile.ZipFile(temparchive, "a")
        temp_examples = os.path.join(tempdir, "examples")
        os.makedirs(temp_examples)
        zf.extractall(temp_examples)
        zf.close()

        #Copy everything within that directory to the desired output
        name = os.path.walk

        dir_name = None

        for dirname, dirnames, filenames in os.walk(temp_examples):
            dir_name = dirnames[0]
            break

        source = os.path.join(temp_examples, dir_name)

        #print "Removing: %s" % dest
        #print "Copying over from: %s to %s" % (source, dest)
        try:
            shutil.rmtree(dest)
        except:
            pass
        shutil.copytree(source, dest)

        shutil.rmtree(tempdir)

    def get_user_project_dir(self):
        return self.get_paths_dict()["nysa_user_base"]

    def get_user_examples_dir(self):
        return os.path.join(self.get_user_project_dir(), USER_BASE_EXAMPLES_DIR)

    def get_user_verilog_dir(self):
        return os.path.join(self.get_user_project_dir(), USER_BASE_VERILOG_DIR)

    def get_user_app_dir(self):
        return os.path.join(self.get_user_project_dir(), USER_BASE_APP_DIR)

    def get_user_dev_dir(self):
        return os.path.join(self.get_user_project_dir(), USER_BASE_DEV_DIR)

    def get_user_cbuilder_project_dir(self):
        return os.path.join(self.get_user_project_dir(), USER_BASE_CBUILDER_DIR)

    def get_user_ibuilder_project_dir(self):
        return os.path.join(self.get_user_project_dir(), USER_BASE_IBUILDER_DIR)

    def get_cocotb_directory(self):
        return COCOTB_PATH

    def install_cocotb(self):
        if os.path.exists(COCOTB_PATH):
            shutil.rmtree(COCOTB_PATH)
        v = subprocess.call(["git", "clone", COCOTB_URL, COCOTB_PATH])


