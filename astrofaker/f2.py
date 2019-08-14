from astrofaker import AstroFaker, noslice
from gemini_instruments.f2.adclass import AstroDataF2

class AstroFakerF2(AstroFaker, AstroDataF2):
    def _add_required_phu_keywords(self, mode):
        self.phu['IAA'] = 0.117  # Value seen in recent headers
        self.phu['CD3_3'] = 1

        if 'IMAGE' in mode:
            self.phu['GRISM'] = 'Open'

    @noslice
    def init_default_extensions(self):
        del self[:]
        self.add_extension(shape=(1,2048,2048), pixel_scale=0.179)
