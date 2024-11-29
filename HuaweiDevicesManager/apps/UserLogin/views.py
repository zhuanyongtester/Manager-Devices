from django.shortcuts import render
from apps.UserLogin.Login.LoginBaseView import BaseView
# Create your views here.
class AdminLoginView(BaseView):
    def get(self,request):
        return render(request,"login/login_ui.html")
    def post(self,request):
        return  self.authAccount(request)

class AccountManagerView(BaseView):
    def get(self,request):

        jsonList=self.accountShow(request)
        return  render(request,'login/login.html',jsonList)

class outAccountView(BaseView):
    def post(self,request):
        return  self.autAccessToken(request)

