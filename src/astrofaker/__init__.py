# -*- coding: utf-8 -*-

from importlib import import_module
from pkg_resources import get_distribution, DistributionNotFound

from astrodata import factory
from .astrofaker import AstroFaker
from gemini_instruments.gemini import addInstrumentFilterWavelengths

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

# Put in one place (i.e., here) all the stuff that the individual modules
# in gemini_instruments do. It makes things a bit cleaner.

def add_instrument(instrument):
    lookup = import_module('.{}.lookup'.format(instrument.lower()),
                           'gemini_instruments')
    addInstrumentFilterWavelengths(instrument.upper(), lookup.filter_wavelengths)
    module = import_module('.{}'.format(instrument), __name__)
    cls = getattr(module, 'AstroFaker{}'.format(instrument.capitalize()))
    factory.addClass(cls)

add_instrument('f2')
add_instrument('gmos')
add_instrument('gnirs')
add_instrument('gsaoi')
add_instrument('niri')

create = AstroFaker.create
open = AstroFaker.open
