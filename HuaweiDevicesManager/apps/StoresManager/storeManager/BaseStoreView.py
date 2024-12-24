from rest_framework import status, response

from apps.StoresManager.serializers import StoreSerializer
from apps.StoresManager.storeManager.VerifyParm import VerifyParm


class BaseStore(VerifyParm):
    def store_create_status(self,request):
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():

            serializer.save()  # 保存有效的数据
            return self._getSuccessRespones(self.success_1000,self.SUCCESS_CREATE,serializer.data)
        return self._getErrorRespones(self.FAILED_1001,self.FAILED_CREATE,serializer.errors)
