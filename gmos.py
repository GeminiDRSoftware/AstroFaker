from .astrofaker import AstroFaker
from gemini_instruments.gmos.adclass import AstroDataGmos

class AstroFakerGmos(AstroFaker, AstroDataGmos):
    pass
