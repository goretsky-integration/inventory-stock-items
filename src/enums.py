from enum import StrEnum, auto

__all__ = ('CountryCode', 'MeasurementUnit', 'CategoryName')


class CountryCode(StrEnum):
    RU = auto()


class MeasurementUnit(StrEnum):
    QUANTITY = 'Quantity'
    KILOGRAM = 'Kilogram'
    LITER = 'Liter'
    METER = 'Meter'


class CategoryName(StrEnum):
    INGREDIENT = 'Ingredient'
    SEMI_FINISHED_PRODUCT = 'SemiFinishedProduct'
    FINISHED_PRODUCT = 'FinishedProduct'
    INVENTORY = 'Inventory'
    PACKING = 'Packing'
    CONSUMABLES = 'Consumables'
