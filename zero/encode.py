from flask.json import JSONEncoder
from datetime import date, datetime


class ISO8601JSONEncoder(JSONEncoder):
    """Renders date and datetime objects as ISO8601 datetime strings."""

    def default(self, obj):
        """Overriden to render date(time)s in isoformat."""
        try:
            if type(obj) in [date, datetime]:
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
