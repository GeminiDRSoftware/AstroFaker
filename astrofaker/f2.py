#!/usr/bin/env python
"""
(some docstring here)
"""
from gemini_instruments.f2.adclass import AstroDataF2

from .astrofaker import AstroFaker, noslice


class AstroFakerF2(AstroFaker, AstroDataF2):
    """
    Class that mimics an AstroDataF2 object.
    """
    def _add_required_phu_keywords(self, mode):
        self.phu['IAA'] = 0.117  # Value seen in recent headers
        self.phu['CD3_3'] = 1

        if 'IMAGE' in mode:
            self.phu['GRISM'] = 'Open'

    @noslice
    def init_default_extensions(self):
        del self[:]
        self.add_extension(shape=(1, 2048, 2048), pixel_scale=0.179)
