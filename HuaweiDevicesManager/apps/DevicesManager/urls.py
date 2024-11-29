"""
URL configuration for HuaweiDevicesManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from apps.DevicesManager.views import BaseDevicesView,DeviceOutView,DevicesGetDataView,SubmitStockView,ShowSelectedDevicesView,ShowBorrowSelectedDevicesView,DeviceBorrowView,\
ShowBackelectedDevicesView,DeviceBackView,DownloadAllDevicesInfo,ReturnAllDevicesView,BorrowALLDevicesView,SearchBorrowUSerView,SearchJobNumInfoView,DownloadTemplateView
app_name = 'DevicesManager'
urlpatterns = [
    re_path(r'^$', BaseDevicesView.as_view(), name='index'),
    re_path(r'^out/', DeviceOutView.as_view(), name='out_Devices'),
    re_path(r'^borrow/', DeviceBorrowView.as_view(), name='borrow_Devices'),
    re_path(r'^back/', DeviceBackView.as_view(), name='back_Devices'),
    re_path(r'^upload/', DevicesGetDataView.as_view(), name='DevicesUpload'),
    re_path(r'^sub_form/', SubmitStockView.as_view(), name='submit_Form'),
    re_path(r'^download_excel/', DownloadAllDevicesInfo.as_view(), name='download_excel'),
    re_path(r'^back_all/', ReturnAllDevicesView.as_view(), name='back_all_devices'),
    re_path(r'^borrow_all/', BorrowALLDevicesView.as_view(), name='borrow_all_devices'),
    re_path(r'^search_user/', SearchBorrowUSerView.as_view(), name='search_user'),
    re_path(r'^show_selected_devices/', ShowSelectedDevicesView.as_view(), name='show_selected_devices'),
    re_path(r'^borrow_selected_devices/', ShowBorrowSelectedDevicesView.as_view(), name='borrow_selected_devices'),
    re_path(r'^back_selected_devices/', ShowBackelectedDevicesView.as_view(), name='back_selected_devices'),

    re_path(r'^search_job_name/', SearchJobNumInfoView.as_view(), name='search_job_name'),
    re_path(r'^download_template/', DownloadTemplateView.as_view(), name='download_template'),

]
