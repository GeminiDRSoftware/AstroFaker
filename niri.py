import numpy as np

from .astrofaker import AstroFaker, noslice
from gemini_instruments.niri.adclass import AstroDataNiri

class AstroFakerNiri(AstroFaker, AstroDataNiri):
    @noslice
    def add_extension(self, dtype=np.float32, pixel_scale=0.11635,
                      pa=0, flip=False):
        super(self.__class__, self).add_extension(shape=(1024,1024), dtype=dtype,
                                pixel_scale=pixel_scale, pa=pa, flip=flip)
        self[-1].hdr.update({'LOWROW': 0, 'HIROW': 1023,
                             'LOWCOL': 0, 'HICOL': 1023})