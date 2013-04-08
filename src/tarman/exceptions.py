

class TarmanError(Exception):
    pass


class FileError(TarmanError, IOError):
    pass


class NotFound(FileError):
    pass
