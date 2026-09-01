from importlib import import_module
from importlib.metadata import version, PackageNotFoundError

from astrodata import factory
# astrodata_gemini refactor.
try:
    from astrodata_gemini.gemini import addInstrumentFilterWavelengths
except ModuleNotFoundError:
    from gemini_instruments.gemini import addInstrumentFilterWavelengths

from .astrofaker import AstroFaker
from .niri import AstroFakerNiri


# Put in one place (i.e., here) all the stuff that the individual modules
# in gemini_instruments do. It makes things a bit cleaner.
def add_instrument(instrument):

    # astrodata_gemini refactor.
    try:
        lookup = import_module(
            '.{}.lookup'.format(instrument.lower()), 'astrodata_gemini')
    except ModuleNotFoundError:
        lookup = import_module(
            '.{}.lookup'.format(instrument.lower()), 'gemini_instruments')

    addInstrumentFilterWavelengths(instrument.upper(), lookup.filter_wavelengths)
    module = import_module('.{}'.format(instrument), __name__)
    cls = getattr(module, 'AstroFaker{}'.format(instrument.capitalize()))

    # astrodata refactor.
    try:  # new astrodata
        factory.add_class(cls)
    except AttributeError:  # old astrodata
        factory.addClass(cls)


add_instrument('f2')
add_instrument('gmos')
add_instrument('gnirs')
add_instrument('gsaoi')
add_instrument('niri')

create = AstroFaker.create
open = AstroFaker.open

try:
    __version__ = version('astrofaker')
except PackageNotFoundError:
    __version__ = 'unknown'  # source checkout without building package
