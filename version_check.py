import semver

class ModuleMinimumVersionNotMetError(ImportError):
    """Raised when a minumum version requirement from an import is not met"""
    def __init__(self, exp_ver, found_ver, **kwargs):
        super().__init__(**kwargs)
        self.exp_ver = exp_ver
        self.found_ver = found_ver
        
    def __str__(self):
        return f"Version of {self.name} found is {self.found_ver} "\
               f"but minimum required version is {self.exp_ver}"
           
def check_version(module, exp_ver):
    if semver.VersionInfo.parse(module.__version__) < semver.VersionInfo.parse(exp_ver):
        raise ModuleMinimumVersionNotMetError(
            exp_ver=exp_ver,
            found_ver=module.__version__,
            name=module.__name__, 
            path=module.__path__,
        )
