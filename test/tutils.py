import os


def save_file(filename, content):
    fpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "fake", filename))
    f = open(fpath, "w")
    f.write(content)
    f.close()
