.. _overview:

Overview
********

DRAGONS (Data Reduction for Astronomy from Gemini Observatory North and South)
comprises four separate packages:

* ``astrodata``, which defines a uniform access structure for astronomical
  data

* ``gemini_instruments``, which provides a high-level interface for access
  to metadata via methods known as *descriptors*

* ``geminidr``, which defines primitives to manipulate the data and recipes
  that link together primitives to provide full reduction of raw data

* ``recipe_system``, which links these together and, via "mappers",
  automatically associates the primitives and recipes with the input data

AstroFaker replaces the standard ``gemini_instruments`` module associated
with ``astrodata``. It provides its own subclasses for Gemini instruments
that are extended from the ``astrodata`` classes with the addition of the
``AstroFaker`` mixin.



The structure of the AstroFaker package is as follows::

  AstroFaker/
    __init__.py
    astrofaker.py
    fake_it.py
    <instrument1.py>
    <instrument2.py>
    <instrument3.py>

Each instrument supported by AstroFaker has its own module but, unlike
the modules in ``gemini_instruments``, this is merely a single file rather
than a separate directory.


The code in ``AstroFaker/__init__.py`` is::

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

The ``add_instrument()`` function performs the essential housekeeping that was
done by the individual ``__init__``\s in the ``gemini_instruments`` modules:
the dictionary of filter wavelengths is added to the internal database, and
the AstroFaker subclass is registered with the AstroData factory. Due to the
use of dynamic loading, the naming convention must be adhered to rigidly, with
the AstroFaker subclass in ``instrument.py`` called ``AstroFakerInstrument``,
capitalizing the first letter, e.g., the the module ``gnirs.py`` defines the
class ``AstroFakerGnirs``.



Do I still need to import astrodata?
====================================

In general, no. The ``astrodata.open`` and ``astrodata.create`` methods are
superseded by ``AstroFaker`` class methods with the same names.