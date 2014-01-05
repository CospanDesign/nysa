from sap_gui_error import GUI_Error

class Icon:
  def __init__(self):
    self.x = 0.0
    self.y = 0.0
    self.width = 0.0
    self.height = 0.0
    self.r = 0.0
    self.g = 0.0
    self.b = 0.0
    self.connected = False
    self.slave_name = ""

class Box(QGraphicsItem):
 
  def __init__(self, parent = None, graphicView = None, graphicsScene=None):
    QGraphicsItem.__init__(self, parent)
    self.x = 0.0
    self.y = 0.0
    self.width = 0.0
    self.height = 0.0
    self.tag = ""
    self.r = 0.0
    self.g = 0.0
    self.b = 0.0
    self.name = ""
    self.arb_master_ratio = 0.1
    self.arb_master_pad = 2
    self.arb_master = {}
    self.arb_slave = False
    self.arb_slave_ratio = 0.2
    self.arb_slave_width = 0.0

  def set_location_and_size(self, x, y, width, height):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    # Check if there is any arbitrators to modify

    self.generate_icons()

  def generate_icons(self, debug = False):
    # Calculate the size of the slave portion.
    self.arb_slave_width = self.width * self.arb_slave_ratio

    # Get the total number of arbitrators.
    arb_total = len(self.arb_master.keys())

    # Modify any arbitrators.
    for key in self.arb_master.keys():
      if debug:
        print "setting arbitrator size/location"
      arb = self.arb_master[key]
      # Get the position of this arbitrator in the list.
      arb_pos = self.arb_master.keys().index(key)
      # Calculate the width.
      arb.width = self.width * self.arb_master_ratio
      # Calculate the height.
      arb.height = self.height / arb_total

      # Calculate the position
      arb.x = self.x + self.width - arb.width
      arb.y = self.y + (arb_pos * arb.height)

    if debug:
      print "arb master: " + str(self.arb_master[name])
      print "\tConnected: " + str(self.arb_master[name].connected)
      print "\tSlave: " + str(self.arb_master[name].slave)

  def connect_arbitrator_master(self, name, slave_name):
    if name not in self.arb_master.keys():
      raise GUI_Error("arbitrator is not in box")

    self.arb_master[name].connected = True
    self.arb_master[name].slave = slave_name
    self.generate_icons()

  def get_connected_slave(self, name):
    if name not in self.arb_master.keys():
      raise GUI_Error("arbitrator is not in box")
    return self.arb_master[name].slave

  def disconnect_arbitrator_master(self, name):
    if name not in self.arb_master.keys():
      raise GUI_Error("arbitrator is not in box")

    self.arb_master[name].connected = False
    self.arb_master[name].slave = ""
    self.generate_icons()

  def add_arbitrator_master(self, name, is_connected, slave_name, debug = False):
    self.arb_master[name] = Icon()
    self.arb_master[name].connected = is_connected
    self.arb_master[name].slave = slave_name
    self.generate_icons()

  def in_bounding_box(self, x, y):
    return self.x <= x and x <= self.x + self.width and \
           self.y <= y and y <= self.y + self.height

  def in_arb_master_icon(self, x, y):
    """Check if the user selected the arbitrator master or one of the
    arbitrator masters."""
    for key in self.arb_master.keys():
      arb = self.arb_master[key]
#      print "working on : " + key
      if arb.x <= x and x <= (arb.x + arb.width) and \
         arb.y <= y and y <= (arb.y + arb.height):
#        print "X: %f <= %f <= %f" % (arb.x, x, (arb.x + arb.width))
#        print "Y: %f <= %f <= %f" % (arb.y, y, (arb.y + arb.height))
        return True
    return False

  def get_arb_master_names(self):
    return self.arb_master.keys()

  def get_arb_master_name(self, x, y):
    """User selected one of the arbitrator master, return the name associated
    with the location."""
    for key in self.arb_master.keys():
      arb = self.arb_master[key]
      if arb.x <= x and x <= (arb.x + arb.width) and \
         arb.y <= y and y <= (arb.y + arb.height):
        return key
    return None

  def is_arb_master_connected(self, name):
    if name not in self.arb_master.keys():
      return None
    return self.arb_master[name].connected

  def get_name_of_connected_slave(self, name):
    if name not in self.arb_master.keys():
      return None
    return self.arb_master[name].slave

  def set_arb_slave_connected(self, connected):
    self.arb_slave = connected

  def set_name(self, name):
    self.name = name

  def set_color(self, r, g, b):
    self.r = r
    self.g = g
    self.b = b
    return False


