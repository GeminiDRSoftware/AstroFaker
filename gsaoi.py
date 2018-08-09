from .astrofaker import AstroFaker
from gemini_instruments.gsaoi.adclass import AstroDataGsaoi

class AstroFakerGsaoi(AstroFaker, AstroDataGsaoi):
    pass
