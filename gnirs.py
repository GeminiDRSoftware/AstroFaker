from .astrofaker import AstroFaker
from gemini_instruments.gnirs.adclass import AstroDataGnirs

class AstroFakerGnirs(AstroFaker, AstroDataGnirs):
    pass
