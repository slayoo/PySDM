"""
Created at 11.05.2020
"""

from PySDM.attributes.extensive_attribute import ExtensiveAttribute


class DryVolume(ExtensiveAttribute):

    def __init__(self, builder):
        super().__init__(builder, name='dry volume')