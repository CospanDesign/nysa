# -*- coding: utf-8 *-*

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QRectF
#from PyQt4.QtGui import QGraphicsItem
#from PyQt4.QtGui import QRadialGradient
#from PyQt4.QtGui import QGraphicsTextItem
#from PyQt4.QtGui import QStyle
#from PyQt4.QtGui import QColor
#from PyQt4.QtGui import QPen
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGraphicsView
from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtGui import QVBoxLayout

from ninja_ide.gui.main_panel import itab_item
#from ninja_ide.tools import introspection
#from ninja_ide.core import file_manager

#from graph_utils import Box




class FPGADesigner(QWidget, itab_item.ITabItem):
  output = None

  def __init__(self, actions, parent=None):
    QWidget.__init__(self, parent)
    itab_item.ITabItem.__init__(self)
    self.actions = actions
    self.graphicView = QGraphicsView(self)
    self.scene = QGraphicsScene()
    self.graphicView.setScene(self.scene)
    self.graphicView.setViewportUpdateMode(
      QGraphicsView.BoundingRectViewportUpdate)

    vLayout = QVBoxLayout(self)
    self.setLayout(vLayout)
    vLayout.addWidget(self.graphicView)
    self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
    self.scene.setSceneRect(-200, -200, 400, 400)
    self.graphicView.setMinimumSize(400, 400)
    #actualProject = self.actions.ide.explorer.get_actual_project()

    #XXX: Here is where I get my modules

    #arrClasses = self.actions._locator.get_classes_from_project(
    #  actualProject)

    #FIXME:dirty need to fix
    self.mX = -400
    self.mY = -320
    self.hightestY = self.mY
    '''
    filesList = []
    for elem in arrClasses:
      #loking for paths
      filesList.append(elem[2])
    for path in set(filesList):
      self.create_class(path)
    '''


  def create_box(self, core_dict = {}):
    mYPadding = 10
    mXPadding = 10

  def set_output(self, output):
    self.output = output

  def scale_view(self, scaleFactor):
    factor = self.graphicView.transform().scale(
      scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()

    if factor > 0.05 and factor < 15:
      self.graphicView.scale(scaleFactor, scaleFactor)


  def keyPressEvent(self, event):
    taskList = {
      Qt.Key_Plus: lambda: self.scaleView(1.2),
      Qt.Key_Minus: lambda: self.scaleView(1 / 1.2)}
    if(event.key() in taskList):
      taskList[event.key()]()
    else:
      QWidget.keyPressEvent(self, event)


