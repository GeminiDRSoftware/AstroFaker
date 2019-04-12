Test Examples
*************

This section provides examples of unit tests that use the ``AstroFaker``
module.


Photometry Primitives
=====================

The primitives in the ``Photometry`` class are all tested with fake NIRI
data, purely for reasons of simplicity. Additional tests using GMOS to
test multi-extension data could also be written.

The unit tests module has a Pytest fixture to initialize an instance of
a ``NIRIImage`` object with a single image that has stars at specified
locations

.. code-block:: python

   STAR_POSITIONS = [(200.,200.), (300.5,800.5)]

   @pytest.fixture()
   def niriImage():
       ad = AstroFaker.create('NIRI', 'IMAGE')
       ad.init_default_extensions()
       # SExtractor struggles if the background is noiseless
       ad.add_read_noise()
       for x, y in STAR_POSITIONS:
           ad[0].add_star(amplitude=500, x=x, y=y)
      return NIRIImage([ad])


addReferenceCatalog
-------------------

To test the ``addReferenceCatalog`` primitive, we first call it as a method
on our instance of the ``NIRIImage`` class, and confirm that it returns a
list containing a single image.
We then check that the appropriate timestamp keyword has been added to the
header, and that a ``REFCAT`` attribute has been added at the top level.
Finally, we confirm that the locations of the sources in the reference
catalog are all within the requested distance (which we determine from the
default parameter value).

.. code-block:: python

   def test_addReferenceCatalog(niriImage):
       adinputs = niriImage.addReferenceCatalog()
       assert len(adinputs) == 1
       ad = adinputs[0]
       assert timestamp_keys["addReferenceCatalog"] in ad.phu
       assert hasattr(ad, 'REFCAT')
       search_radius = niriImage.params['addReferenceCatalog'].radius
       base_coord = SkyCoord(ra=ad.wcs_ra(), dec=ad.wcs_dec(), unit='deg')
       for ra, dec in ad.REFCAT['RAJ2000', 'DEJ2000']:
           assert SkyCoord(ra=ra, dec=dec, unit='deg').separation(base_coord).value < search_radius
