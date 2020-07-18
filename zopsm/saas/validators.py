from graceful.errors import ValidationError
import re


def is_service_code(val):
    """
    This method validates if service_code is one of "push", "roc", or "sms"
    else raises ValidationError.

    Args:
        val (string): service code name

    Raises:
        Validation error

    """
    if val not in ["push", "roc", "sms"]:
        raise ValidationError(
            "service_code must be one of push, roc, sms")


def id_validator(id):
    """
    Check the `id` is hex.
    Args:
        id:
    Returns:
        bool:
    """
    return re.fullmatch("[0-9a-fA-F]{32}", id or "") is not None


def phone_validator(phone_number):
    """
    `phone_number`s length is equal to 11?
    Args:
        phone_number:
    Raises:
        ValidationError
    """
    phone_format = re.compile('[0-9]{11}')
    if not bool(re.match(phone_format, phone_number)):
        raise ValidationError("Phone number is not proper format.").as_bad_request()


def email_validator(email):
    """
    Check email format with regex.
    Args:
        email:
    Returns:
        ValidationError
    """
    email_format = re.compile('[^@]+@[^@]+\.[^@]+')
    if not bool(re.match(email_format, email)):
        raise ValidationError("Email address is not valid.").as_bad_request()


def log_level_validator(val):
    if val not in ['WARNING', 'ERROR']:
        raise ValidationError(
            "logLevel must be one of WARNING or ERROR")
