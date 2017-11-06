"""
Tests for bluew.responses.
"""


import unittest
from bluew.responses import Response, ResponseError,\
    validate_response, DataResponse


class ResponseTest(unittest.TestCase):
    """
    Tests for bluew.responses.Response class.
    """

    def test_constructs(self):
        """
        Test normal construction of a Response.
        :return: Assertion.
        """
        msg = 'works'
        has_succeeded = True
        blw_response = Response(has_succeeded, msg)
        self.assertEqual(blw_response.has_succeeded, True)
        self.assertEqual(blw_response.message, msg)

    def test_validates_wrong_types(self):
        """
        Test that Response(WITH_WRONG_TYPES...)
        raises exceptions.
        :return: Assertion.
        """

        wrong_msg = 1
        wrong_has_succeeded = 1

        correct_msg = "Works"
        correct_has_succeeded = False

        self.assertRaises(ResponseError, Response,
                          correct_has_succeeded,
                          wrong_msg,)

        self.assertRaises(ResponseError, Response,
                          wrong_has_succeeded,
                          correct_msg,)

    def test_validate_without_resp(self):
        """
        Test that validate_response(NOT_RESPONSE)
        raises exception.
        :return: Assertion.
        """

        resp = "Not Response"
        self.assertRaises(ResponseError, validate_response, resp)


class ResponseErrorTest(unittest.TestCase):
    """
    Tests for responses.ResponseError
    """

    def test_exception_to_str(self):
        """
        test __str__ function of ResponseError.
        """

        reason = 'meh'
        exp = ResponseError(reason)
        self.assertEqual(str(exp), reason)


class DataResponseTest(unittest.TestCase):
    """
    Tests for responses.DataResponse.
    """

    def test_constructs(self):
        """
        Test the normal Construction of a DataResponse.
        :return: Assertion.
        """

        some_data = ['some', 'data']
        has_succeeded = True
        message = 'works'
        data_response = DataResponse(some_data, has_succeeded, message)
        self.assertEqual(data_response.data, some_data)
