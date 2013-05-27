import abc


class Gen:
  """class specifically for overriding and generating a file"""
  def __init__(self):
    self.tags = {}

  def gen_script (self, tags = {}, buf = ""):
    """This function is made for overriding, tags = input tags that modify the
    file, buf is the file buffer itself, its easier to modify a buffer than a
    file"""
    pass

  def get_name (self):
    print "gen"

