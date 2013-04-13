

class TarmanError(Exception):
    pass


class AlreadyExists(TarmanError):
    def __init__(self, message, child):
        super(AlreadyExists, self).__init__(message)
        self.child = child


class FileError(TarmanError, IOError):
    pass


class NotFound(FileError):
    pass


class OutOfRange(FileError):
    pass
