import wx
import wx.lib.mixins.listctrl as listmix

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

StatusLevel = enum ('FATAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'VERBOSE')


class MainStatus(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
#class MainStatus() :
  _instance=None
  index = 0
  '''Singleton Status interface'''
  def __init__(self, parent, message):
    wx.ListCtrl.__init__(   self,
                            parent,
                            wx.ID_ANY,
                            wx.DefaultPosition,
                            wx.Size(-1, 150),
                            wx.LC_REPORT | wx.EXPAND)

    self.index = 0

    self.InsertColumn(0, "Index", width = 40)
    self.InsertColumn(1, "Level", width = 80)
    self.InsertColumn(2, "Class", width = 150)
    self.InsertColumn(3, "Message", width = -1)

    listmix.ListCtrlAutoWidthMixin.__init__(self)

    self.level = StatusLevel.VERBOSE
    self.SetName("main_status")

  def Verbose (self, c, text):
    if self.CheckLevel(StatusLevel.VERBOSE):
      self.status_output("Verbose", c, text, fg = "White", bg="Blue")

  def Debug (self, c, text):
    if self.CheckLevel(StatusLevel.DEBUG):
      self.status_output("Debug", c, text, fg = "White", bg="Black")

  def Info (self, c, text):
    if self.CheckLevel(StatusLevel.INFO):
      self.status_output("Info", c, text, fg="Green", bg="Black")

  def Warning (self, c, text):
    if self.CheckLevel(StatusLevel.WARNING):
      self.status_output("Warning", c, text, fg="Yellow", bg="Black")

  def Error (self, c, text):
    if self.CheckLevel(StatusLevel.ERROR):
      self.status_output("Error", c, text, fg="Red")

  def Fatal (self, c, text):
    if self.CheckLevel(StatusLevel.FATAL):
      self.status_output("Fatal", c, text, fg="Red", bg="Black")

  def Print (self, text):
    self.status_output("Extra", self, text)

  def PrintLine(self, text):
    self.status_output("Extra", self, text)

  def status_output(self, level, c, text, fg = None, bg = None):
    item = self.InsertStringItem(self.index, "%d" % self.index)
    self.SetStringItem(self.index, 1, level)
    self.EnsureVisible(self.GetItemCount() - 1)

    if fg is not None:
      self.SetItemTextColour(item, fg)
    if bg is not None:
      self.SetItemBackgroundColour(item, bg)

    self.SetStringItem(self.index, 2, c.__class__.__name__)
    self.SetStringItem(self.index, 3, text)

    self.index += 1

  def SetLevel(self, level):
    self.level = level

  def GetLevel(self):
    return self.level

  def CheckLevel(self, requestLevel):
    if requestLevel is StatusLevel.FATAL:
      return True
    elif requestLevel is StatusLevel.VERBOSE:
      if  self.level is StatusLevel.VERBOSE:
        return True
    elif requestLevel is StatusLevel.DEBUG:
      if  self.level is StatusLevel.VERBOSE or \
          self.level is StatusLevel.DEBUG:
        return True
    elif requestLevel is StatusLevel.INFO:
      if self.level is StatusLevel.VERBOSE or  \
          self.level is StatusLevel.DEBUG or   \
          self.level is StatusLevel.INFO:
        return True
    elif requestLevel is StatusLevel.WARNING:
      if self.level == StatusLevel.VERBOSE or  \
          self.level == StatusLevel.DEBUG or   \
          self.level == StatusLevel.INFO  or   \
          self.level == StatusLevel.WARNING:
        return True
    elif requestLevel is StatusLevel.ERROR:
      if self.level == StatusLevel.VERBOSE or  \
          self.level == StatusLevel.DEBUG or   \
          self.level == StatusLevel.INFO  or   \
          self.level == StatusLevel.WARNING or \
          self.level == StatusLevel.ERROR:
        return True

    return False

class Dummy ():
  level = StatusLevel.FATAL
  def __init__(self, level=StatusLevel.FATAL):
    self.level = level

  def CheckLevel(self, requestLevel):
    if requestLevel is StatusLevel.FATAL:
      return True
    elif requestLevel is StatusLevel.VERBOSE:
      if  self.level is StatusLevel.VERBOSE:
        return True
    elif requestLevel is StatusLevel.DEBUG:
      if  self.level is StatusLevel.VERBOSE or  \
          self.level is StatusLevel.DEBUG:
        return True
    elif requestLevel is StatusLevel.INFO:
      if self.level is StatusLevel.VERBOSE or  \
          self.level is StatusLevel.DEBUG or    \
          self.level is StatusLevel.INFO:
        return True
    elif requestLevel is StatusLevel.WARNING:
      if self.level == StatusLevel.VERBOSE or  \
          self.level == StatusLevel.DEBUG or    \
          self.level == StatusLevel.INFO  or    \
          self.level == StatusLevel.WARNING:
        return True
    elif requestLevel is StatusLevel.ERROR:
      if self.level == StatusLevel.VERBOSE or  \
          self.level == StatusLevel.DEBUG or    \
          self.level == StatusLevel.INFO  or    \
          self.level == StatusLevel.WARNING or  \
          self.level == StatusLevel.ERROR:
        return True

  def SetLevel(self, level):
    self.level = level

  def GetLevel(self):
    return self.level

  def Verbose (self, c, text):
    if self.CheckLevel(StatusLevel.VERBOSE):
      print "(Verbose) %s: %s" % (c.__class__.__name__, text)

  def Debug (self, c, text):
    if self.CheckLevel(StatusLevel.DEBUG):
      print "(Debug) %s: %s" % (c.__class__.__name__, text)

  def Info (self, c, text):
    if self.CheckLevel(StatusLevel.INFO):
      print "(Info) %s: %s" % (c.__class__.__name__, text)

  def Warning (self, c, text):
    if self.CheckLevel(StatusLevel.WARNING):
      print "(Warning) %s: %s" % (c.__class__.__name__, text)

  def Error (self, c, text):
    if self.CheckLevel(StatusLevel.ERROR):
      print "(Error) %s: %s" % (c.__class__.__name__, text)

  def Fatal (self, c, text):
    if self.CheckLevel(StatusLevel.FATAL):
      print "(Fatal) %s: %s" % (c.__class__.__name__, text)

