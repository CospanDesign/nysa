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
   def __str__(self):
        value = "\n"
        value += "File: %s not found\n" % self.args[0]
        value += "Searched user paths:\n"
        for u in self.args[1]:
            value += "\t%s\n" % u
        value += "Searched default paths:\n"
        for d in self.args[2]:
            value += "\t%s\n" % u
        return value

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

class ArbiterError(Exception):
    """ArbiterError

    Errors associated with generatign arbiters
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

class ProjectGeneratorError(Exception):
    """Project Generator Error

    Raised when:
        Errors loading project tags
        Errors loading template tags
        Errors created output project structure
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


