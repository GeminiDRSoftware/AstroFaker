#!/usr/bin/env python
"""
Manages package version.
"""

API = 0
FEATURE = 2
BUG = 0


def version(short=False):
    """
    Returns the parsed version.

    Parameters
    ----------
    short : Bool (default=False)
        Returns only the major version (API.FEATURE).

    Returns
    -------
        str : current package version using '{:d}.{:d}.{:d}' format.
    """
    if short:
        s = "{:d}.{:d}".format(API, FEATURE)
    else:
        s = "{:d}.{:d}.{:d}".format(API, FEATURE, BUG)

    return s
