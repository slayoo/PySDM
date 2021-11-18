"""
P(x) = exp(-x / lambda)
Created at 13.05.2021 by edejong
"""

import numpy as np


class ExponFrag:

    def __init__(self, scale):
        self.core = None
        self.scale = scale
        
    def register(self, builder):
        self.core = builder.core
        builder.request_attribute('radius')
        self.max_size = self.core.PairwiseStorage.empty(self.core.n_sd // 2, dtype=float)
        self.frag_size = self.core.PairwiseStorage.empty(self.core.n_sd // 2, dtype=float)

    def __call__(self, output, u01, is_first_in_pair):
        self.max_size.max(self.core.particles['radius'],is_first_in_pair)
        self.core.backend.exp_fragmentation(output, self.scale, self.frag_size,
            self.max_size, u01)
        