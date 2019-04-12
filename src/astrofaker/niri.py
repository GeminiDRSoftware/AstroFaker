from .astrofaker import AstroFaker, noslice
from gemini_instruments.niri.adclass import AstroDataNiri

PIXEL_SCALES = {6: 0.1171, 14: 0.499, 32: 0.0219}


class AstroFakerNiri(AstroFaker, AstroDataNiri):
    def _add_required_phu_keywords(self, mode):
        self.phu['IAA'] = 270.56  # Value seen in recent headers

    @noslice
    def init_default_extensions(self, fratio=6, roi_size=1024):
        """
        fratio; int
          The f-ratio at which the instrument is located
        roi_size: int
          The linear size of the ROI section

        Raises a ValueError for inappropriate values/combinations
        """
        del self[:]
        try:
            pixel_scale = PIXEL_SCALES[fratio]
        except KeyError:
            raise ValueError("Invalid f/ratio")
        if self.is_ao():
            if fratio == 32:
                pixel_scale = 0.0214
            else:
                raise ValueError("AO used without f/32 setting")
            if self.phu.get('INPORT') != 1:
                raise ValueError("AO observations require the bottom port")
        if roi_size not in (512, 768, 1024):
            raise ValueError("Invalid roi_size")
        flip = (self.phu.get('INPORT') == 1 and not self.is_ao())
        self.add_extension(shape=(roi_size, roi_size),
                           pixel_scale=pixel_scale,
                           flip=flip)

    @noslice
    def add_extension(self, data=None, shape=(1024, 1024),
                      pixel_scale=PIXEL_SCALES[6], flip=False,
                      extra_keywords={}):
        """
        NIRI-specific method which provides NIRI-like defaults. Note that we
        don't check for valid NIRI data shapes because we may wish to create
        smaller fake data to speed up computation.

        This extends the AstroFaker method to deal with the bizarre way NIRI
        describes its sections.
        """
        extra_keywords.update({'LOWROW': 0, 'HIROW': shape[0] - 1,
                               'LOWCOL': 0, 'HICOL': shape[1] - 1})
        super(self.__class__, self).add_extension(data=data, shape=shape,
                                                  pixel_scale=pixel_scale, flip=flip,
                                                  extra_keywords=extra_keywords)
        for sec in ('array', 'data', 'detector'):
            del self[-1].hdr[self._keyword_for('{}_section'.format(sec))]
