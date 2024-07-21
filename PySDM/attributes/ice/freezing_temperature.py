"""
particle freezing temperature (assigned at initialisation, modified through collisions only,
 used in singular regime)
"""

from PySDM.attributes.impl import MaximumAttribute, register_attribute


@register_attribute()
class FreezingTemperature(MaximumAttribute):
    def __init__(self, builder):
        super().__init__(builder, name="freezing temperature")
