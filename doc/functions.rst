Functions
*********

This section lists functions that have been written to aid with the
production of fake data. They live in the ``fake_it.py`` module.


**dither** *(ad_base, cycles=1, shape=(3,3), offset=10, rms=0, dither_overhead=5., add_objects=None, add_noise=True, seed=None)*

    This function returns a list of ``AstroFaker`` objects representing a sequence
    of images taken in one or more cycles of a standard gird-like dither pattern,
    with the offset header keywords set appropriately. A function (the
    *add_objects* parameter) can be passed that produces a consistent artificial
    sky, and random offsetting errors can be introduced. The observation times of
    consecutive images are increased by the exposure time of each image plus an
    overhead (the *dither_overhead* parameter), ensuring that the ``associateSky``
    primitive will work as expected.

    ad_base
      An *AstroFaker* object used as a reference

    cycles
      An *int* indicating the number of dither cycles to model

    shape
      A two-element *tuple* indicating the size of the grid-like dither pattern

    offset
      A *float* indicating the spacing (in arcseconds) between dither positions

    rms
      A *float* indicating the positional uncertainty (in arcseconds) in each of
      right ascension and declination. Although the offsets in the headers will
      be exactly the commanded values, the "true" positions may be given an
      uncertainty, meaning the objects will not be at precisely the right
      coordinates according to the WCS. This is irrelevant if *add_objects* is
      ``None``.

    dither_overhead
      A *float* indicating the additional time (in seconds) between subsequent
      exposures in the sequence

    add_objects
      A callable function that takes an ``AstroFaker`` object as an argument and
      adds celestial objects to it. The output of the **make_star_function**
      function is suitable.

    add_noise
      A *boolean* that specifies whether to call the ``add_read_noise`` and
      ``add_poisson_noise`` methods to each image

    seed
      An *int* (or ``None``) that is passed to ``numpy.random.seed()`` to seed
      the random number generator before creating the offsetting errors


**make_star_function** *(ad_base, nstars=10, border=None, radius=None, fwhm=None, flux=1., seed=None)*

    This function produces a function that takes an ``AstroFaker`` object as an
    argument and places fake stars on it in accordance with a pre-constructed
    "artificial sky". The positions of these stars are determined either by
    the footprint of a reference frame passed to **make_star_function**, or
    within a specified radius of the nominal position of this frame. Locations
    are determined randomly within this region, but a seed for the random
    number generator can be passed to this function to ensure that the same
    positions are always used.

    ad_base
      An *AstroFaker* object used as a reference

    nstars
      An *int* indicating the number of stars to put in the "sky"

    border
      An *int* indicating how far away from the edge of the reference image
      to avoid placing stars. A negative value will allow stars to be placed
      outside of the field of view of the reference, which may be desirable

    fwhm
      A *float* indicating the FWHM (in arcseconds) of the stellar sources.
      Or ``None``, which will use the ``seeing`` attribute of each image.
      Or a function that should take an integer representing the sequence number
      of the star (0-indexed) and return a FWHM value.

    flux
      A *float* indicating the total flux of each star. Again, a function that
      takes a single integer argument can be used.

    seed
      An *int* (or ``None``) that is passed to ``numpy.random.seed()`` to seed
      the random number generator before creating the star positions