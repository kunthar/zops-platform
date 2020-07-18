from graceful.parameters import StringParam, BoolParam, IntParam

from zopsm.lib.rest.validators import datetime_param_format_validator, \
    alphanumeric_param_validator


class ZopsDateParam(StringParam):
    def __init__(
            self,
            details,
            label=None,
            required=False,
            default=None,
            many=False,
            validators=None
    ):
        if validators:
            validators.extend([datetime_param_format_validator])
        else:
            validators = [datetime_param_format_validator]

        super(ZopsDateParam, self).__init__(details, label, required, default, many, validators)


class ZopsStringParam(StringParam):
    """
    Wrapper for StringParam
    """


class ZopsAlphaNumericStringParam(ZopsStringParam):
    def __init__(
            self,
            details,
            label=None,
            required=False,
            default=None,
            many=False,
            validators=None
    ):
        if validators:
            validators.extend([alphanumeric_param_validator])
        else:
            validators = [alphanumeric_param_validator]

        super(ZopsAlphaNumericStringParam, self).__init__(details, label, required, default, many,
                                                          validators)


class ZopsBooleanParam(BoolParam):
    """
    Wrapper class for BoolParam
    """


class ZopsIntegerParam(IntParam):
    """
    Wrapper class for IntParam
    """