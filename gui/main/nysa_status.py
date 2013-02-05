import wx

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

StatusLevel = enum ('FATAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'VERBOSE')


class NysaStatus(wx.TextCtrl) :
#class NysaStatus() :
  _instance=None
  '''Singleton Status interface'''
  def __init__(self, parent, message):

    self.output = wx.TextCtrl.__init__( self,
                                        parent,
                                        -1,
                                        "%s\n" % message,
                                        wx.DefaultPosition,
                                        wx.Size(200, 150),
                                        wx.NO_BORDER | wx.TE_MULTILINE)
    self.level = StatusLevel.VERBOSE


  def Verbose (self, c, text):
    if self.CheckLevel(StatusLevel.VERBOSE):
      self.AppendText ("(Verbose) %s: %s\n" % (c.__class__.__name__, text))

  def Debug (self, c, text):
    if self.CheckLevel(StatusLevel.DEBUG):
      self.AppendText ("(Debug) %s: %s\n" % (c.__class__.__name__, text))

  def Info (self, c, text):
    if self.CheckLevel(StatusLevel.INFO):
      self.AppendText ("(Info) %s: %\n" % (c.__class__.__name__, text))

  def Warning (self, c, text):
    if self.CheckLevel(StatusLevel.WARNING):
      self.AppendText ("(Warning) %s: %s\n" % (c.__class__.__name__, text))

  def Error (self, c, text):
    if self.CheckLevel(StatusLevel.ERROR):
      self.AppendText ("(Error) %s: %s\n" % (c.__class__.__name__, text))

  def Fatal (self, c, text):
    if self.CheckLevel(StatusLevel.FATAL):
      self.AppendText ("(Fatal) %s: %s\n" % (c.__class__.__name__, text))

  def Print (self, text):
    self.AppendText (text)

  def PrintLine(self, text):
    self.AppendText ("%s\n" % text)

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

    return False
 
