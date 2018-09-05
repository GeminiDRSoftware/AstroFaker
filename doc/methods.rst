.. _methods:

AstroFaker Methods
******************

This section lists all the methods of the ``AstroFaker`` class. These
modify in-place the ``AstroFaker`` instance on which they are called
and return ``None``.


Object creation methods
=======================

``AstroFaker`` has two static methods for producing a new instance of
an instrument-specific subclass.

**create** *(header, mode='IMAGE', extra_keywords={}, filename='N20010101S0001.fits')*

  This method creates an ``AstroFaker`` object using either an existing
  header-like object or entirely from scratch. If creating from scratch
  (by specifying a instrument-name string as the *header* parameter, as
  described below), some keywords are added to the PHU to ensure
  a minimum degree of functionality. The *RA* and *DEC* keywords are set
  arbitrarily to (180,0) and the exposure time to 10 seconds. All telescope
  offsets are set to zero.

  header
    A *string* specifying the name of the instrument, or a ``PrimaryHDU`` or
    ``Header`` object. If this is a string, then an ``AstroFaker`` object
    will be created "from scratch".

  mode
    A *string* or *list* defining the mode of the observation when constructing
    an object from scratch. This is passed directly to the
    **_add_required_phu_keywords** method of the appropriate instrument
    subclass.

  extra_keywords
    A *dict* defining extra keywords to be added to the PHU after creating the
    object. These are added at the end of the method and so will overwrite any
    keywords already there (e.g., the default keywords when creating from
    scratch, or those in the header-like object provided).

  filename
     A *string* with the full filename (including extension). This is placed in
     the *ORIGNAME* keyword and assigned to the *filename* and *_orig_filename*
     attributes of the created object.

**open** *(source)*

  This method simply calls the ``astrodata.open`` method. With ``AstroFaker``
  imported instead of ``gemini_instruments``, the returned object will be a
  member of the appropriate ``AstroFaker`` instrument subclass. It exists
  solely to remove the need to explicitly ``import astrodata`` in code that
  will construct fake data in this way.

  source
    Can be a file on disk, a ``PrimaryHDU`` object, or a ``Header`` object.



Decorators
==========

**convert_rd2xy**

  This should be used to decorate a *sliceonly* method that takes *x* and *y*
  parameters specifying a pixel location on that extension. A method decorated
  in this way can then be called on a full ``AstroFaker`` object with *ra* and
  *dec* specified as positional parameters instead of *x* and *y*. The decorator
  will determine which extension the celestial coordinates lie on and call the
  decorated method on that extension only with the pixel coordinates determined
  from the WCS. The decorated method should *not* have *ra* and *dec* parameters
  in its call signature.

.. todo::

   This only applies the method to the slice where the object center lies, so
   large objects will be truncated at the extension boundaries, rather than
   cross over onto adjacent extensions.

**noslice**

  This should be used to decorate methods that can only operate on a full
  ``AstroFaker`` object. It will raise a ``TypeError`` if run on a single
  slice.

**sliceable**

  This should be used to decorate methods that can operate on *either* a full
  ``AstroFaker`` object *or* a slice. If run on a full object, it will call
  the decorated method on each slice in sequence and return a list of the
  values returned by each call.

**sliceonly**

  This should be used to decorate methods that can only operate on a single
  slice. It will raise a ``TypeError`` if run on a full ``AstroFaker`` object.


Data initialization methods
===========================

**add_extension** *(self, data=None, shape=None, dtype=np.float32, pixel_scale=None, flip=False, extra_keywords={})*

  This method adds an extension to an existing ``AstroFaker`` object. A
  minimal header is added with *EXTVER* being set equal to the number of
  extensions present (after this has been added) and the three "section"
  descriptors (``array_section``, ``data_section``, and ``detector_section``)
  all set to the shape of the data by setting the appropriate header keywords.

  If this is the first extension and *RA* and *DEC* keywords exist in the PHU,
  a WCS is constructed with the center of the array assumed to be the location
  of those coordinates. The value of the *PA* PHU keyword is used to determine
  the on-sky orientation of the data; if absent, a value of zero is assumed.
  If this is not the first extension, then no WCS keywords are added because
  there is no information about how they should relate to those in the existing
  extenion(s).

  Instrument-specific subclasses may define their own versions of this method
  that limit or exclude some of the parameters.

  data
    An *array* from which the SCI plane should be constructed.

  shape
    A *tuple* describing the shape of the data plane, if the *data* parameter
    is not supplied, in which case all pixels will be initialized to zero. If
    both *data* and *shape* are ``None``, the shape will be taken from the
    first extension, if it exists; otherwise, a ``ValueError`` will be raised.

  dtype
    A *datatype* describing the nature of the SCI plane. This is only used if
    *data* is ``None``; otherwise, the datatype is preserved.

  pixel_scale
    A *float* specifying the pixel scale in arcseconds. If this is ``None``, the
    value of the ``pixel_scale`` descriptor will be used.

  flip
    A *boolean* specifying whether the orientation of the WCS should be flipped
    (i.e., East will be to the right if North is up).

  extra_keywords
     A *dict* defining etra keywords to put in this extension's header. This is
     performed at the end of the method and will overwrite any standard keywords
     added by the method.

