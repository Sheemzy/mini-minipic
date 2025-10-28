"""Tools for CI."""

import math

from termcolor import cprint

from libminipic.exceptions import (
    IncorrectValueMiniPICError,
    ThresholdValueMiniPICError,
    ValueMiniPICError,
)


def success(message):
    """Print a success message."""
    cprint(message, "green", attrs=["bold"])


def failure(message):
    """Print a failure message."""
    cprint(message, "red", attrs=["bold"])


def evaluate(value, reference, threshold, operator="relative", txt=""):

    flag = False
    error_value = 0

    if operator == "<":

        error_value = math.fabs(value - threshold)

        flag = value > threshold

        if flag:
            raise ThresholdValueMiniPICError(
                f"{txt}: {value} > {threshold} with error {error_value}"
            )

        return

    if operator == "==":

        error_value = math.fabs(value - threshold)

        flag = error_value != 0

        if flag:
            raise IncorrectValueMiniPICError(
                f"{txt}: {value} not equal to {threshold} with value {error_value}"
            )

        return

    if operator == "relative":

        if reference == 0:
            raise ValueMiniPICError(
                "Can not evaluate a relative error with reference == 0"
            )

        error_value = math.fabs((value - reference) / reference)

        flag = error_value > threshold

        if flag:
            raise ThresholdValueMiniPICError(
                f"{txt}: {value} vs {reference}, with error {error_value} for relative threshold {threshold}"
            )

        return

    if operator == "absolute":

        error_value = math.fabs(value - reference)

        flag = error_value > threshold

        if flag:
            raise ThresholdValueMiniPICError(
                f"{txt}: {value} vs {reference} with error {error_value} for absolute threshold {threshold}"
            )

        return

    raise ValueMiniPICError(f"Operator not recognized {operator}")
