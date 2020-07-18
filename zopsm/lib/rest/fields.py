import json

from graceful.fields import StringField, BoolField, BaseField, IntField

from zopsm.lib.rest.validators import datetime_field_format_validator, \
    alphanumeric_field_validator, alphanumeric_list_of_strings_field_validator


class ZopsStringField(StringField):
    """
    Wrapper class for the string field.
    """
    def from_representation(self, data):
        """Convert representation value to ``str`` if it is not None."""
        return str(data) if data is not None else None


class ZopsAlphaNumericStringField(ZopsStringField):
    """
    Wrapper class to make sure the accepted string fields are always alphanumeric by specifying
    custom validators in constructor.
    """
    def __init__(
            self,
            details,
            label=None,
            source=None,
            validators=None,
            many=False,
            read_only=False,
            write_only=False,
    ):
        if validators:
            validators.extend([alphanumeric_field_validator])
        else:
            validators = [alphanumeric_field_validator]
        super(ZopsAlphaNumericStringField, self).__init__(
            details, label, source, validators, many, read_only, write_only
        )


class ZopsDatetimeField(ZopsStringField):
    """
    Wrapper class to inspect the formats the datetime strings with custom validators which
    specified in the constructor.
    """
    def __init__(
            self,
            details,
            label=None,
            source=None,
            validators=None,
            many=False,
            read_only=False,
            write_only=False,
    ):
        if validators:
            validators.extend([datetime_field_format_validator])
        else:
            validators = [datetime_field_format_validator]
        super(ZopsDatetimeField, self).__init__(
            details, label, source, validators, many, read_only, write_only
        )


class ZopsBooleanField(BoolField):
    """
    Wrapper class for the BoolField of graceful.
    """


class ZopsListOfStringsField(BaseField):
    """
    Represents the list of strings type field in our api.
    """
    def from_representation(self, data):
        return data

    def to_representation(self, value):
        return value


class ZopsListOfAlphaNumericStringsField(ZopsListOfStringsField):
    def __init__(
            self,
            details,
            label=None,
            source=None,
            validators=None,
            many=False,
            read_only=False,
            write_only=False,
    ):
        if validators:
            validators.extend([alphanumeric_list_of_strings_field_validator])
        else:
            validators = [alphanumeric_list_of_strings_field_validator]
        super(ZopsListOfAlphaNumericStringsField, self).__init__(
            details, label, source, validators, many, read_only, write_only
        )


class ZopsJsonObjectField(BaseField):
    """
    Wrapper class for Json objects
    """
    def from_representation(self, data):
        return data

    def to_representation(self, value):
        return value


class ZopsIntegerField(IntField):
    """
    Wrapper class for IntField
    """