from importlib import import_module
from astrodata import factory
from .astrofaker import AstroFaker
from gemini_instruments.gemini import addInstrumentFilterWavelengths

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
