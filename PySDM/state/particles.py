"""
Created at 03.06.2019
"""

from typing import Dict

import numpy as np

from PySDM.attributes.attribute import Attribute


class Particles:

    def __init__(
            self, core,
            idx,
            extensive_attributes,
            extensive_keys: dict,
            intensive_attributes,
            intensive_keys: dict,
            cell_start,
            attributes: Dict[str, Attribute]
    ):
        self.core = core

        self.__n_sd = core.n_sd
        self.__valid_n_sd = core.n_sd
        self.healthy = True
        self.__healthy_memory = self.core.Storage.from_ndarray(np.full((1,), 1))
        self.__idx = idx
        self.__strides = self.core.Storage.from_ndarray(self.core.mesh.strides)

        self.extensive_attributes = extensive_attributes
        self.extensive_keys = extensive_keys
        self.intensive_attributes = intensive_attributes
        self.intensive_keys = intensive_keys

        self.cell_idx = self.core.Index.identity_index(len(cell_start) - 1)
        self.__cell_start = self.core.Storage.from_ndarray(cell_start)
        self.__cell_caretaker = self.core.bck.make_cell_caretaker(self.__idx, self.__cell_start,
                                                                  scheme=core.sorting_scheme)
        self.__sorted = False
        self.attributes = attributes

        self.recalculate_cell_id()

    @property
    def cell_start(self):
        if not self.__sorted:
            self.__sort_by_cell_id()
        return self.__cell_start

    @property
    def SD_num(self):
        assert self.healthy
        return len(self.__idx)

    def sanitize(self):
        if not self.healthy:
            self.__idx.length = self.__valid_n_sd
            self.__idx.remove_zeros(self['n'])
            self.__valid_n_sd = self.__idx.length
            self.healthy = True
            self.__healthy_memory[:] = 1
            self.__sorted = False

    def cut_working_length(self, length):
        assert length <= len(self.__idx)
        self.__idx.length = length

    def get_working_length(self):
        return len(self.__idx)

    def reset_working_length(self):
        self.__idx.length = self.__valid_n_sd

    def reset_cell_idx(self):
        self.cell_idx.reset_index()
        self.__sort_by_cell_id()

    def __getitem__(self, item):
        return self.attributes[item].get()

    def permutation(self, u01, local):
        if local:
            """
            apply Fisher-Yates algorithm per cell
            """
            self.__idx.shuffle(u01, parts=self.cell_start)
        else:
            """
            apply Fisher-Yates algorithm to all super-droplets
            """
            self.__idx.shuffle(u01)
            self.__sorted = False

    def __sort_by_cell_id(self):
        self.__cell_caretaker(self['cell id'], self.cell_idx, self.__cell_start, self.__idx, self.SD_num)
        self.__sorted = True

    def get_extensive_attrs(self):
        return self.extensive_attributes

    def get_intensive_attrs(self):
        return self.intensive_attributes

    def recalculate_cell_id(self):
        if 'cell origin' not in self.attributes:
            return
        else:
            self.core.bck.cell_id(self['cell id'], self['cell origin'], self.__strides)
            self.__sorted = False

    def sort_within_pair_by_attr(self, is_first_in_pair, attr_name):
        self.core.bck.sort_within_pair_by_attr(self.__idx, self.SD_num, is_first_in_pair, self[attr_name])

    def moments(self, moment_0, moments, specs: dict, attr_name='volume', attr_range=(-np.inf, np.inf)):
        specs_ex_idx, specs_ex_rank = [], []
        specs_in_idx, specs_in_rank = [], []
        for attr in specs:
            for rank in specs[attr]:
                if attr in self.extensive_keys:
                    specs_ex_idx.append(self.extensive_keys[attr])
                    specs_ex_rank.append(rank)
                if attr in self.intensive_keys:
                    specs_in_idx.append(self.intensive_keys[attr])
                    specs_in_rank.append(rank)
        specs_ex_idx = self.core.bck.Storage.from_ndarray(np.array(specs_ex_idx, dtype=int))
        specs_ex_rank = self.core.bck.Storage.from_ndarray(np.array(specs_ex_rank, dtype=float))
        specs_in_idx = self.core.bck.Storage.from_ndarray(np.array(specs_in_idx, dtype=int))
        specs_in_rank = self.core.bck.Storage.from_ndarray(np.array(specs_in_rank, dtype=float))
        self.core.bck.moments(moment_0,
                              moments,
                              self['n'],
                              self.extensive_attributes,
                              self.intensive_attributes,
                              self['cell id'],
                              self.__idx,
                              self.SD_num,
                              specs_ex_idx,
                              specs_ex_rank,
                              specs_in_idx,
                              specs_in_rank,
                              attr_range[0], attr_range[1],
                              self[attr_name])

    def coalescence(self, gamma, is_first_in_pair):
        self.core.bck.coalescence(n=self['n'],
                                  volume=self['volume'],
                                  idx=self.__idx,
                                  length=self.SD_num,
                                  intensive=self.get_intensive_attrs(),
                                  extensive=self.get_extensive_attrs(),
                                  gamma=gamma,
                                  healthy=self.__healthy_memory,
                                  is_first_in_pair=is_first_in_pair
                                  )
        self.healthy = bool(self.__healthy_memory)
        self.attributes['volume'].mark_updated()

    def adaptive_sdm_end(self, dt_left):
        return self.core.bck.adaptive_sdm_end(dt_left, self.core.particles.cell_start)

    def has_attribute(self, attr):
        return attr in self.attributes

    def remove_precipitated(self) -> float:
        res = self.core.bck.flag_precipitated(self['cell origin'], self['position in cell'],
                                              self['volume'], self['n'],
                                              self.__idx, self.SD_num, self.__healthy_memory)
        self.healthy = bool(self.__healthy_memory)
        return res
