"""
Setup module to handle all initialization before other imports
"""
import sys
import os
from collections.abc import Mapping

# Add the current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Create our frozendict implementation
class frozendict(Mapping):
    """An immutable wrapper around dictionaries"""
    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(frozenset(self._dict.items()))
        return self._hash

    def __eq__(self, other):
        if isinstance(other, frozendict):
            return self._dict == other._dict
        return self._dict == other

    def __repr__(self):
        return f'frozendict({self._dict!r})'

def freeze(obj):
    """Convert a mutable object to an immutable one"""
    if isinstance(obj, dict):
        return frozendict((k, freeze(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set)):
        return tuple(freeze(x) for x in obj)
    return obj

def unfreeze(obj):
    """Convert an immutable object back to a mutable one"""
    if isinstance(obj, frozendict):
        return dict((k, unfreeze(v)) for k, v in obj.items())
    elif isinstance(obj, tuple):
        return list(unfreeze(x) for x in obj)
    return obj

# Create a fake frozendict module
class FrozenDictModule:
    def __init__(self):
        self.frozendict = frozendict
        
# Install our fake frozendict module
sys.modules['frozendict'] = FrozenDictModule() 