import re
from typing import Dict
from num2words import num2words

_comma_number_re = re.compile(r"([0-9][0-9\.]+[0-9])")
_decimal_number_re = re.compile(r"([0-9]+,[0-9]+)")
_currency_re = re.compile(r"(€|CHF|£)([0-9\.]*[0-9]+)")
_ordinal_re = re.compile(r"([0-9]+)\.")
_number_re = re.compile(r"-?[0-9]+")

def _remove_periods(m):
    return m.group(1).replace(".", "")

def _expand_decimal_point(m):
    return m.group(1).replace(",", " Komma ")

def __expand_currency(value: str, inflection: Dict[float, str]) -> str:
    parts = value.replace(".", "").split(",")
    if len(parts) > 2:
        return f"{value} {inflection[2]}"  # Unexpected format
    text = []
    integer = int(parts[0]) if parts[0] else 0
    if integer > 0:
        integer_unit = inflection.get(integer, inflection[2])
        text.append(f"{num2words(integer, lang='de')} {integer_unit}")
    fraction = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if fraction > 0:
        fraction_unit = inflection.get(fraction / 100, inflection[0.02])
        text.append(f"{num2words(fraction, lang='de')} {fraction_unit}")
    if len(text) == 0:
        return f"null {inflection[2]}"
    return " ".join(text)

def _expand_currency(m: "re.Match") -> str:
    currencies = {
        "€": {
            0.01: "Cent",
            0.02: "Cent",
            1: "Euro",
            2: "Euro",
        },
        "CHF": {
            0.01: "Rappen",
            0.02: "Rappen",
            1: "Schweizer Franken",
            2: "Schweizer Franken",
        },
        "£": {
            0.01: "Penny",
            0.02: "Pence",
            1: "Pfund",
            2: "Pfund",
        },
    }
    unit = m.group(1)
    currency = currencies.get(unit, {})
    value = m.group(2)
    return __expand_currency(value, currency)

def _expand_ordinal(m):
    number = int(m.group(1))
    return f"{num2words(number, to='ordinal', lang='de')}"

def _expand_number(m):
    num = int(m.group(0))
    return num2words(num, lang='de')

def normalize_numbers(text):
    text = re.sub(_comma_number_re, _remove_periods, text)
    text = re.sub(_currency_re, _expand_currency, text)
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    text = re.sub(_ordinal_re, _expand_ordinal, text)
    text = re.sub(_number_re, _expand_number, text)
    return text
