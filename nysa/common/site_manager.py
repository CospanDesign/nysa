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
BOARD_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1dif3JBFwjEiNVn5hNxr2ZQ58ypy1LqTsKIlVk3pWVtE/export?format=csv"
REMOTE_PACKAGE_URL = "http://www.cospandesign.com/nysa/packages"
BOARD_PACKAGE_PATH = os.path.join(SITE_PATH, "boards")
DEFAULT_BOARD_BRANCH = "master"

def get_paths_path():
    return PATHS_PATH

def get_site_path():
    return SITE_PATH

def get_versions_path():
    return VERSION_PATH

def get_board_package_path():
    return BOARD_PACKAGE_PATH

class LocalDefinition(Exception):
    pass

class RemoteDefinition(Exception):
    pass

class SiteManagerError(Exception):
    pass

class SiteManager(object):

    def __init__(self, remote_url = REMOTE_PACKAGE_URL):

        if not os.path.exists(SITE_PATH):
            os.makedirs(os.path.join(SITE_PATH))

        if not os.path.exists(VERSION_PATH):
            #Doesn't exists, create a reference to it
            f = open(VERSION_PATH, "w")
            f.write("{}")
            f.close()

        self.initialize_paths_dictionary()
        self.remote_url = remote_url
        self.set_remote_url(remote_url)

    def initialize_paths_dictionary(self):
        if not os.path.exists(PATHS_PATH):
            #Doesn't exists, create a reference to it
            f = open(PATHS_PATH, "w")
            f.write("{}")
            f.close()

        path_dict = None
        try:
            f = open(PATHS_PATH, "r")
            path_dict = json.load(f)
            f.close()
        except ValueError as e:
            f = open(PATHS_PATH, "w")
            f.write("{}")
            f.close()
            f = open(PATHS_PATH, "r")
            path_dict = json.load(f)
            f.close()

        if "boards" not in path_dict:
            path_dict["boards"] = {}
        if "verilog" not in path_dict:
            path_dict["verilog"] = []

        f = open(PATHS_PATH, "w")
        f.write(json.dumps(path_dict))
        f.close()

    def set_remote_url(self, remote_url):
        self.remote_url = remote_url
        self.remote_version_path = "%s/%s" % (remote_url, "versions.json")

    def _create_site_dir(self):
        os.makedirs(os.path.join(SITE_PATH))

    def _site_dir_exists(self):
        return os.path.exists(SITE_PATH)

    def _remove_local_site_dir(self):
        shutil.rmtree(SITE_PATH)

    def get_remote_version_dict(self):
        self.remote_version = json.load(urllib2.urlopen(self.remote_version_path).read())
        return self.remote_version

    def get_local_version_dict(self):

        f = open(VERSION_PATH, "r")
        self.version = json.load(f)
        f.close()
        return self.version

    def get_paths_dict(self):

        f = open(PATHS_PATH)
        path_dict = json.load(f)
        f.close()
        return path_dict

    def board_exists(self, name):
        path_dict = self.get_paths_dict()
        for board_name in path_dict["boards"]:
            if board_name.lower() == name.lower():
                if os.path.exists(path_dict["boards"][board_name]["path"]):
                    return True
        return False

    def add_board(self, name, timestamp, path):
        path_dict = self.get_paths_dict()
        path_dict["boards"][name] = {}
        path_dict["boards"][name]["timestamp"] = timestamp
        path_dict["boards"][name]["path"] = path
        f = open(PATHS_PATH, "w")
        f.write(json.dumps(path_dict))
        f.close()

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
        tempdir = tempfile.mkdtemp()
        temparchive = os.path.join(tempdir, "archive.zip")
        f = open(temparchive, "w")
        f.write(data)
        f.close()

        zf = zipfile.ZipFile(temparchive, "r")
        zf.extractall(get_board_package_path())
        zf.close()
        shutil.rmtree(tempdir)
        dir_name = "%s-%s" % (url.rpartition("/")[2], branch)
        board_dir = os.path.join(get_board_package_path(), dir_name)

        self.add_board(name, timestamp, board_dir)

    def compare_version_entry(self, entry):
        remote_version = self.get_remote_version_dict()
        local_version = self.get_local_version_dict()
        if entry not in remote_version:
            raise RemoteDefinition("%s is not within the remote version" % entry)

        if entry not in local_version:
            raise LocalDefinition("%s is not within local version" % entry)

        if local_version[entry] != remote_version[entry]:
            return False

        return True

    def update_local_version(self, entry):
        remote_version = self.get_remote_version_dict()
        local_version = self.get_local_version_dict()
        local_version[entry] = remote_version[entry]
        f = open(VERSION_PATH, "w")
        f.write(json.dumps(local_version))
        f.close()

    def create_local_entry(self, entry, value):
        local_version = self.get_local_version_dict()
        local_version[entry] = value
        f = open(VERSION_PATH, "w")
        f.write(json.dumps(local_version))
        f.close()

