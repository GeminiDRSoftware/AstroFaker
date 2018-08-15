from .astrofaker import AstroFaker
from gemini_instruments.gsaoi.adclass import AstroDataGsaoi

class AstroFakerGsaoi(AstroFaker, AstroDataGsaoi):
    def _add_required_phu_keywords(self):
        self.phu['IAA'] = 0.959  # Value seen in recent headers
