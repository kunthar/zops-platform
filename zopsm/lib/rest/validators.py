from datetime import datetime
from graceful.errors import ValidationError
from zopsm.lib.settings import DATETIME_FORMAT


def datetime_field_format_validator(date_str):
    try:
        if date_str:
            datetime.strptime(date_str, DATETIME_FORMAT)
    except ValueError:
        raise ValidationError(
            "Datetime fields must be in {} format!".format(DATETIME_FORMAT)).as_bad_request()


def datetime_param_format_validator(date_str):
    try:
        datetime.strptime(date_str, DATETIME_FORMAT)
    except ValueError:
        raise ValidationError(
            "Datetime parameters must be in {} format!".format(DATETIME_FORMAT)).as_invalid_param()


def alphanumeric_field_validator(value):
    if value is not None and not value.isalnum():
        raise ValidationError(
            "Field must be alphanumeric!"
        ).as_bad_request()


def alphanumeric_param_validator(value):
    if not value.isalnum():
        raise ValidationError(
            "Parameter must be alphanumeric!"
        ).as_invalid_param(value)


def alphanumeric_list_of_strings_field_validator(value):
    for item in value:
        alphanumeric_field_validator(item)
