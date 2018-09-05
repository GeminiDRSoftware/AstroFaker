# This module contains a series of functions for creating a fake dataset.
import numpy as np
from functools import partial
from astropy.wcs import WCS
from copy import deepcopy

def make_star_function(ad_base, nstars=10, border=0, radius=None,
                       fwhm=None, flux=1., seed=None):
    """
    Create a function to add stars to an image at a series of random RA/dec
    coordinates. These coordinates are determined based on the sky coverage
    of a provided AstroData object.

    The function created by this function takes an AD object as an argument
    and adds stars at these positions. The idea, therefore, is to allow
    multiple images, with different pointings, to produce observations of
    the same counterfeit sky, possibly using the dither() function below.
    
    Parameters
    ----------
    ad_base: AstroData
        An AD object that will be the reference
    nstars: int
        Number of star-like objects to add
    border: int
        Number of pixels to avoid around the edges of each extension when
        placing stars. Note: A negative value will allow objects to be placed
        outside the field of view of ad_base. Ignored if radius is not None.
    radius: float/None
        The radius (in arcseconds) around the ra() and dec() locations
        within which stars may be placed.
    fwhm: float/None/function
        FWHM of each star. A function should accept an integer which is the
        location in the sequence of stars (0=first)
    flux: float/function
        Total flux of each star. A function should accept an integer, like "fwhm"
    seed: int/None
        Random number seed, to ensure repeatability
    """
    def stars(ad, ra_list, dec_list, flux_list, fwhm_list):
        for ra, dec, flux, fwhm in zip(ra_list, dec_list, flux_list, fwhm_list):
            ad.add_star(ra=ra, dec=dec, flux=flux, fwhm=fwhm)

    ra_list, dec_list = [], []
    flux_list = []
    fwhm_list = []
    wcs = [WCS(h) for h in ad_base.hdr]

    if radius is not None:
        try:
            ra_base = ad_base.ra()
            dec_base = ad_base.dec()
            pix_scale = ad_base.pixel_scale()
            xbase, ybase = wcs[0].all_world2pix(ra_base, dec_base, 0)
        except:
            raise ValueError("Cannot determine WCS info of reference image")

    np.random.seed(seed)
    for i, index in enumerate(np.random.randint(len(ad_base), size=nstars)):
        if radius is None:
            shape = ad_base[index].data.shape
            stary, starx = [np.random.rand() * (len_axis-2*border) + border
                            for len_axis in shape]
            ra, dec = wcs[index].all_pix2world(starx, stary, 0)
        else:
            # To avoid difficulties with crossing poles, we're going to do this
            # in pixel space
            while True:
                rx, ry = np.random.rand(2)
                if rx*rx + ry*ry <= 1.0:
                    break
            starx = xbase + rx * radius/pix_scale
            stary = ybase + ry * radius/pix_scale
            ra, dec = wcs[0].all_pix2world(starx, stary, 0)

        ra_list.append(ra)
        dec_list.append(dec)
        fwhm_list.append(fwhm(i) if callable(fwhm) else fwhm)
        flux_list.append(flux(i) if callable(flux) else flux)

    return partial(stars, ra_list=ra_list, dec_list=dec_list,
                   flux_list=flux_list, fwhm_list=fwhm_list)

def dither(ad_base, cycles=1, shape=(3,3), offset=10, rms=0, dither_overhead=5.,
           add_objects=None, add_noise=True, seed=None, write=False):
    """
    This produces a series of AD objects mimicking one or more rectangular
    dither patterns on the sky. A function to position objects at the same
    celestial coordinates in each image can be provided. Pointing errors can
    also be introduced.
    
    Parameters
    ----------
    ad_base: AstroData
        Base AD object from which to construct new fake ADs
    cycles: int
        Number of dither cycles
    shape: tuple
        Shape of dither pattern. There will by cycles*shape[0]*shape[1] images
        produced
    offset: float
        step (in arcseconds) between dither positions
    rms: float
        rms of Gaussian-distributed positional errors (in arcseconds)
    dither_overhead: float
        time (in seconds) between exposures
    add_objects: function/None
        function to call to add objects to each output AD object
    add_noise: bool
        Call add_read_noise() and add_poisson_noise() after creation?
    seed: int/None
        Random number seed, to ensure repeatability
    write: bool
        Write files to disk?
    """
    adinputs = []
    exptime = ad_base.exposure_time()
    time_since_start = 0.
    np.random.seed(seed)
    for cycle in range(cycles):
        for iy in range(shape[1]):
            yoff = (iy - 0.5 * (shape[1]-1)) * offset
            for ix in range(shape[0]):
                xoff = (ix - 0.5 * (shape[0]-1)) * offset
                ad = deepcopy(ad_base)
                ad.time_offset(seconds=time_since_start)
                time_since_start += exptime + dither_overhead
                ad.update_filename(suffix="_{}{}{}".format(cycle if cycles>1 else '',
                                                           ix, iy))
                ad.phu['ORIGNAME'] = ad.filename
                dx, dy = rms * np.random.randn(2)
                # Place objects at the "true" locations
                ad.sky_offset(xoff+dx, yoff+dy)
                if add_objects is not None:
                    add_objects(ad)
                # Reset the header offsets to the requested values
                ad.sky_offset(-dx, -dy)
                if add_noise:
                    ad.add_poisson_noise()
                    ad.add_read_noise()
                adinputs.append(ad)
                if write:
                    ad.write(overwrite=True)
    return adinputs