**init_default_extensions** *(self)*

  This is an abstract method that *must* be defined for each instrument
  subclass. It is intended to produce standard-looking data, and the
  **add_extension** method (below) should be used for more exotic creations.
  The parameters it takes will vary depending on the flexibility of
  each instrument. All implementations should be decorated with ``@noslice``
  and start by deleting all existing extensions (``del self[:]``).

  Details of how this method is implemented for the various supported
  instruments are given in :ref:`subclasses`.

.. todo::

   Are the WCS header keywords for spectroscopic data different? If so, these
   methods will need to alter their behavior based on the ``tags``.


Header-faking methods
=====================

**_add_required_phu_keywords** *(self, mode)*

  This is an abstract methods that *must* be defined for each instrument
  subclass. It is called by the ``AstroFaker.create`` method and updates the
  PHU with instrument-specific header keywords depending on the specified
  mode of observation. The primary purpose is to ensure that the
  ``AstroFaker`` object gains the appropriate set of tags.

  mode
    A *string* or *list* defining the mode of operation. It seems sensible to
    use AstroData tags (e.g., *IMAGE*, *SPECT*, *BIAS*, *DARK*) to define the
    mode.

**rotate** *(self, angle)*

  angle
    A *float* specifying the angle (in degrees) through which the data should
    be rotated. The *PA* keyword in the PHU is increased by this amount, and
    modified if necessary to lie in the range 0-360.

**sky_offset** *(self, ra_offset, dec_offset)*

  This method alters various header keywords to mimic the effect of a
  telescope offset. Four pairs of keywords are modified.

  The *RAOFFSET* and *DECOFFSE* keywords in the PHU are incremented by the
  values of the parameters.

  The *CRVAL1* and *CRVAL2* keywords in each of the extension headers are
  incremented by the appropriate amounts (arcseconds are converted to
  degrees, and the "cos-delta" factor is applied to *CRVAL1*).

  The *XOFFSET* and *YOFFSET* keywords in the PHU are incremented by the
  values provided by the **_xymapping** method. If the instrument alignment
  angle (IAA) and position angle (PA) are both zero, these values are
  simply the negatives of *ra_offset* and *dec_offset*.

  The *POFFSET* and *QOFFSET* keywords in the PHU are incremented by the
  values provided by the **_pqmapping** method. If the PA is zero, then
  these values are equal to *ra_offset* and *dec_offset*.

  ra_offset, dec_offset
    Offsets in arcseconds to be applied in the right ascension and
    declination directions, respectively.

.. todo::

   I'm not completely sure about these XY/PQ mappings, which is why they're
   abstracted. Some instruments have flipped axes on certain ports so is
   that something we need to implement?

**time_offset** *(self, seconds=0, minutes=0)*

  This method advances the time of the observation by the specified amount.
  The ``ut_datetime`` descriptor is used to determine the time of the
  observation and then the modified time is written to the ``DATE-OBS``
  keyword. This is the first place that the Gemini-level descriptor looks
  so, even if the original file lacks this keyword and the observation
  time is derived in a different way, the modified file will behave as
  desired.

  seconds, minutes
    *Floats* indicating the number of seconds and minutes to advance the
    time (net negative values will result in an earliet time). These are
    passed directly to a ``datetime.timedelta`` object so there is a lot
    of flexibility in the values that can be passed.

Pixel-faking methods
====================

**add_galaxy** *(self, amplitude=None, n=4.0, r_e=1.0, axis_ratio=1.0, pa=0.0, x=None, y=None)*

  This method adds a galaxy-like object at a specified pixel location on a
  given image extension. The galaxy is modelled as an elliptical object
  with a Sersic profile, which is then convolved with a 2D Gaussian to
  represent the seeing.

  With the default signature, this method must be called on a single slice.
  However, it is decorated by ``convert_rd2xy`` so can be called on an unsliced
  object if *ra* and *dec* parameters are specified instead of *x* and *y*.

  amplitude
    A *float* defining the peak of the galaxy profile *before convolution*.

  n
    A *float* defining the Sersic profile index. *n=1* is an exponential disk,
    while *n=4* is a de Vaucouleurs profile.

  r_e
    A *float* defining the effective radius of the Sersic profile in
    arcseconds.

  axis_ratio
    A *float* defining the ratio of major to minor axes.

  pa
    A *float* defining the position angle (east of north) of the major axis.

  x, y
    *Floats* defining the pixel location of the Gaussian's peak. These
    parameters are ignored if **ra** and **dec** are provided.

