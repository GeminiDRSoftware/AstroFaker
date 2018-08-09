import numpy as np
from scipy.ndimage.filters import gaussian_filter
import datetime
from astropy.modeling import models
from astropy.wcs import WCS
from functools import wraps
from types import MethodType

@models.custom_model
def Sersic(x, y, amplitude=1.0, r_e=1.0, n=4.0):
    m = 1.0/n
    # This approximation is from Ciotti & Bertin (1999; A&A, 352, 447)
    b = 2.*n - 1./3. + 4.*m/405. + 46.*m**2/25515.
    r = np.sqrt(x*x + y*y)
    return amplitude * np.exp(-b*(r/r_e)**m)

def sliceable(fn):
    # Works on a slice but can operate on a full AD if sent
    # slice-by-slice
    @wraps(fn)
    def gn(self, *args, **kwargs):
        if self.is_single:
            ret_value = fn(self, *args, **kwargs)
        else:
            ret_value = [fn(ext, *args, **kwargs) for ext in self]
        return ret_value
    return gn

def sliceonly(fn):
    # Raises TypeError if NOT run on a slice
    @wraps(fn)
    def gn(self, *args, **kwargs):
        if self.is_single:
            ret_value = fn(self, *args, **kwargs)
        else:
            raise TypeError("Can only run {} on a single AD "
                            "slice".format(fn.__name__))
        return ret_value
    return gn

def noslice(fn):
    # Raises TypeError if run on a slice
    @wraps(fn)
    def gn(self, *args, **kwargs):
        if not self.is_single:
            ret_value = fn(self, *args, **kwargs)
        else:
            raise TypeError("Can only run {} on an unsliced AD "
                            "instance".format(fn.__name__))
        return ret_value
    return gn

def convert_rd2xy(fn):
    # Allows you to pass (ra,dec) instead of (x,y), and will determine which
    # extension those world coordinates lie on if sent a full AD
    @wraps(fn)
    def gn(self, *args, **kwargs):
        ra = kwargs.get("ra")
        dec = kwargs.get("dec")
        if not (ra is None or dec is None):
            if self.is_single:
                wcs = WCS(self[0].hdr)
                x, y = wcs.all_world2pix(ra, dec, 0)
                slice = self
            else:
                for index in range(len(self)):
                    wcs = WCS(self[index].hdr)
                    x, y = wcs.all_world2pix(ra, dec, 0)
                    nypix, nxpix = self[index].data.shape
                    if x>-0.5 and y>-0.5 and y<nypix-0.5 and x<nxpix-0.5:
                        slice = self[index]
                        break
                else:
                    print "Location not on any extensions"
                    return
            del kwargs["ra"], kwargs["dec"]
            ret_value = fn(slice, x=x, y=y, *args, **kwargs)
        else:
            ret_value = fn(self, *args, **kwargs)  # unchanged
        return ret_value
    return gn

