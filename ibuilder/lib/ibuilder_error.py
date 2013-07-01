class SlaveError(Exception):
    """SlaveError

    Errors associated with slaves in particular:
        setting incorrect parameters.
        setting incorrect bindings
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ModuleNotFound(Exception):
   """ModuleNotFound

   Errors associated with searching for a module file location
   usually occurs when the module is not found in the local directory
   or in the rtl files in ibuilder
   """
   def __init__(self, value):
        self.value = value
   def __str__(self):
        return repr(self.value)

class ModuleFactoryError(Exception):
    """ModuleFactoryError

    Errors associated with creating and generating modules
        Modules may not be found
        Modules generation script may not be found
        Unable to execute a gen script
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PreProcessorError(Exception):
    """PreProcessorError

    Errors associated with preprocessing a file
    Errors include:
        Defines that could not be evaluated
        Referenced modules not located
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ArbitorError(Exception):
    """ArbitorError

    Errors associated with generatign arbitors
          User didn't specify the number of masters required
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class NysaEnvironmentError(Exception):
    """NysaEnvironmentError

    Raised when a user attempts to retrieve Nysa environmental
    variables before running 'init_settings.py' in the Nysa base
    directory
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class XilinxToolchainError(Exception):
    """XilinxToolchainError

    Raised when:
        User attempts to access Xilnix toolchain when one doesn't exists
        Unable to locate a directoryj

    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class IBuilderError(Exception):
    """IBuilder Error

    Raised when:
        General errors associated with the ibuilder library
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ConstraintError(Exception):
    """Constraint Errors

    Raised when:
        Errors associated with constraints is detected such as:
            -unable to find clock rate
            -unable to find net names
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
