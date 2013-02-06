import wx
import main_status

class MainToolBarManager ():
  def __init__ (self, toolbar, parent):
    self.parent = parent
    TBFLAGS = ( wx.TB_HORIZONTAL |
                wx.NO_BORDER     |
                wx.TB_FLAT )
    self.tb = toolbar
    self.tb.SetWindowStyle(TBFLAGS)
    self.output = parent.get_output()
    self.tb.SetName("main_toolbar")


  def on_go_home(self, event):
    '''Callback to handle default functions'''
    self.output.Verbose(self, "Home Pressed!")


  def set_default_tools(self):
    '''
    resets the toolbar with the default tools

    Args:
      Nothing

    Return:
      Nothing

    Raises:
      Nothing
    '''
    self.output.Verbose(self, "Setting default tools")
    self.tb.ClearTools()
    self.tb.Bind( wx.EVT_TOOL,
                  self.on_go_home,
                  self.tb.AddLabelTool(wx.ID_ANY, 'Home', wx.ArtProvider.GetBitmap(wx.ART_GO_HOME)))
    self.tb.Realize()

  def clear_toolbar(self):
    '''
    Clears the toolbar of any previous tools on it

    Args:
      Nothing

    Return:
      Nothing

    Raises:
      Nothing
    '''
    self.tb.ClearTools()

  def add_tool(self, name, image, tooltip_short=None, tooltip_long=None, handler=None, user_data=None):
    '''
    Add a tool to the current toolbar

    Args:
      name: name of the tool (used to identify the tool when the event is pressed)
      image: image (Bitmap) example: wx.ArtProvider.GetBitmap(wx.ART_GO_HOME)
      tooltip: test to display when the user hovers over the button
      handler: function to call when the user presses the button
      user_data: data to return when an event is called
        function (event)

    Return:
      Nothing

    Raises:
      XXX: Raises something when handler is None  (or at least it should)
    '''
    self.tb.Bind(wx.EVT_TOOL,
                handler,
                self.tb.AddLabelTool( id=wx.ID_ANY,
                                      label=name,
                                      bitmap=image,
                                      longHelp=tooltip,
                                      clientData=user_data), )

    self.tb.Realize()

