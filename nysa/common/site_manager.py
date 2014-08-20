import os
import urllib2
import json
import site
import shutil
import csv
import zipfile
import tempfile
from cookielib import CookieJar
from urllib2 import build_opener, HTTPCookieProcessor



SITE_PATH = os.path.join(site.getuserbase(), "nysa")
VERSION_PATH = os.path.join(SITE_PATH, "versions.json")
PATHS_PATH = os.path.join(SITE_PATH, "paths.json")
BOARD_ID_PATH = os.path.join(SITE_PATH, "board_id.json")
BOARD_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1dif3JBFwjEiNVn5hNxr2ZQ58ypy1LqTsKIlVk3pWVtE/export?format=csv"
#REMOTE_PACKAGE_URL = "http://www.cospandesign.com/nysa/packages"
VERILOG_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1fyr9G2sVVa1bOi3Rtg9uGz0KELReo8buoTrP8DQfNTA/export?format=csv"
BOARD_PACKAGE_PATH = os.path.join(SITE_PATH, "boards")
VERILOG_PACKAGE_PATH = os.path.join(SITE_PATH, "verilog")
DEFAULT_BOARD_BRANCH = "master"

NYSA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

paths_dict = None

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

    def __init__(self):

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

        paths_dict["nysa"] = NYSA_BASE

        f = open(get_paths_path(), "w")
        f.write(json.dumps(paths_dict))
        f.close()

    def _create_site_dir(self):
        os.makedirs(os.path.join(SITE_PATH))

    def _site_dir_exists(self):
        return os.path.exists(SITE_PATH)

    def _remove_local_site_dir(self):
        shutil.rmtree(SITE_PATH)

    def get_paths_dict(self, force = False):
        global paths_dict
        #print "pre path dict: %s" % str(paths_dict)
        if paths_dict is not None or force:
            #print "\tGetting cached version"
            return paths_dict
        #print "\tGetting non-cached version"
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
        f.write(json.dumps(paths_dict))
        f.close()
        self.get_paths_dict(force = True)

    def add_verilog_package(self, name, timestamp, path):
        paths_dict = self.get_paths_dict()
        paths_dict["verilog"][name] = {}
        paths_dict["verilog"][name]["timestamp"] = timestamp
        paths_dict["verilog"][name]["path"] = path
        f = open(get_paths_path(), "w")
        f.write(json.dumps(paths_dict))
        f.close()
        self.get_paths_dict(force = True)

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

    def install_remote_board_package(self, name, branch = DEFAULT_BOARD_BRANCH):
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
        self.update_board_id_dict(grid_data)
        result = None
        for row in grid_data:
            #print "row: %s" % str(row)
            if row[0].strip() == "Timestamp":
                continue
            if row[1].lower() == name.lower():
                result = row
                break

        if result is None:
            raise SiteManagerError("Did not find remote board: %s" % name)

        url = result[2]
        timestamp = result[0]
        archive_url = None
        if url.endswith('zip'):
            print "Found zip file URL"
            raise SiteManagerError("Current version of stie manager can only fetch Github URLs")
        elif "github" not in url:
            raise SiteManagerError("Current version of site manager can only fetch Github URLs")

        if "github" in url:
            archive_url = url + "/archive/%s.zip" % branch

        if not os.path.exists(get_board_package_path()):
            os.makedirs(os.path.join(get_board_package_path()))

        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        resp = opener.open(archive_url)
        data = resp.read()

        #board_path = os.path.join(get_board_package_path(), name.lower())
        #board_path = os.path.join(get_board_package_path(), name.lower())

        if not os.path.exists(get_board_package_path()):
            os.makedirs(get_board_package_path())

        #tempdir = tempfile.mkdtemp()
        tempdir = get_board_package_path()
        temparchive = os.path.join(tempdir, "archive.zip")
        f = open(temparchive, "w")
        f.write(data)
        f.close()

        zf = zipfile.ZipFile(temparchive, "a")
        zf.extractall(get_board_package_path())
        zf.close()
        #shutil.rmtree(tempdir)
        dir_name = "%s-%s" % (url.rpartition("/")[2], branch)
        board_dir = os.path.join(get_board_package_path(), dir_name)

        self.add_board(name, timestamp, board_dir)
        self.get_paths_dict(force = True)

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
        f.write(json.dumps(board_id_dict))
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
            f.write(json.dumps(paths_dict))
            f.close()
            self.get_paths_dict(force = True)

    def update_verilog_package(self, name = None, branch = None):
        if name is None:
            name = "nysa-verilog"
        if branch is None:
            branch = DEFAULT_BOARD_BRANCH

        name = name.lower()

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

        url = result[2]
        timestamp = result[0]
        archive_url = None
        if url.endswith('zip'):
            print "Found zip file URL"
            raise SiteManagerError("Current version of stie manager can only fetch Github URLs")
        elif "github" not in url:
            raise SiteManagerError("Current version of site manager can only fetch Github URLs")

        if "github" in url:
            archive_url = url + "/archive/%s.zip" % branch


        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        resp = opener.open(archive_url)
        data = resp.read()

        if not os.path.exists(get_verilog_package_path()):
            os.makedirs(get_verilog_package_path())
        #tempdir = tempfile.mkdtemp()
        tempdir = get_verilog_package_path()
        temparchive = os.path.join(tempdir, "archive.zip")
        f = open(temparchive, "w")
        f.write(data)
        f.close()

        zf = zipfile.ZipFile(temparchive, "a")
        zf.extractall(get_verilog_package_path())
        zf.close()
        #shutil.rmtree(tempdir)
        dir_name = "%s-%s" % (url.rpartition("/")[2], branch)

        verilog_dir = os.path.join(get_verilog_package_path(), dir_name)
        self.add_verilog_package(name, timestamp, verilog_dir)
        self.get_paths_dict(force = True)


