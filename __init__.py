from importlib import import_module
from astrodata import factory
from .astrofaker import AstroFaker
from gemini_instruments.gemini import addInstrumentFilterWavelengths

# Put in one place (i.e., here) all the stuff that the individual modules
# in gemini_instruments do. It makes things a bit cleaner.

from .f2 import AstroFakerF2
from .gmos import AstroFakerGmos
from .gnirs import AstroFakerGnirs
from .gsaoi import AstroFakerGsaoi
from .niri import AstroFakerNiri

def add_instrument(instrument):
    lookup = import_module('.{}.lookup'.format(instrument.lower()), 'gemini_instruments')
    addInstrumentFilterWavelengths(instrument.upper(), lookup.filter_wavelengths)

add_instrument('f2')
add_instrument('gmos')
add_instrument('gnirs')
add_instrument('gsaoi')
add_instrument('niri')

factory.addClass(AstroFakerF2)
factory.addClass(AstroFakerGmos)
factory.addClass(AstroFakerGnirs)
factory.addClass(AstroFakerGsaoi)
factory.addClass(AstroFakerNiri)

create = AstroFaker.create