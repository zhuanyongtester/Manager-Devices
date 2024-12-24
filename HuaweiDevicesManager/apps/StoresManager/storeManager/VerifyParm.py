from rest_framework import status, response
from rest_framework.views import APIView


class VerifyParm(APIView):
    def __init__(self, error_des=None):
        self.FAILED_400 = status.HTTP_400_BAD_REQUEST
        self.SUCCESS_201= status.HTTP_201_CREATED
        self.SUCCESS_200=status.HTTP_200_OK
        self.success_1000 = 1000
        self.FAILED_1001 = 1001
        self.FAILED_1002 = 1002
        self.FAILED_1003 = 1003
        self.FAILED_1004 = 1004
        self.FAILED_CREATE = "Create Store Failed"
        self.SUCCESS_CREATE="Store Create Success"
    def _getErrorRespones(self, result_code,message,err_data):
            response_data = {
                "statusCode": self.FAILED_400,
                "resultCode": result_code,
                "message": message,
                "errors": err_data or {}
            }
            return response_data
    def _getSuccessRespones(self,result_code,message,success_data):
        response_data = {
            "statusCode": self.SUCCESS_201,
            "resultCode": result_code,
            "message": message,
            "data": success_data or {}
        }
        return response_data

