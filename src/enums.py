from enum import StrEnum, auto

__all__ = ('CountryCode', 'MeasurementUnit')


class CountryCode(StrEnum):
    RU = auto()


class MeasurementUnit(StrEnum):
    QUANTITY = 'Quantity'
    KILOGRAM = 'Kilogram'
    LITER = 'Liter'
    METER = 'Meter'
