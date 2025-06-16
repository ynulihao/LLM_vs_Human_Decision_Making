from random import random
import re

def check_prob(prob, varname=None):
    if not isinstance(prob, int) and not isinstance(prob, float):
        if isinstance(prob, str):
            prob = float(prob)
        else:
            raise TypeError('Probability {}should be int or float.'.format(
                '' if varname is None else '"' + varname + '" '))
    if prob < 0 or prob > 1:
        raise ValueError('Probability {}should be in [0, 1].'.format(
            '' if varname is None else '"' + varname + '" '))
    return prob


def list_from_string(string: str, sep: str = ',', types=None, length=None, remove_space=True, varname=None):
    if remove_space: string = string.replace(' ', '')
    items = string.split(sep=sep)
    if length is None: length = len(items)
    if len(items) != length:
        raise ValueError('Number of items {}should be {} exactly.'.format(
            '' if varname is None else 'in "' + varname + '" ', length))
    if types is None:
        types = [str] * len(items)
    elif isinstance(types, list):
        if len(types) < length:
            types = types + [str] * (length - len(types))
    else:
        types = [types] * len(items)
    return [t(i) for i, t in zip(items, types)]


def random_float(lower, upper):
    if lower > upper: lower, upper = upper, lower
    return random() * (upper - lower) + lower


def clean_html(input_string):
    match = re.search(r'<!DOCTYPE html>\s*<html>.*</html>', input_string, re.DOTALL)
    # breakpoint()
    if match:
        return match.group()
    else:
        assert False, "No HTML content found"
