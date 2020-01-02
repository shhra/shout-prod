from rest_framework.exceptions import APIException

class ProfileDoesNotExist(APIException):
    status_code = 400
    default_detail = 'Oops! Who were you looking for?'
