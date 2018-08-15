from .astrofaker import AstroFaker, noslice
from gemini_instruments.gnirs.adclass import AstroDataGnirs

class AstroFakerGnirs(AstroFaker, AstroDataGnirs):
    def _add_required_phu_keywords(self, mode):
        self.phu['IAA'] = 89.747  # Value seen in recent headers

        if 'IMAGE' in mode:
            self.phu['ACQMIR'] = 'In'
        elif 'SPECT' in mode:
            self.phu['ACQMIR'] = 'Out'
        elif 'DARK' in mode:
            self.phu['OBSTYPE'] = 'DARK'
        else:
            raise ValueError('GNIRS mode must include IMAGE, SPECT, or DARK')

    @noslice
    def add_extension(self, data=None):
        """
        GNIRS-specific method which provides GNIRS-like defaults. Unlike NIRI,
        we demand that GNIRS data have the shape of real data because it's a
        bit of an odd instrument and is only likely to be used in tests for
        GNIRS-specific things, where non-standard data will cause trouble.
        """
        if data is not None and data.shape != (1022, 1024):
           raise ValueError("Invalid GNIRS data shape {}".format(data.shape))
        super(self.__class__, self).add_extension(data=data, shape=(1022, 1024),
                                                  pixel_scale=0.15, flip=False)
        self[-1].hdr.update({'LOWROW': 0, 'HIROW': 1023,
                             'LOWCOL': 0, 'HICOL': 1023})