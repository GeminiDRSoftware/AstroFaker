from .astrofaker import AstroFaker
from gemini_instruments.f2.adclass import AstroDataF2

class AstroFakerF2(AstroFaker, AstroDataF2):
    def _add_required_phu_keywords(self):
        self.phu['IAA'] = 0.117

