from graceful.errors import ValidationError


def tag_value_type_validator(tag_value_type):
    if tag_value_type not in ['int', 'float', 'str', None]:
        raise ValidationError(
            "Tag value type must be an int, float str or null!").as_bad_request()


def tag_type_validator(tag_type):
    if tag_type not in ['key', 'key-value', 'multi']:
        raise ValidationError(
            "Tag type must be key, key-value or multi!").as_bad_request()


def device_type_validator(device_type):
    if device_type not in ['android', 'ios']:
        raise ValidationError(
            "Device type must be android or ios!").as_bad_request()


def residents_validator(residents):
    """
    ```json
    "residents": {
                    "sets": {
                        "a": {"key": "age", "relation": ">", "value": "15", "intention": "target"},
                        "b": {"key": "eye-color", "relation": "=", "value": "blue", "intention": "target"}
                    },
                    "expression": "a n b"
                }
    ```
    Args:
        residents (dict):

    Returns:

    """
    if not (residents.get("sets") or residents.get("expression")):
        raise ValidationError(
            "Fields: sets and expression cannot be empty!").as_bad_request()


def intention_validator(residents):
    """
    ```json
    "residents": {
                    "sets": {
                        "a": {"key": "age", "relation": ">", "value": "15", "intention": "target"},
                        "b": {"key": "eye-color", "relation": "=", "value": "blue", "intention": "target"}
                    },
                    "expression": "a n b"
                }
    ```
    Args:
        residents (dict):

    """
    sets = residents.get("sets")
    for set in sets:
        if set.get("intention") not in ['client', 'target']:
            raise ValidationError(
                "Field: intention must be one of client or target!").as_bad_request()


def list_of_consumer_validator(consumer_list):
    if len(consumer_list) > 100:
        raise ValidationError("You can send maximum 100 consumer id in a request").as_bad_request()
