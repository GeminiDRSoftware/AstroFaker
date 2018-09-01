AstroFaker class
****************

The ``AstroFaker`` class is a mixin to be added to the existing ``AstroData``
classes, viz::

  class AstroFakerF2(AstroFaker, AstroDataF2):
      <methods>

The base ``AstroFaker`` class adds methods that allow fake data to be
constructed. These methods are described in detail in :ref:`methods`.

``AstroFaker`` objects also have a ``seeing`` attribute assigned to them.
This is used by some of the data-faking methods to determine the morphology
of fake objects. It is specified in arcseconds and the default value is 0.8.

It is generally advised that fake datasets be constructed in such a way as
to have them handled by the standard ``gemini_instrument`` classes. However,
in some cases the mapping between header keywords and descriptors may be
complex and, for ease-of-use, the base ``AstroFaker`` class allows the
descriptor methods it inherits from the standard instrument class to be
overridden::

  ad.filter_name = 'K'

Subsequent calls to the descriptor (as ``ad.filter_name()``) will return
this value. Note that when a
descriptor is overridden in this way, any arguments passed to it are ignored.
Therefore, ``ad.filter_name(pretty=False)`` will return the value ``'K'``,
even though that parameter would normally result in a more complex string
being returned.