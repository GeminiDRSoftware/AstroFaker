from .astrofaker import AstroFaker
from gemini_instruments.gnirs.adclass import AstroDataGnirs

class AstroFakerGnirs(AstroFaker, AstroDataGnirs):
    def _add_required_phu_keywords(self):
        self.phu['IAA'] = 89.747  # Value seen in recent headers
