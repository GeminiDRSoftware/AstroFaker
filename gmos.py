import numpy as np

from .astrofaker import AstroFaker, noslice
from gemini_instruments.gmos.adclass import AstroDataGmos
from gemini_instruments.gmos import lookup

BIAS_WIDTH = 32
# TODO: These are only good for Hamamatsu data
CRPIX2N = (2136.9534, 2136.0563, 2135.6827)
CRPIX2S = (2136.7972, 2137.6572, 2141.7487)

class AstroFakerGmos(AstroFaker, AstroDataGmos):
    def _add_required_phu_keywords(self, mode):
        # Values seen in recent headers
        north = self.instrument() == 'GMOS-N'
        self.phu['IAA'] = 179.901 if north else 359.9
        self.phu['DETTYPE'] = "S10892-N" if north else "S10892"
        if 'EEV' in mode:
            self.phu['DETID'] = ("EEV9273-16-03EEV9273-20-04EEV9273-20-03" if north
                                 else "EEV2037-06-03EEV8194-19-04EEV8261-07-04")
        elif 'e2v' in mode:
            if north:
                self.phu['DETID'] = "e2v 10031-23-05,10031-01-03,10031-18-04"
            else:
                raise ValueError("GMOS-S never had e2v CCDs!")
        else:
            self.phu['DETID'] = ("BI13-20-4k-1,BI12-09-4k-2,BI13-18-4k-2" if north
                                 else "BI5-36-4k-2,BI11-33-4k-1,BI12-34-4k-1")

        if 'IMAGE' in mode:
            self.phu['GRATING'] = 'MIRROR'

    @noslice
    def init_default_extensions(self, num_ext=12, binning=1, overscan=True):
        if num_ext != 12:
            raise NotImplementedError("Only tested for full array ROI")
        if binning not in (1, 2, 4):
            raise ValueError("Binning must be 1, 2, or 4")

        del self[:]
        shape = ((4224 if self.phu['DETID'].startswith('BI') else 4608) // binning,
                 512 // binning + (BIAS_WIDTH if overscan else 0))
        # If the overscan is present, assume it's raw data
        dtype = np.uint16 if overscan else np.float32
        pixel_scale = lookup.gmosPixelScales[self.instrument(),
                                             self.phu['DETTYPE']] * binning

        north = self.instrument() == 'GMOS-N'
        crpix1 = 3132.69 if north else 3133.5
        crpix1 = (crpix1 - 0.5) / binning + 0.5
        crpix2_list = CRPIX2N if north else CRPIX2S
        chip_gap = 67. if north else 61.

        extra_keywords = {'CRVAL1': self.phu['RA'], 'CRVAL2': self.phu['DEC'],
                          'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN',
                          'CCDSUM': '{} {}'.format(binning, binning)}
        for i in range(num_ext):
            ccd = i // 4
            crpix2 = (crpix2_list[ccd] - 0.5) / binning + 0.5

            detx1 = i * 512
            detx2 = detx1 + 512
            detsec = '[{}:{},1:4224]'.format(detx1+1, detx2)

            datx1 = BIAS_WIDTH if (overscan and i % 2 == 1) else 0
            datx2 = datx1 + 512 // binning
            datasec = '[{}:{},1:{}]'.format(datx1+1, datx2, shape[0])

            if overscan:
                biasx1 = BIAS_WIDTH - datx1
                biassec = '[{}:{},1:{}]'.format(biasx1+1, biasx1+BIAS_WIDTH, shape[0])
                extra_keywords[self._keyword_for('overscan_section')] = biassec

            arrx1 = detx1 % 2048
            arrx2 = arrx1 + 512
            arraysec = '[{}:{},1:4224]'.format(arrx1, arrx2)

            extra_keywords.update({self._keyword_for('detector_section'): detsec,
                              self._keyword_for('data_section'): datasec,
                              self._keyword_for('array_section'): arraysec,
                              'CRPIX1': crpix1+datx1, 'CRPIX2': crpix2})

            crpix1 -= (datx2-datx1)
            # This isn't entirely right but it'll do
            if i % 4 == 3:
                crpix1 -= chip_gap / binning

            self.add_extension(shape=shape, pixel_scale=pixel_scale,
                               dtype=dtype, extra_keywords=extra_keywords)