**add_object** *(self, obj)*

  This method adds an "object" to the SCI plane of an extension. It is
  called by the ``add_star`` method.

  This method can only be run on a single slice.

  obj
    A callable that takes two arrays as arguments, representing the x- and
    y-pixel coordinates, and returns the amplitude of the "object" at that
    pixel location. It is likely that this will be an instance of an
    ``astropy.modeling.models.Model`` object.


**add_poisson_noise** *(self, scale=1.0)*

  This method simulates the effect of photon shot noise on the data by
  adding Gaussian random variates to the pixel data. The standard deviation
  of these variates is given by the square root of the counts in electrons
  of each pixel (or zero for negative pixel values), multiplied by the
  supplied scale factor. Appropriate scaling is performed if the data are
  in ADU, using the value of the *gain* descriptor.

  This method can be run on a sliced or unsliced object.

  scale
    A *float* providing a multiplicative scale factor to be applied to
    determine the standard deviation of the Gaussian distribution.


**add_read_noise** *(self, scale=1.0)*

  This method simulates the effect of read noise on the data by adding
  Gaussian random variates to the pixel data. The standard deviation of
  these variates is given by the value of the *read_noise* descriptor
  multiplied by the supplied scale factor. Since the descriptor returns
  the read noise in electrons, appropriate scaling is performed if the
  data are in ADU, using the value of the *gain* descriptor.

  This method can be run on a sliced or unsliced object.

  scale
    A *float* providing a multiplicative scale factor to be applied to
    the value of the *read_noise* descriptor to determine the standard
    deviation of the Gaussian distribution.

**add_star** *(self, amplitude=None, flux=None, fwhm=None, x=None, y=None)*

  This method add a star-like object at a specified pixel location on a
  given image extension. The star is modelled as a circular Gaussian.

  With the default signature, this method must be called on a single slice.
  However, it is decorated by ``convert_rd2xy`` so can be called on an unsliced
  object if *ra* and *dec* parameters are specified instead of *x* and *y*.

  amplitude
    A *float* defining the peak of the Gaussian.

  flux
    A *float* defining the total number of counts in the Gaussian. Only used
    if *amplitude* is ``None``.

  fwhm
    A *float* defining the full width at half-maximum (FWHM) of the Gaussian.
    If ``None``, the image's ``seeing`` is used.

  x, y
    *Floats* defining the pixel location of the Gaussian's peak. These
    parameters are ignored if **ra** and **dec** are provided.

**zero_data** *(self)*

  This method resets the SCI planes of all extensions to zero (maintaining
  their shapes) and removes the VAR and DQ planes.

  This method can be run on a sliced or unsliced object.


.. _subclasses:

Instrument-specific methods
===========================

This section lists instrument-specific variations and implementations of the
``AstroFaker`` methods.

F2
--

For imaging purposes, F2 is a pretty vanilla instrument so the
**init_default_extensions** method takes no parameters.


GMOS
----

GMOS has a lot of functionality and this means realistic GMOS data for
testing purposes cannot be too vanilla. An ``AstroFakerGmos`` object has
*DETID* and *DETTYPE* keywords created and these are used to determine
the pixel scale from the GMOS lookup table in ``gemini_instruments``.

**init_default_extensions** *(self, num_ext=12, binning=1, overscan=True)*

  num_ext
    An *int* specifying the number of extensions being read out. At present,
    only the value of 12 is accepted.

  binning
    An *int* specifying the pixel binning.

  overscan
    A *boolean* specifying whether to add an overscan section to the data.
    The keywords for the various section descriptors are written to the
    headers appropriately. If this flag is set, the data array will be
    created as unsigned 16-bit integers.

.. todo::

   Allow alternative ROIs.


GNIRS
-----

``AstroFakerGnirs`` objects are likely to only be used for GNIRS-specific
tests and therefore less flexibility is provided for constructing such
objects (who knows what will happen if one attempts to apply the keyhole
mask to a fake 1x1 image?).

The **init_default_extensions** method therefore takes no parameters, while
**add_extension** requires that the data array (if provided) is 1022 rows by
1024 columns.

GSAOI
-----

GSAOI has only one imaging mode so **init_default_extensions** takes no
parameters. The WCS matrices written to the headers of the four extensions
show little consistency between observations, in terms of either the effective
pixel scale or the positional relationship between the detectors, so an
arbitrary average has been employed.

NIRI
----

Most near-infrared tests are expected to use ``AstroFakerNiri`` objects and
therefore these can be constructed with more flexibility than is afforded to
``AstroFakerGnirs``, despite the similar natures of the instruments.

**init_default_extensions** *(self, fratio=6, roi_size=1024)*

  Adds a single extension of the ROI size requested, mimicking the stated
  f-ratio. The method will check for valid values of these parameters,
  perform a orientation flip for non-AO f/32 observations, and raise an
  error if AO observations are being faked at a faster f-ratio or not on
  the bottom port.

  fratio
    An *int* describing the focal ratio of NIRI; must be one of 6, 14, or 32.

  roi_size
    An *int* describing the number of pixels along each size of the detector
    read-out section; must be one of 512, 768, or 1024.