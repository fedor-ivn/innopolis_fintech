from eth_utils.units import units as default_units
from web3 import Web3

UNITS_ALIASES = {
    'poa': 'ether',
}


def check_unit_alias(unit):
    if unit in default_units:
        return unit
    elif unit in UNITS_ALIASES:
        return UNITS_ALIASES[unit]
    else:
        raise ValueError(
            "Unknown unit.  Must be one of {0} or {1}".format(
                "/".join(default_units.keys()),
                "/".join(UNITS_ALIASES.keys())
            )
        )


def get_unit(amount):
    """Масштабирование суммы.
    Минимально возможное нормализованное значение, чья целая часть больше ноля
    """
    val = {
        0: 'wei',
        3: 'kwei',
        6: 'mwei',
        9: 'gwei',
        12: 'szabo',
        15: 'finney',
        18: 'poa'
    }
    for power in reversed(list(val.keys())):
        if amount >= 10 ** power:
            return val[power]


def get_scaled_amount(amount):
    unit = get_unit(amount)
    unitized_amount = round(Web3.fromWei(amount, check_unit_alias(unit)), 6)
    return unitized_amount, unit
