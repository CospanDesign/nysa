import wx
import nysa_main
import main_status
from main_status import StatusLevel

class MainMenuBarManager():

  parent = None
  output = None

  def __init__(self, parent, output):
    self.parent = parent
    #self.output = output
    self.output = main_status.Dummy()
    #self.output.SetLevel(StatusLevel.VERBOSE)
    self.menubar = wx.MenuBar()
    parent.SetMenuBar(self.menubar)

  def clear(self):
    '''
    clear the menubar

    Args:
      Nothing

    Return:
      Nothing

    Raises:
      Nothing
    '''
    self.menubar.SetMenus([])

  def remove_item(self, item_path):
    '''
    Removes the item given in the path, if this is the last item in a menu or submenu this
    will also remove the submenu or item

    Args:
      item_path: String format the path is in the form of <menu>.<menu>.item

    Returns:
      True if item is found/deleted
      False if item is not found

    Raises:
      Nothing
    '''
    rhs       = item_path
    menu_list = []
    curr_menu = None
    found     = False
    while '.' in rhs:
      item = rhs.partition('.')[0]
      rhs = rhs.partition('.')[2]

      #look to see if this item already exists in the menu, or path
      if curr_menu is None:
        found = True
        if self.menubar.FindMenu(item) == -1:
          return False
        else: 
          self.output.Debug(self, "Menu %s Item exists" % item)
          curr_menu = self.menubar.GetMenu(self.menubar.FindMenu(item))
          menu_list.insert(0, curr_menu)

      else:
        #By now we should have a reference to a menu, now I need to find a reference to a menu item
        found = False
        mil = curr_menu.GetMenuItems()
        for m in mil:
          if m.GetText() == item and m.IsSubMenu():
            self.output.Debug (self, str("Submenu %s exists" % item))
            curr_menu = m.GetSubMenu()
            found = True
            menu_list.insert(0, curr_menu)
            break

      if not found:
        return False


    found = False
    self.output.Debug(self, str("Final Item: %s" % rhs))
    mil = curr_menu.GetMenuItems()
    m = None
    for m in mil:
      if m.GetText() == rhs:
        found = True
        self.output.Debug (self, str("Found Finale Item: %s" % rhs))
        break

    if not found:
      return False

    curr_menu.RemoveItem(m)

    print "Menu List: %s" % str(menu_list)
    for menu in menu_list:
      self.output.Debug(self, str("menu title: %s" % menu.GetTitle()))
      if menu is None:
        continue

      if menu.GetMenuItemCount() == 0:
        #menu is empty
        self.output.Debug(self, str("Found an empty sub menu: %s" % menu.GetTitle()))
        #check to see if this is the last item
        if menu.GetParent() is None:
          self.output.Debug(self, "Parent is menubar")
          pos = self.menubar.FindMenu(menu.GetTitle())
          self.menubar.Remove(pos)

        #not the last item, remove it from the upper menu
        else:
          parent = menu.GetParent()
          self.output.Debug(self, str("Parent of %s type: %s" % (menu.GetTitle(), str(parent))))
          self.output.Debug(self, str("Parent is a menu called %s" % parent.GetTitle()))
          mis = parent.GetMenuItems()
          for mi in mis:
            if mi.GetText() == menu.GetTitle(): 
              parent.RemoveItem(mi)
              break

    return True


  def add_item (self, item_path, description = "", accellerator = None, handler = None, data=None):
    '''
    Adds an item using the 'path' that the user specifies with item_path

    Args:
      item_path: String format the path is in the form of <menu>.<menu>.item
      accellerator: Shortcut key combination that user presse to activate
      handler: function to callback when the user selects an item

    Return:
      ID of the menu item

    Raises:
      XXX: Someting... but what??
    '''

    #dissasemble the path
    #look for existing items within the path
    rhs       = item_path
    curr_menu = None
    found     = False

    while '.' in rhs:
      item = rhs.partition('.')[0]
      rhs = rhs.partition('.')[2]

      #look to see if this item already exists in the menu, or path
      if curr_menu is None:
        found = True
        if self.menubar.FindMenu(item) != -1:
          self.output.Debug(self, "Menu %s Item exists" % item)
          curr_menu = self.menubar.GetMenu(self.menubar.FindMenu(item))
        else:
          #top menu item doesn't exists, I need to create it
          self.output.Debug(self, str("Top Menu Doesn't exist create a new menu called: %s" % item))
          m = wx.Menu()
          m.SetTitle(item)
          self.menubar.Append(m, item)
          curr_menu = m

      else:
        #By now we should have a reference to a menu, now I need to find a reference to a menu item
        found = False
        mil = curr_menu.GetMenuItems()
        for m in mil:
          if m.GetText() == item and m.IsSubMenu():
            self.output.Debug (self, str("Submenu %s exists" % item))
            m.SetTitle(item)
            curr_menu = m.GetSubMenu()
            found = True
            break

      if not found:
        self.output.Debug(self, str("Need to make a new submenu called %s" % item))
        m = wx.Menu()
        m.SetTitle(item)
        curr_menu.AppendMenu(wx.ID_ANY, item, m)
        curr_menu = m

    self.output.Debug(self, str("Final Item: %s" % rhs))
    mi = wx.MenuItem(curr_menu, wx.ID_ANY, rhs, description)
    if accellerator is not None:
      mi.SetAccel(accellerator)

    curr_menu.AppendItem(mi)
    self.parent.Bind(wx.EVT_MENU, handler, mi)

    return mi.GetId()

