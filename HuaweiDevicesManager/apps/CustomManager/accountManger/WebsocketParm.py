
from apps.CustomManager.accountManger.VerifyParm import VerifyParm
class WebsocketParm(VerifyParm):


    def verifty_session_key(self,session_id):
        if not session_id:
            err_data={
                'type':"session_id",
                'message':"No get session_id"
            }
            self._getErrorRespones(self.CODE_F_QR,self.WEBSOCKET_CONNECT_FAILED,err_data)
