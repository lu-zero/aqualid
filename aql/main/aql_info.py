__all__ = (
    'get_aql_info',
    'dump_aql_info',
)

# ==============================================================================


class AqlInfo (object):
    __slots__ = (
        'name',
        'module',
        'description',
        'version',
        'date',
        'url',
        'license',
    )

    # -----------------------------------------------------------

    def __init__(self):
        self.name = "Aqualid"
        self.module = "aqualid"
        self.description = "General purpose build system."
        self.version = "0.6.1"
        self.date = None
        self.url = 'https://github.com/aqualid'
        self.license = "MIT License"

    # -----------------------------------------------------------

    def dump(self):
        result = "{name} {version}".format(
            name=self.name, version=self.version)
        if self.date:
            result += ' ({date})'.format(date=self.date)

        result += "\n"
        result += self.description
        result += "\nSite: %s" % self.url

        return result

# -----------------------------------------------------------

_AQL_VERSION_INFO = AqlInfo()

# ==============================================================================


def get_aql_info():
    return _AQL_VERSION_INFO

# ==============================================================================


def dump_aql_info():
    return _AQL_VERSION_INFO.dump()
