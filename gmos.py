from .astrofaker import AstroFaker
from gemini_instruments.gmos.adclass import AstroDataGmos

class AstroFakerGmos(AstroFaker, AstroDataGmos):
    def _add_required_phu_keywords(self, mode):
        # Values seen in recent headers
        self.phu['IAA'] = 179.901 if self.instrument() == 'GMOS-N' else 359.9

        if 'IMAGE' in mode:
            self.phu['GRATING'] = 'MIRROR'