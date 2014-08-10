import os
import urllib2
import json
import site
import shutil

class LocalDefinition(Exception):
    pass

class RemoteDefinition(Exception):
    pass

class SiteManager(object):

    def __init__(self, site_name, remote_url = "http://www.cospandesign.com/nysa/packages"):
        self.site_name = site_name
        self.site_path = os.path.join(site.getuserbase(), self.site_name)
        self.local_version_path = os.path.join(self.site_path, "versions.json")
        self.remote_url = remote_url
        self.set_remote_url(remote_url)

    def set_remote_url(self, remote_url):
        self.remote_url = remote_url
        self.remote_version_path = "%s/%s" % (remote_url, "versions.json")

    def _create_site_dir(self):
        os.makedirs(os.path.join(self.site_path))

    def _site_dir_exists(self):
        return os.path.exists(self.site_path)

    def _remove_local_site_dir(self):
        shutil.rmtree(self.site_path)

    def get_remote_version(self):
        return urllib2.urlopen(self.remote_version_path).read()

    def get_local_version(self):
        if not os.path.exists(self.local_version_path):
            #Doesn't exists, create a reference to it
            f = open(self.local_version_path, "w")
            f.write("{}")
            f.close()
                
        f = open(self.local_version_path, "r")
        version = f.read()
        f.close()
        return version

    def compare_version_entry(self, entry):
        remote_version = json.loads(self.get_remote_version())
        local_version = json.loads(self.get_local_version())
        if entry not in remote_version:
            raise RemoteDefinition("%s is not within the remote version" % entry)

        if entry not in local_version:
            raise LocalDefinition("%s is not within local version" % entry)

        if local_version[entry] != remote_version[entry]:
            return False

        return True

    def update_local_version(self, entry):
        remote_version = json.loads(self.get_remote_version())
        local_version = json.loads(self.get_local_version())
        local_version[entry] = remote_version[entry]
        f = open(self.local_version_path, "w")
        f.write(json.dumps(local_version))
        f.close()


    def create_local_entry(self, entry, value):
        local_version = json.loads(self.get_local_version())
        local_version[entry] = value
        f = open(self.local_version_path, "w")
        f.write(json.dumps(local_version))
        f.close()


