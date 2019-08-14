from astrofaker import AstroFaker, noslice
from gemini_instruments.gsaoi.adclass import AstroDataGsaoi


class AstroFakerGsaoi(AstroFaker, AstroDataGsaoi):
    def _add_required_phu_keywords(self, mode):
        self.phu['IAA'] = 0.959  # Value seen in recent headers

    @noslice
    def init_default_extensions(self):
        del self[:]
        # The WCS of GSAOI is a bit of a mess, with no consistent offsets
        # between the CRPIXi values and random pixel scales
        for i in range(4):
            crpix1 = -500. if (i==0 or i==3) else 1650.
            crpix2 = 3000. if i<2 else 850.
            self.add_extension(shape=(2048,2048), pixel_scale=0.0195,
                               extra_keywords={'CRPIX1': crpix1,
                                               'CRPIX2': crpix2})
