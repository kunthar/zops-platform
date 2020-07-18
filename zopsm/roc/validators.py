from graceful.errors import ValidationError


def channel_type_validator(val):
    if val not in ['public', 'private', 'invisible', 'public-announcement', 'private-announcement',
                   'invisible-announcement', 'all']:
        raise ValidationError(
            "Channel type must be one of 'public', 'public-group', 'private-group', "
            "'announcement', 'private'.")


def invite_approve_validator(val):
    if val not in ['approved', 'rejected', 'not_evaluated', None]:
        raise ValidationError(
            "approve must be one of approved, rejected, not_evaluated")


def behavioral_status_validator(val):
    if val not in ['online', 'idle', 'offline']:
        raise ValidationError(
            "behavioralStatus must be one of online, idle, or offline")


def manager_length_validator(val):
    if not len(val) > 0:
        raise ValidationError("Channel must include manager")


def subscribers_length_validator(val):
    if not len(val) > 0:
        raise ValidationError("Subscribers list must include at least one subscriber id")
