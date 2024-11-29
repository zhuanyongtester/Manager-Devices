import json
from datetime import datetime, timedelta
import pandas as pd
import openpyxl
from MySQLdb import IntegrityError, OperationalError
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from HuaweiDevicesManager import settings
from apps.DevicesManager.models import HuaweiDevice,BorrowInfo,StockInInfo,StockOutInfo,BorrowerInfo
from django.db.models import Q, Count  # 导入 Q 对象以支持复杂查询
from apps.UserLogin.models import Token,CustomUser
class BaseView(View):
    def __init__(self, code=None, error=None, state=None, callback_url=None):
        self.error = error
        self.state = state
        self.callback_url = callback_url

    def dispatch(self, request, *args, **kwargs):
        if not self.check_auth(request):
            return redirect('/')  # Redirect to your login page
        return super().dispatch(request, *args, **kwargs)
    def check_auth(self, request):
        work_name = request.session.get('work_name')
        access_token = request.session.get('access_token')

        if not work_name or not access_token:
            return False  # 表示未认证

        # 假设您有 Token 模型来存储 token 及其有效性
        try:
            token = Token.objects.get(work_person__work_number=work_name, access_token=access_token)
            if token.is_expired():  # 假设你有一个方法检查 token 是否过期
                return False
        except Token.DoesNotExist:
            return False  # token 不存在，表示未认证

        return True  # 表示已认证

    def getAdminName(self,request):
        try:
            work_name = request.session.get('work_name')  # 获取 URL 中的 work_name
            user = CustomUser.objects.get(work_number=work_name)  # 根据 work_number 查询用户
            return user.work_name  # 返回工作名称
        except CustomUser.DoesNotExist:
            return None  # 用户不存在时返回 None

    def is_valid_job_number(self, job_number):
        """
        检查工号签名是否符合要求：
        - 工号最多9位
        - 工号包含字母和数字：其中数字部分不少于6位
        - 工号只包含数字：长度为6到9位

        参数:
        job_number (str): 输入的工号字符串

        返回值:
        tuple: (bool, str) - 第一个值表示是否符合要求，第二个值为错误消息或空字符串
        """

        status = True
        message = ""

        # 检查工号长度是否超过9位
        if len(job_number) > 9:
            status = False
            message = "工号不能超过9位数"
            return status, message

        # 检查工号是否包含字母和数字混合的情况
        if any(char.isalpha() for char in job_number) and any(char.isdigit() for char in job_number):
            # 提取工号中的数字部分并检查是否不少于6位
            numeric_part = ''.join(filter(str.isdigit, job_number))
            if len(numeric_part) < 6:
                status = False
                message = "含字母和数字的工号，其数字部分不少于6位"
                return status, message

        # 检查纯数字的情况，长度必须在6到9位之间
        if job_number.isdigit():
            if not (6 <= len(job_number) <= 9):
                status = False
                message = "纯数字工号长度必须在6到9位之间"
                return status, message

        # 如果既不符合字母和数字混合、也不符合纯数字的规则
        return status, message


    def getStrParam(self, request, paramName):
        if request.method == 'GET':

            value = request.GET.get(paramName)
            if value is None:
                value = ''
            return value
        elif request.method == 'POST':

            value = request.POST.get(paramName)

            if value is None:
                value = ''
            return value
    def primaryDevicesExist(self, imei_sn):  # 判断主键是否存在
        try:
            HuaweiDevice.objects.get(imei_sn=imei_sn.strip())
            print("Exist")
            return True
        except HuaweiDevice.DoesNotExist:
            print("NoExist" + str(HuaweiDevice.DoesNotExist))
            return False

    def render_error_message(self, request, message):
        return render(request, 'stock_devices.html', {'error_message': message})

    def showDevicesInof(self):
        devicesList=[]
        devices = HuaweiDevice.objects.all()

        i = 1
        for device in devices:
            if device.status != 3:  # 排除出库状态的设备
                # 初始化holder_name和borrow_count
                holder_name = '无'  # 默认无持有人
                borrow_count = 0  # 默认借用次数为0

                # 获取借用次数
                borrow_count = BorrowInfo.objects.filter(device=device).count()

                # 获取最新借用记录
                latest_borrow_info = device.borrowinfo_set.order_by('-borrow_time').first()

                if latest_borrow_info:  # 如果有借用记录
                    holder_name = latest_borrow_info.borrow_operator  # 获取借用人的姓名
                else:
                    # 如果没有借用记录，则获取入库信息的负责人
                    try:
                        latest_stock_in = StockInInfo.objects.filter(device=device).latest('stock_in_time')
                        holder_name = latest_stock_in.stock_in_person  # 获取持有人姓名
                    except StockInInfo.DoesNotExist:
                        holder_name = '无'  # 如果没有找到入库信息

                # 准备展示信息
                deviceInfo = {
                    'num': i,
                    'device_name': device.model_name,
                    'device_color': device.color,
                    'status': device.get_status_display(),
                    'person': holder_name,
                    'times': borrow_count,
                    'imei_sn': device.imei_sn
                }
                devicesList.append(deviceInfo)
                i += 1
        devicesList

        return devicesList

    def stockSave(self, request,person):
        message = ''
        imei_sn = self.getStrParam(request, "imei").strip()
        model_name = self.getStrParam(request, "model_name").strip()
        model_number = self.getStrParam(request, "model_number").strip()
        color = self.getStrParam(request, "color").strip()
        description = self.getStrParam(request, "description").strip()

        # 查找设备
        device = HuaweiDevice.objects.filter(imei_sn=imei_sn).first()

        if device:
            # 如果设备存在，检查状态
            if device.status in [0, 1, 2]:
                message = "设备已在库，无法再次入库。"
                print(message)
                return False, message  # 返回设备已存在的信息
            elif device.status == 3:
                # 如果设备状态为3，更新设备信息
                if description:  # 检查 description 是否有内容
                    if len(description) > 200:  # 加入最大长度限制
                        return self.render_error_message(request, "Description 不能超过200个字符！")

                device.model_name = model_name  # 更新设备名称
                device.model_num = model_number  # 更新设备编号
                device.color = color  # 更新设备颜色
                device.status = 0  # 更新设备状态为 0
                try:
                    device.save()  # 保存更新后的设备
                    runStatus = True
                    message = "设备信息更新成功！"
                    print("设备信息更新成功！")
                except OperationalError:
                    message = "数据库操作失败，请检查数据库连接！"
                    print("数据库操作失败，请检查数据库连接！")
                    runStatus = False
                except Exception as e:
                    message = f"设备更新失败：{e}"
                    print(f"设备更新失败：{e}")
                    runStatus = False
        else:
            # 如果设备不存在，创建新的设备记录
            if description:  # 检查 description 是否有内容
                if len(description) > 200:  # 加入最大长度限制
                    return self.render_error_message(request, "Description 不能超过200个字符！")

            device = HuaweiDevice(
                imei_sn=imei_sn,  # IMEI/SN
                model_name=model_name,  # 设备名称
                model_num=model_number,  # 设备编号
                color=color,  # 设备颜色
                status=0  # 初始状态为在库
            )
            stock_in_info = StockInInfo(
                device=device,  # 关联的设备
                stock_in_person=person,  # 入库人
                stock_Remark=description  # 入库备注
            )

            try:
                device.save()
                stock_in_info.save()
                runStatus = True
                message = "设备保存成功！"
                print("设备保存成功！")
            except OperationalError:
                message = "数据库操作失败，请检查数据库连接！"
                print("数据库操作失败，请检查数据库连接！")
                runStatus = False
            except Exception as e:
                message = f"设备保存失败：{e}"
                print(f"设备保存失败：{e}")
                runStatus = False

        return runStatus, message

    from django.db import transaction, IntegrityError
    def viewBorrowStatus(self, request,person):
        back_operator=person
        from django.utils import timezone
        view_status = False
        view_status = True  # 假设所有操作成功
        messages = []  # 用于收集消息
        data = json.loads(request.body.decode('utf-8'))
        imei_sn_list = data.get('imei_sn_list', '')
        sign_name = data.get('sign_name', '').strip()
        print(f"获取的值：{imei_sn_list} - {sign_name}")

        # 检查imei_sn_list是否为空
        if not imei_sn_list:
            return False, "请选择设备后再执行归还操作"
        status,meesages=self.is_valid_job_number(sign_name)
        if not status:
            return False,meesages


        # 分割传入的 IMEI/SN 列表
        imei_sn_list = [imei.strip() for imei in imei_sn_list.split(',') if imei.strip()]

        # 开始数据库事务
        with transaction.atomic():
            for imei_sn in imei_sn_list:
                try:
                    # 获取设备对象
                    device = HuaweiDevice.objects.get(imei_sn=imei_sn)

                    # 获取该设备的最后一条借用记录
                    borrow_info = BorrowInfo.objects.filter(device=device).order_by('-borrow_time').first()

                    # 检查设备的状态
                    if device.status in [0, 1]:
                        messages.append(f"设备 {imei_sn} 不可归还，因为设备状态为不可用或已借出")
                        view_status = False
                        continue  # 处理下一个设备
                    print("back ")
                    if borrow_info and borrow_info.back_time is None:

                        # 检查借用用户是否是最后一个借用人
                        if sign_name in borrow_info.borrower.job_number:
                            # 设置归还时间
                            borrow_info.back_time = timezone.now()
                            borrow_info.borrow_operator = back_operator
                            borrow_info.save()  # 保存更新借用记录

                            # 更新设备状态为“可用”(假设可用状态为 1)
                            device.status = 1
                            device.save()
                            messages.append(f"设备 {imei_sn} 归还成功")
                        else:
                            # 非最后一个借用人，不能归还
                            messages.append(f"您不是最后一个借用 {imei_sn} 设备的人，无法归还")
                            view_status = False
                    else:
                        # 没有借用记录或设备已经归还
                        messages.append(f"未找到 {imei_sn} 的有效借用记录或设备已被归还")
                        view_status = False

                except HuaweiDevice.DoesNotExist:
                    # 如果设备不存在
                    messages.append(f"设备 {imei_sn} 不存在")
                    view_status = False

        return view_status, "; ".join(messages)

    def borrowSave(self, request,person):
        borrow_status = False
        data = json.loads(request.body.decode('utf-8'))
        borrow_operator = person  # 操作人
        # 获取请求中的数据
        borrow_job_number = data.get('borrow_job_number', '').strip()
        borrowName = data.get('borrowName', '').strip()
        borrow_department = data.get('borrow_department', '').strip()
        borrow_days = data.get('borrow_days', '')
        description = data.get('borrow_description', '')
        imei_sn_list = data.get('imei_sn_list', [])
        print(borrow_job_number)
        status,messagess=self.is_valid_job_number(borrow_job_number)
        if not status:
            return False,messagess
        if not borrow_job_number:
            return False, "借用人工号不能为空"

        # 验证数据
        if len(imei_sn_list) == 0:
            return False, "设备至少选一台！"

        try:
            borrow_days = int(borrow_days)
            if borrow_days <= 0:
                return False, "借机天数必须为正整数"
        except ValueError:
            return False, "借机天数必须为整数"

        # 获取设备并检查是否可借用
        existing_devices = HuaweiDevice.objects.filter(imei_sn__in=imei_sn_list)
        if not existing_devices.exists():
            return False, "所选设备不存在或不可借用"

        unavailable_devices = existing_devices.filter(status__in=[2, 3])
        if unavailable_devices.exists():
            return False, f"以下设备不可借用：{', '.join([d.imei_sn for d in unavailable_devices])}"

        # 获取借用人信息，若不存在则创建新的借用人信息
        try:
            borrower_info, created = BorrowerInfo.objects.get_or_create(
                job_number=borrow_job_number,
                defaults={

                    'name': borrowName,
                    'department': borrow_department
                }
            )
            if created:
                print(
                    f"新借用人信息已创建：工号 {borrower_info.job_number}, 姓名 {borrower_info.name}, 部门 {borrower_info.department}")
        except Exception as e:
            return False, f"借用人信息处理失败：{str(e)}"

        try:
            # 开始一个数据库事务
            with transaction.atomic():
                # 设备状态更新为 "借用中" (status=2)
                updated_count = existing_devices.update(status=2)
                if updated_count != len(imei_sn_list):
                    # 如果有设备未能成功更新，抛出异常进行回滚
                    raise IntegrityError("部分设备状态更新失败")

                # 记录借机信息
                borrow_out_records = []
                for device in existing_devices:
                    borrow_out_records.append(BorrowInfo(
                        device=device,
                        borrower=borrower_info,  # 关联借用人
                        borrow_days=borrow_days,
                        borrow_reason=description,
                        borrow_operator=borrow_operator
                    ))

                # 使用 bulk_create 提高性能，插入 BorrowInfo 数据
                BorrowInfo.objects.bulk_create(borrow_out_records)

                # 设备借机成功
                borrow_status = True
                message = "设备借机成功"

        except IntegrityError as e:
            # 捕捉数据库的唯一性约束异常或事务性问题
            borrow_status = False
            message = f"借机操作失败：{str(e)}"
        except Exception as e:
            # 捕捉其他可能的异常
            borrow_status = False
            message = f"借机操作过程中发生错误：{str(e)}"

        return borrow_status, message

    def outStockShow(self,devicesList):
        devices=[]
        unavailable_devices = []
        if len(devicesList)!=0:
            # 过滤设备，排除状态为 2（借用中）和 3（出库）的设备
            available_devices = HuaweiDevice.objects.filter(imei_sn__in=devicesList).exclude(status__in=[2, 3])
            # 获取状态为 2 和 3 的设备，用于展示
            unavailable_devices_list = HuaweiDevice.objects.filter(imei_sn__in=devicesList, status__in=[2, 3])
            num = 1

            # 构建可用设备的展示列表
            for device in available_devices:
                deviceInfo = {
                    "num": num,
                    "device_name": device.model_name,
                    "device_color": device.color,
                    "imei_sn": device.imei_sn
                }
                devices.append(deviceInfo)
                num += 1

            # 构建不可用设备的展示列表（状态为 2 和 3）
            for device in unavailable_devices_list:
                deviceInfo = {
                    "num": num,
                    "device_name": device.model_name,
                    "device_color": device.color,
                    "imei_sn": device.imei_sn,
                    "status": device.get_status_display()  # 添加状态显示
                }
                unavailable_devices.append(deviceInfo)
                num += 1


        return devices,unavailable_devices
    def timeChangeUTC(self,use_time):
        if use_time is not None:

            borrow_time_beijing = use_time + timedelta(hours=8)
        else:
            borrow_time_beijing = None  # 或者其他的默认值，例如设置为当前时间
        return borrow_time_beijing
    def returnViewDevice(self, devicesList,adminName):
        if len(devicesList) == 1:
            deviceId = devicesList[0]

            # 获取设备对象，若不存在则返回404
            device = get_object_or_404(HuaweiDevice, imei_sn=deviceId)

            # 获取设备的当前状态
            view_status = device.get_status_display()

            # 获取与该设备相关的所有借用记录
            borrow_records = BorrowInfo.objects.filter(device=device)

            # 将记录转化为可展示的数据（如字典或其他结构）
            devices = []
            num=1
            for record in borrow_records:
                devices.append({
                    'num':num,
                    "borrow_job_number":record.borrower.job_number  ,
                    "borrow_name": record.borrower.name,
                    "borrow_department": record.borrower.department,
                    "borrow_time": self.timeChangeUTC(record.borrow_time),
                    "borrow_days":record.borrow_days,
                    "back_time": self.timeChangeUTC(record.back_time),
                    "borrow_status_back": "超期" if record.is_overdue else "未超期",  # 是否已归还
                    "overdue_days": record.overdue_days if record.is_overdue else 0
                })
                num=num+1

            # 准备要返回的数据
            viewData = {
                "view_imei_sn": deviceId,
                "view_status": view_status,
                "devices": devices,
                "backName":adminName
            }

            return viewData
        else:
            # 当 devicesList 不为1时，可以返回一个空的字典或其他处理方式
            return {}

    def outStock_updateStatus(self, outDevicesList, person, stock_remark):
        try:
            # 开始事务
            with transaction.atomic():
                # 获取存在的设备 IMEI/SN 列表
                existing_devices = HuaweiDevice.objects.filter(imei_sn__in=outDevicesList)

                if not existing_devices.exists():
                    # 如果没有找到设备，抛出异常
                    return False, "未找到任何匹配的设备"

                # 更新状态为3（出库状态）
                updated_count = existing_devices.update(status=3)

                if updated_count != len(outDevicesList):
                    # 如果更新数量与期望不符，抛出异常
                    return False, "部分设备状态更新失败"

                # 记录设备的出库信息
                stock_out_records = []
                for device in existing_devices:
                    stock_out_records.append(StockOutInfo(
                        device=device,
                        stock_out_person=person,
                        stock_Remark=stock_remark
                    ))

                # 使用 bulk_create 提高性能，插入 StockOutInfo 数据
                if stock_out_records:
                    StockOutInfo.objects.bulk_create(stock_out_records)

            # 如果所有操作都成功，返回成功状态
            return True, "设备出库成功"

        except IntegrityError as e:
            # 捕捉数据库的事务性问题或唯一性约束错误
            return False, f"设备状态更新失败：{str(e)}"

        except ValueError as e:
            # 捕捉设备未找到的情况
            return False, f"操作失败：{str(e)}"

        except Exception as e:
            # 捕捉所有其他类型的异常
            return False, f"出库操作过程中发生错误：{str(e)}"

    def searchDevicesinfo(self,request):
        devicesList = []
        search_emui_sn=self.getStrParam(request,"emui_sn").strip()
        search_borrow_name = self.getStrParam(request, "borrow_name").strip()
        search_device_status = self.getStrParam(request, "device_status").strip()
        print("search_emui_sn:"+search_emui_sn+"-search_borrow_name:"+search_borrow_name+"-search_device_status:"+search_device_status)
        filters = Q()  # 使用 Q 对象来构建复杂查询

        # 根据 emui_sn 过滤
        if search_emui_sn:
            filters &= Q(imei_sn__icontains=search_emui_sn)

        # 根据借用人名称过滤
        if search_borrow_name:
            filters &= Q(borrowinfo__borrower__name__icontains=search_borrow_name)

        # 根据设备状态过滤（确保它是整数）
        if search_device_status:
            try:
                status_value = int(search_device_status)
                filters &= Q(status=status_value)
            except ValueError:
                # 如果转换失败，可以选择记录日志或者处理异常
                pass

        # 如果没有任何查询条件，则返回提示信息
        if not filters:
            return render(request, "index.html", {"devices": devicesList, "message": "请提供至少一个搜索条件。"})

        # 查询设备
        devices = HuaweiDevice.objects.filter(filters).annotate(
            borrow_count=Count('borrowinfo'),  # 统计借用次数
        )

        for i, device in enumerate(devices, start=1):
            # 获取最新借用信息
            holder_name = ""
            latest_borrow_info = device.borrowinfo_set.order_by('-borrow_time').first()  # 获取最新的借用记录

            if latest_borrow_info:  # 如果存在借用记录
                holder_name = latest_borrow_info.borrow_operator  # 获取借用人的姓名
            else:
                # 如果没有借用记录，则获取入库信息的负责人
                latest_stock_in_info = device.stockininfo_set.order_by('-stock_in_time').first()  # 获取最新的入库记录
                if latest_stock_in_info:
                    holder_name = latest_stock_in_info.stock_in_person  # 获取入库人的姓名
            # 准备展示信息
            deviceInfo = {
                'num': i,
                'device_name': device.model_name,
                'device_color': device.color,
                'status': device.get_status_display(),
                'person': holder_name,
                'times': device.borrow_count,  # 使用统计的借用次数
                'imei_sn': device.imei_sn
            }
            devicesList.append(deviceInfo)  # 添加到结果列表

        return devicesList

    def file_iterator(self,request, chunk_size=512):
        fExcel_name = "%s/download/template/%s" % (settings.MEDIA_ROOT, "template.xlsx")
        print(fExcel_name)
        with open(fExcel_name, "rb") as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    def queryAllDevicesData(self):
        devices = HuaweiDevice.objects.all()
        data = []

        for device in devices:
            # Get borrow info and handle datetime fields
            latest_borrow_info = device.borrowinfo_set.order_by('-borrow_time').first()

            if latest_borrow_info:
                borrow_time = latest_borrow_info.borrow_time.replace(
                    tzinfo=None) if latest_borrow_info.borrow_time else '无'
                back_time = latest_borrow_info.back_time.replace(tzinfo=None) if latest_borrow_info.back_time else '无'
            else:
                borrow_time = ''
                back_time = ''

            # Get stock in and stock out info similarly and make datetime fields timezone unaware
            latest_stock_in = device.stockininfo_set.order_by('-stock_in_time').first()
            if latest_stock_in:
                stock_in_time = latest_stock_in.stock_in_time.replace(
                    tzinfo=None) if latest_stock_in.stock_in_time else ''
            else:
                stock_in_time = ''

            latest_stock_out = device.stockoutinfo_set.order_by('-stock_out_time').first()
            if latest_stock_out:
                stock_out_time = latest_stock_out.stock_out_time.replace(
                    tzinfo=None) if latest_stock_out.stock_out_time else '无'
            else:
                stock_out_time = ''

            # Prepare device info
            device_info = {
                'IMEI/SN': device.imei_sn,
                'Device Name': device.model_name,
                'Device Color': device.color,
                'Status': device.get_status_display(),
                'Borrow Time': borrow_time,
                'Back Time': back_time,
                'Stock In Time': stock_in_time,
                'Stock Out Time': stock_out_time,
                # Add more fields as necessary...
            }

            data.append(device_info)
        # 创建 DataFrame
        df = pd.DataFrame(data)
        excel_path = "%s/download/devicesInfo/" % (settings.MEDIA_ROOT)
        current_date = datetime.now().strftime('%Y%m%d')
        excel_filename = f'devices_info_{current_date}.xlsx'  # 动态文件名
        # 创建 Excel 文件
        excel_filename = excel_path + excel_filename
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Devices Info')

        # 返回 Excel 文件作为 HTTP 响应
        with open(excel_filename, 'rb') as excel_file:
            response = HttpResponse(
                excel_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response[
                'Content-Disposition'] = f'attachment; filename="{excel_filename.split("/")[-1]}"'  # 只提供文件名，而不是完整路径
            return response
    def search_borrow_person(self,borrow_person_job):
        # 获取与借用人工号匹配的借用人信息
        try:
            borrower = BorrowerInfo.objects.get(job_number=borrow_person_job)
            borrow_person_name = borrower.name
            borrow_department = borrower.department
        except BorrowerInfo.DoesNotExist:
            # 处理借用人不存在的情况
            return {
                'devices': [],
                'borrow_name': '',
                'borrow_job_number': '',
                'borrow_department': '',
                'error_message': '借用人信息不存在，请确认工号。'
            }

        # 查询借用信息
        devices = BorrowInfo.objects.select_related('device').filter(
            borrower=borrower,  # 使用外键过滤
            back_time__isnull=True  # 只获取没有还机时间的记录
        )

        # 在 devices 中添加自定义属性
        for device_info in devices:
            device_info.borrow_status_back = "超期" if device_info.is_overdue else "未超期"

        # 将设备信息传递到上下文
        context = {
            'devices': devices,  # 返回 BorrowInfo 的查询集
            'borrow_name': borrow_person_name,  # 借用人姓名
            'borrow_job_number': borrow_person_job,  # 借用人工号
            'borrow_department': borrow_department  # 借用人部门
        }

        return context

    def search_can_borrow(self):
        devices = HuaweiDevice.objects.filter(status__in=[0, 1])  # 假设状态0和1表示设备可借用
        context = {'devices': devices}  # 将设备信息传递给模板
        return context

    def get_borrow_department(self, borrow_person):

        latest_borrow_info = BorrowInfo.objects.filter(user__icontains=borrow_person).order_by('-borrow_time').first()

        if latest_borrow_info:
            # 获取部门和最新借机时间
            department = latest_borrow_info.department
            latest_borrow_time = latest_borrow_info.borrow_time
        else:
            department = None
            latest_borrow_time = None

        return department, latest_borrow_time

    def search_borrow_user(self, search_term):
        if search_term:
            # 根据工号或姓名搜索借用人信息
            users = BorrowerInfo.objects.filter(
                Q(job_number__icontains=search_term) |
                Q(name__icontains=search_term)
            ).values(
                'job_number',
                'name',
                'department'
            ).distinct()  # 使用 distinct() 以避免重复

            return JsonResponse(list(users), safe=False)
        else:
            return JsonResponse([], safe=False)
    def searchBorrowerInfo(self,request):
        data = json.loads(request.body)
        query = data.get('job_number', '').strip()  # 获取并去掉多余空白字符

        matches = BorrowerInfo.objects.filter(job_number__icontains=query)  # 模糊匹配工号

        # 创建返回数据，包含 job_number, name 和 department
        job_numbers = [{'job_number': borrower.job_number, 'name': borrower.name, 'department': borrower.department}
                       for borrower in matches]
        print(job_numbers)
        return JsonResponse({'job_numbers': job_numbers})

    def uploadExcel(self, request,admin_person):


        try:
            # excel_file = request.FILES['excel_file']
            excel_file = request.FILES['excel_devices_file']
            if not excel_file.name.endswith(('.xls', '.xlsx')):
                return JsonResponse({"status": "error", "message": "文件格式错误，请上传Excel文件（.xls或.xlsx）！"})

            df = pd.read_excel(excel_file)

            # 遍历每一行并插入或更新数据
            for index, row in df.iterrows():
                imei_sn = row.get('IMEI_SN')
                model_name = row.get('Model Name', '')
                model_num = row.get('Model number', '')
                color = row.get('Color', '')
                description = row.get('description', '')

                # 检查IMEI_SN是否存在
                if not imei_sn:
                    return HttpResponse(f"第 {index + 1} 行缺少 IMEI_SN 值", status=400)

                # 插入或更新设备数据
                device, created = HuaweiDevice.objects.update_or_create(
                    imei_sn=imei_sn,
                    defaults={
                        'model_name': model_name,
                        'model_num': model_num,
                        'color': color,
                        'status': 0  # 设置为默认状态0
                    }
                )

                # 插入 StockInInfo 记录
                StockInInfo.objects.create(
                    device=device,  # 关联的设备
                    stock_in_person=admin_person,  # 入库人
                    stock_Remark=description  # 入库备注
                )

            return  JsonResponse({"status": "success", "message": "数据已成功插入或更新。"})

        except Exception as e:
            # 如果出现异常，返回详细的错误信息
            return JsonResponse({"status": "error", "message": f"上传失败，错误信息：{str(e)}"})