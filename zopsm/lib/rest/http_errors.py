from falcon import HTTPError, OptionalRepresentation
from falcon import status


class HTTPPaymentRequired(OptionalRepresentation, HTTPError):
    """402 Payment Required."""

    def __init__(self, **kwargs):
        super(HTTPPaymentRequired, self).__init__(status.HTTP_402, **kwargs)
