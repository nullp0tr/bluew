"""
bluew.response
~~~~~~~~~~~~~~

This module provides Response objects, to be returned
by the API.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


class Response:
    """A bluew Response object.

    Response is gonna be passed between,
    engine and bluew, and bluew and
    other programs.

    """

    def __init__(self, has_succeeded, message):
        self.has_succeeded = has_succeeded
        self.message = message
        validate_response(self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            same_has_succeeded = other.has_succeeded == self.has_succeeded
            same_message = other.message == self.message
            if same_has_succeeded and same_message:
                return True
        return False

    @staticmethod
    def donothing():
        """Just shutting pylint up"""
        pass

    @staticmethod
    def donothingg():
        """Just shutting pylint up"""
        pass


def validate_response(blw_response):
    """
    Validate a Response.
    :param blw_response: A BluewResponseInstance.
    :return: return if valid, raise exception if not.
    """

    if not isinstance(blw_response, Response):
        raise ResponseError(
            ResponseError.OBJECT_IS_NOT_BLUEW_RESPONSE)

    elif not isinstance(blw_response.has_succeeded, bool):
        raise ResponseError(
            ResponseError.HAS_SUCCEEDED_WRONG_TYPE)

    elif not isinstance(blw_response.message, str):
        raise ResponseError(
            ResponseError.MESSAGE_WRONG_TYPE)

    return


class ResponseError(BaseException):
    """
    Exception thrown out when an invalid response is constucted.
    """

    OBJECT_IS_NOT_BLUEW_RESPONSE = 'passed object is not Response'
    HAS_SUCCEEDED_WRONG_TYPE = "has_succeeded must be a bool"
    MESSAGE_WRONG_TYPE = "message must be a string"

    def __init__(self, reason, *args):
        """
        :param reason: Why Response is invalid.
        """

        super().__init__(*args)
        self.reason = reason

    def __str__(self):
        return self.reason


class DataResponse(Response):
    """
    This response class would be used,
    when returning BluewResponses from
    commands that return data.
    """

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data


class ConnectSucceededResponse(Response):
    """Return this when connection is established"""

    def __init__(self):
        super().__init__(True, 'Successfully connected')


class ConnectFailedResponse(Response):
    """Return this when can't connect"""

    def __init__(self):
        super().__init__(False, 'Failed to connect')


class ConnectedAlreadyResponse(Response):
    """Return this when device was already connected"""

    def __init__(self):
        super().__init__(True, 'Already connected')


class DisconnectSucceededResponse(Response):
    """Return this when successfully disconnected"""

    def __init__(self):
        super().__init__(True, 'Successfully disconnected')


class DisconnectFailedResponse(Response):
    """Return this when can't disconnect"""

    def __init__(self):
        super().__init__(False, 'Failed to disconnect')


class DisconnectedAlreadyResponse(Response):
    """Return this when it was already disconnected"""

    def __init__(self):
        super().__init__(True, 'Already disconnected')


class PairSucceededResponse(Response):
    """Return this when successfully paired"""

    def __init__(self):
        super().__init__(True, 'Successfully paired')


class PairFailedResponse(Response):
    """Return this when can't pair."""

    def __init__(self):
        super().__init__(False, 'Failed to pair')


class PairedAlreadyResponse(Response):
    """Return this when it was already paired."""

    def __init__(self):
        super().__init__(True, 'Already paired')


class TrustSucceededResponse(Response):
    """Return this when successfully trusted."""

    def __init__(self):
        super().__init__(True, 'Successfully trusted')


class TrustFailedResponse(Response):
    """Return this when can't trust. (FML)"""

    def __init__(self):
        super().__init__(False, 'Failed to trust')


class TrustedAlreadyResponse(Response):
    """Return this when it was already trusted."""

    def __init__(self):
        super().__init__(True, 'Already trusted')


class WriteSucceededResponse(Response):
    """Return this when write is successful."""

    def __init__(self):
        super().__init__(True, 'Successfully written')


class WriteFailedResponse(Response):
    """Return this when write fails."""

    def __init__(self):
        super().__init__(False, 'Failed to write')


class ReadSucceededResponse(DataResponse):
    """Return this when read is successful."""

    def __init__(self, data):
        super().__init__(data, has_succeeded=True, message='Successfully read')


class ReadFailedResponse(Response):
    """Return this when read fails."""

    def __init__(self):
        super().__init__(False, 'Failed to read')


class InfoSucceededResponse(DataResponse):
    """Return this when info is found."""

    def __init__(self, data):
        super().__init__(data, True, message='Successfully found info')


class InfoFailedResponse(Response):
    """Return this when no info is found."""

    def __init__(self):
        super().__init__(False, 'Failed to find info')
