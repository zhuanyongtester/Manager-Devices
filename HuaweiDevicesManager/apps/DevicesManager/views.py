from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from apps.DevicesManager.Base.BaseView import BaseView
import json
# Create your views here.
class BaseDevicesView(BaseView):
    def get(self,request):
        work_name=self.getAdminName(request)
        devicesList=self.showDevicesInof()
        return  render (request, "index.html",{"work_name":work_name,"devices":devicesList})
    def post(self,request):
        devicesList=self.searchDevicesinfo(request)
        work_name = self.getAdminName(request)
        return render(request, "index.html", {"work_name":work_name,"devices": devicesList})




class DeviceOutView(BaseView):
    def get(self,request):
        device_ids = request.GET.get('id', '').split(',')
        if not device_ids:
            return JsonResponse({"success": False, "message": "请至少选择一个设备。"})
        # 保存选择的 IMEI/SN 到 session
        request.session['selected_device_ids'] = device_ids
        # 返回包含跳转 URL 的响应
        return JsonResponse({"success": True, "redirect_url": '/auth/show_selected_devices/'})

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        description = data.get('description', '')
        imei_sn_list = data.get('imei_sn_list', [])
        out_status,messages=self.outStock_updateStatus(imei_sn_list, "bob", description)
        if out_status:
            return JsonResponse({'success': out_status, 'message': '设备已成功出库'})
        else:
            return JsonResponse({'success': out_status, 'message': messages})

        # 出库的逻辑

class DeviceBorrowView(BaseView):
    def get(self,request):
        device_ids = request.GET.get('id', '').split(',')
        if not device_ids:
            return JsonResponse({"success": False, "message": "请至少选择一个设备。"})
        # 保存选择的 IMEI/SN 到 session
        request.session['selected_device_ids'] = device_ids
        # 返回包含跳转 URL 的响应
        return JsonResponse({"success": True, "redirect_url": '/auth/borrow_selected_devices/'})
    def post(self, request):
        person = self.getAdminName(request)
        borrow_status, messages = self.borrowSave(request,person)
        if borrow_status:
            return JsonResponse({'success': borrow_status, 'message': messages})
        else:
            return JsonResponse({'success': borrow_status, 'message': messages})

class DeviceBackView(BaseView):
    def get(self,request):
        device_ids = request.GET.get('id', '').split(',')
        if not device_ids:
            return JsonResponse({"success": False, "message": "请至少选择一个设备。"})
        # 保存选择的 IMEI/SN 到 session
        request.session['selected_device_ids'] = device_ids
        # 返回包含跳转 URL 的响应
        return JsonResponse({"success": True, "redirect_url": '/auth/back_selected_devices/'})
    def post(self, request):
        work_name = self.getAdminName(request)
        borrow_status, messages = self.viewBorrowStatus(request,work_name)
        if borrow_status:
            return JsonResponse({'success': borrow_status, 'message': messages})
        else:
            return JsonResponse({'success': borrow_status, 'message': messages})

class ShowSelectedDevicesView(BaseView):
    def get(self, request):
        # 从 session 获取选中的 IMEI/SN
        work_name = self.getAdminName(request)
        device_ids = request.session.get('selected_device_ids', [])
        if isinstance(device_ids, str):
            device_ids = device_ids.split(',')

        # 获取可出库的设备和不可出库的设备
        devices, unavailable_devices = self.outStockShow(device_ids)

        return render(request, 'out_devices.html', {"work_name":work_name,"devices": devices,"outName":work_name})
class ShowBorrowSelectedDevicesView(BaseView):
    def get(self, request):
        # 从 session 获取选中的 IMEI/SN
        device_ids = request.session.get('selected_device_ids', [])
        if isinstance(device_ids, str):
            device_ids = device_ids.split(',')

        # 获取可出库的设备和不可出库的设备
        devices, unavailable_devices = self.outStockShow(device_ids)
        work_name = self.getAdminName(request)
        return render(request, 'borrow_devices.html', {"work_name":work_name,"devices": devices,"borrow_admin_Name":work_name})
class ShowBackelectedDevicesView(BaseView):
    def get(self, request):
        person=self.getAdminName(request)
        # 从 session 获取选中的 IMEI/SN
        device_ids = request.session.get('selected_device_ids', [])
        if isinstance(device_ids, str):
            device_ids = device_ids.split(',')
        print(device_ids)
        # 获取可出库的设备和不可出库的设备
        view_devices= self.returnViewDevice(device_ids,person)

        return render(request, 'device_info_view.html',view_devices )



class SubmitStockView(BaseView):
    def get(self,request):
        person= self.getAdminName(request)
        return  render (request, "stock_devices.html",{"work_name":person,"stockName":person})
    def post(self,request):

        person = self.getAdminName(request)
        status, message = self.stockSave(request,person)
        if status:
            return redirect('/auth/')
        else:
            messages.error(request, message)
            return render(request, 'stock_devices.html', {'stockName': person})  # 保持原有的上下文



class DevicesGetDataView(BaseView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        print("HuaweiHealthNotification view loaded")
        return super().dispatch(*args, **kwargs)
    def post(self,request):
        try:
            data = json.loads(request.body)
            received_data = data.get('data', '')
            # 处理接收到的数据
            print(f"Received data: {received_data}")
            return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

class DownloadAllDevicesInfo(BaseView):
    def get(self,request):
        # response = StreamingHttpResponse(self.file_iterator(request))
        # response['Content-Type'] = 'application/vnd.ms-excel'
        # response['Content-Disposition'] = 'attachment;filename=' + "template.xlsx"
        response=self.queryAllDevicesData()
        return response


class ReturnAllDevicesView(BaseView):
    def get(self,request,*args, **kwargs):
        work_name = self.getAdminName(request)
        person=request.GET.get('job_number')
        context =self.search_borrow_person(person)
        context["work_name"]=work_name

        return  render(request, 'batches_back_devices.html' ,context )


class BorrowALLDevicesView(BaseView):
    def get(self,request):
        work_name = self.getAdminName(request)

        context=self.search_can_borrow()
        context["work_name"]=work_name
        context["borrow_admin_Name"]=work_name
        return  render(request, 'batches_borrow_devices.html'  ,context)

class SearchBorrowUSerView(BaseView):
    def get(self,request):
        name = request.GET.get('job_number_or_name', '')
        return self.search_borrow_user(name)

class SearchJobNumInfoView(BaseView):
    def post(self,request):
        return self.searchBorrowerInfo(request)



class DownloadTemplateView(BaseView):
    def get(self,request):
        response = StreamingHttpResponse(self.file_iterator(request))
        response['Content-Type'] = 'application/vnd.ms-excel'
        response['Content-Disposition'] = 'attachment;filename=' + "template.xlsx"
        return response

    def post(self, request):
        work_name = self.getAdminName(request)
        return self.uploadExcel(request,work_name)