############################ ASTROFAKER CLASS ###############################
class AstroFaker(object):
    def __new__(cls, *args, **kwargs):
        """Since we never call an AstroFakerInstrument's __init__(), we set
        up the the internal attributes here"""
        instance = object.__new__(cls)
        instance._seeing = 0.8
        instance._descriptor_dict = {}
        return instance

    def __setattr__(self, name, value):
        """
        Allow descriptor return values to be set directly, by overriding
        the method. This does not handle the descriptor arguments, which
        just get ignored.

        In general, it is more beneficial to set the relevant header keywords
        so that the descriptor method returns the desired value but sometimes
        that is difficult (e.g., NIRI filter_name) so this option is provided
        """
        def override_descriptor(name):
            def fn(self, *args, **kwargs):
                return self._descriptor_dict[name]
            object.__setattr__(self, name, MethodType(fn, self, type(self)))

        if hasattr(self, name):
            attr = getattr(self, name)
            try:
                if attr.descriptor_method:
                    self._descriptor_dict[name] = value
                    override_descriptor(name)
                    return
            except AttributeError:
                pass
        # Do the "normal" thing if it's not a descriptor
        super(AstroFaker, self).__setattr__(name, value)

    ########################## SEEING DEFINITION ############################
    @property
    def seeing(self):
        return self._seeing

    @seeing.setter
    @noslice
    def seeing(self, value):
        if value > 0:
            self._seeing = value
        else:
            raise ValueError("Seeing must be positive!")
    ######################## HEADER FAKING METHODS ##########################
    @noslice
    def add_extension(self, shape=None, dtype=np.float32, pixel_scale=None,
                      pa=0, flip=False):
        """Add an extension to the existing AD, with some header keywords"""
        # If no shape is provided, use the first extension's shape
        if shape is None and len(self) > 0:
            shape = self[0].nddata.shape
        self.append(np.zeros(shape, dtype=dtype))
        extver = len(self)
        shape_value = '[1:{1},1:{0}]'.format(*shape)
        self[-1].hdr.update({'EXTNAME': 'SCI',
                             'EXTVER': extver,
                             self._keyword_for('data_section'): shape_value,
                             self._keyword_for('detector_section'): shape_value,
                             self._keyword_for('array_section'): shape_value})
        self.phu['PA'] = pa
        if len(self) == 1 and 'RA' in self.phu and 'DEC' in self.phu:
            self[-1].hdr.update({'CRVAL1': self.phu['RA'],
                                    'CRVAL2': self.phu['DEC'],
                                    'CTYPE1': 'RA---TAN',
                                    'CTYPE2': 'DEC--TAN',
                                    'CRPIX1': 0.5*(shape[1]+1),
                                    'CRPIX2': 0.5*(shape[0]+1)})
        if pixel_scale is None:
            pixel_scale = self.pixel_scale()
        if pixel_scale is not None:
            cd_matrix = models.Rotation2D(angle=pa)(
                *np.array([[pixel_scale if flip else -pixel_scale, 0],
                           [0, pixel_scale]]) / 3600.0)
            self[-1].hdr.update({'CD{}_{}'.format(i+1, j+1): cd_matrix[i][j]
                                    for i in (0,1) for j in (0,1)})

    @noslice
    def pixel_offset(self, x_offset, y_offset):
        """
        Apply offsets to the WCS CRPIXi values.
        Assumes all extensions have the same orientation; if not, needs to
        be overridden by an AstroFakerInstrument class
        
        Parameters
        ----------
        x_offset: float
            Shift in x-direction (+ve moves objects to the right)
        y_offset: float
            Shift in y-direction (+ve moves objects up)
        """
        # TODO: We need to do detector_?_offset() too!
        crpix1 = self.hdr['CRPIX1']
        crpix2 = self.hdr['CRPIX2']
        for ext, cr1, cr2 in zip(self, crpix1, crpix2):
            ext.hdr['CRPIX1'] = cr1 + x_offset
            ext.hdr['CRPIX2'] = cr2 + y_offset
        self.phu[self._keyword_for('telescope_x_offset')] = x_offset
        self.phu[self._keyword_for('telescope_y_offset')] = y_offset

    @noslice
    def time_offset(self, seconds=0, minutes=0):
        """
        Change ut_datetime forward by specified amount. The new value is put in
        the DATE-OBS keyword, which is the first place the descriptor looks
        
        Parameters
        ----------
        seconds/minutes: float
            Offset (passed directly to datetime.timedelta object)
        """
        new_time = self.ut_datetime() + datetime.timedelta(seconds=seconds,
                                                           minutes=minutes)
        self.phu['DATE-OBS'] = new_time.isoformat()

    @noslice
    def rotate(self, angle):
        """
        Modify the CD matrices of all the headers to effect a rotation.
        This assumes that the CRVALi keywords are the same in all headers
        or else this modification may be inconsistent.

        Parameters
        ----------
        angle: float
            Rotation angle (degrees)
        """
        for ext in self:
            cd_matrix = models.Rotation2D(angle)(*WCS(ext.hdr).wcs.cd)
            ext.hdr.update({'CD{}_{}'.format(i+1, j+1): cd_matrix[i][j]
                             for i in (0, 1) for j in (0, 1)})

    ######################### PIXEL FAKING METHODS ##########################
    @sliceable
    def zero_data(self, shape=None):
        """
        Reset all pixel values to zero, and delete mask and variance
        
        Parameters
        ----------
        shape: tuple/None
            shape of the data extension (if None, keep current shape)
        """
        if shape is None:
            shape = self.data.shape
        self.reset(data=np.zeros(shape), mask=None, variance=None)

    @sliceable
    def add_poisson_noise(self, scale=1.0):
        """
        Add Poisson-like noise (Normal distribution is used) to pixel data
        
        Parameters
        ----------
        scale: float
            Factor by which to scale the calculated noise
        """
        noise = (scale * np.sqrt(np.where(self.data>0, self.data, 0)) *
                 np.random.randn(*self.data.shape))
        if self.hdr.get('BUNIT', 'ADU').upper() == 'ADU':
            noise /= np.sqrt(self.gain())
        self.add(noise)

    @sliceable
    def add_read_noise(self, scale=1.0):
        """
        Add read noise (Normal distribution is used) to pixel data
                
        Parameters
        ----------
        scale: float
            Factor by which to scale the calculated noise
        """
        noise = scale * self.read_noise() * np.random.randn(*self.data.shape)
        if self.hdr.get('BUNIT','ADU').upper() == 'ADU':
            noise /= self.gain()
        self.add(noise)

    @sliceonly
    def add_object(self, obj):
        """
        Adds an object to a particular extension
        
        Parameters
        ----------
        obj: function/Model
            must return pixel value of object at each pixel in image
        """
        ygrid, xgrid = np.mgrid[:self.data.shape[0], :self.data.shape[1]]
        obj_data = obj(xgrid, ygrid)
        self.add(obj_data)

    @convert_rd2xy
    @sliceonly
    def add_star(self, amplitude=None, flux=None, fwhm=None, x=None, y=None):
        """
        Adds a star (Gaussian2D object) at the specified location.
        Decorated by convert_rd2xy so (ra,dec) can be given
        
        Parameters
        ----------
        amplitude: float/None
            Peak pixel value
        flux: float
            Total counts in object (only used if amplitude=None)
        fwhm: float/None
            FWHM in arcseconds (if None, use seeing attribute)
        x, y: float
            location of centre of star in pixels
            (Decorated by @convert_rd2xy so ra, dec can be specified)
        """
        sigma = 0.42466 * (fwhm or self.seeing) / self.pixel_scale()
        if amplitude is None:
            if flux is None:
                raise ValueError("Need to specify amplitude or flux")
            else:
                amplitude = flux / (2 * np.pi * sigma * sigma)
        obj = models.Gaussian2D(amplitude=amplitude, x_mean=x, y_mean=y,
                                x_stddev=sigma, y_stddev=sigma)
        self.add_object(obj)

    @convert_rd2xy
    @sliceonly
    def add_galaxy(self, amplitude=None, n=4.0, r_e=1.0, axis_ratio=1.0, pa=0.0, x=None, y=None):
        """Adds a Sersic profile galaxy, convolved with the seeing, at the
        specified location.
        
        Parameters
        ----------
        amplitude: float
            Peak pixel value
        n: float
            Sersic index
        r_e: float
            effective radius (arcseconds)
        axis_ratio: float
            ratio of major to minor axis
        pa: float
            position angle (in pixel space) of major axis
        TODO: Convert to sky PA
        x, y: float
            location of centre of star in pixels
            (Decorated by @convert_rd2xy so ra, dec can be specified)
        """
        obj = ((models.Shift(-x) & models.Shift(-y)) | models.Rotation2D(-pa) |
               (models.Scale(axis_ratio) & models.Identity(1)) |
               Sersic(amplitude=amplitude, r_e=r_e/self.pixel_scale(), n=n))
        ygrid, xgrid = np.mgrid[:self.data.shape[0], :self.data.shape[1]]
        obj_data = obj(xgrid, ygrid)
        sigma = 0.42466 * self.seeing / self.pixel_scale()
        convolved_data = gaussian_filter(obj_data, sigma=sigma, mode='constant')
        self.add(convolved_data)