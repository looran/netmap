class System_commands(object):
    @classmethod
    def generic(cls, fpath):
        return fpath.read_text()

    @classmethod
    def generic_strip(cls, fpath):
        return fpath.read_text().strip()
