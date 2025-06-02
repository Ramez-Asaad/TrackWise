"""
Patch for experta to use our custom frozendict implementation
"""
import sys
import os
from importlib import util

def patch_experta():
    """
    Patch experta to use our custom frozendict implementation
    """
    # Add our directory to the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Import our custom frozendict
    from custom_frozendict import frozendict, freeze, unfreeze

    # Find experta's utils module
    experta_spec = util.find_spec('experta.utils')
    if experta_spec is None:
        raise ImportError("Could not find experta.utils module")

    # Get the module
    experta_utils = experta_spec.loader.load_module()

    # Replace the frozendict, freeze, and unfreeze functions
    experta_utils.frozendict = frozendict
    experta_utils.freeze = freeze
    experta_utils.unfreeze = unfreeze

    # Also patch the fact module since it might import directly from frozendict
    fact_spec = util.find_spec('experta.fact')
    if fact_spec is not None:
        fact_module = fact_spec.loader.load_module()
        if hasattr(fact_module, 'frozendict'):
            fact_module.frozendict = frozendict 