class FPGADesignerError(Exception):
    """
    Errors associated with the FPGA designer

    Error associated with:
        -loading the configuration file
        -generating configuration files
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


