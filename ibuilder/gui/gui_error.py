class GraphControllerError(Exception):
  """GraphControllerError

  Errors associated with the graph controller:
    unknown setting.
    setting incorrect.
  """
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class NodeError(Exception):
  """GraphControllerError

  Errors associated with the graph controller:
    unknown setting.
    setting incorrect.
  """
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)
