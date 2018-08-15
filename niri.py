from .astrofaker import AstroFaker, noslice
from gemini_instruments.niri.adclass import AstroDataNiri

class AstroFakerNiri(AstroFaker, AstroDataNiri):
    def _add_required_phu_keywords(self):
        self.phu['IAA'] = 270.56  # Value seen in recent headers

    @noslice
    def add_extension(self, data=None, shape=(1024,1024), pixel_scale=0.11635,
                      flip=False):
        """
        NIRI-specific method which provides NIRI-like defaults. Note that we
        don't check for valid NIRI data shapes because we may wish to create
        smaller fake data to speed up computation.
        """
        #if data is not None:
        #    shape = data.shape
        #if shape[0] != shape[1] and shape[0] not in (512, 768, 1024):
        #    raise ValueError("Invalid NIRI data shape {}".format(shape))
        super(self.__class__, self).add_extension(data=data, shape=shape,
                                pixel_scale=pixel_scale, flip=flip)
        self[-1].hdr.update({'LOWROW': 0, 'HIROW': shape[0]-1,
                             'LOWCOL': 0, 'HICOL': shape[1]-1})