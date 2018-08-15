from .astrofaker import AstroFaker
from gemini_instruments.f2.adclass import AstroDataF2

class AstroFakerF2(AstroFaker, AstroDataF2):
    def _add_required_phu_keywords(self, mode):
        self.phu['IAA'] = 0.117  # Value seen in recent headers

        if 'IMAGE' in mode:
            self.phu['GRISM'] = 'Open'