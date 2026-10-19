import math

from ..utils.backend import call

OPERATIONS = {'doctor', 'status', 'inspect', 'launch', 'home', 'app-switcher',
              'search', 'type', 'key', 'click', 'scroll'}
KEYS = ('return', 'escape', 'tab', 'backspace', 'up', 'down', 'left', 'right')


def request(operation, dry_run=False, **arguments):
    if operation not in OPERATIONS:
        raise ValueError('Unknown operation')
    if operation in {'type', 'search'}:
        text = arguments.get('text', '')
        if not text or len(text) > 1000 or '\x00' in text:
            raise ValueError('Text must contain 1–1000 characters, without NUL.')
    if operation == 'click':
        for key in ('x', 'y'):
            value = arguments.get(key)
            if value is None or not math.isfinite(value) or value < 0:
                raise ValueError('Coordinates must be finite nonnegative window-relative points.')
    if operation == 'scroll' and not 1 <= arguments.get('pixels', 0) <= 10000:
        raise ValueError('Scroll pixels must be between 1 and 10000.')
    if operation == 'key' and arguments.get('name') not in KEYS:
        raise ValueError('Unsupported key')
    return call({'operation': operation, 'dry_run': dry_run, **arguments})
