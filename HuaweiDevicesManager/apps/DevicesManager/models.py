
from django.utils import timezone
from datetime import timedelta
from django.db import models

# Create your models here.
class HuaweiDevice(models.Model):
    STATUS_CHOICES = [
        (0, 'In Stock'),   # 在库
        (2, 'Borrowed'),   # 借用中
        (1, 'Returned'),    # 已归还
        (3, 'Out of Stock') # 出库
    ]

    imei_sn = models.CharField(max_length=150, primary_key=True, verbose_name="设备唯一标识符")  # IMEI或SN，唯一
    model_name = models.CharField(max_length=100, default='', verbose_name="设备名称")  # 设备型号
    model_num = models.CharField(max_length=100, default='', verbose_name="设备编号")  # 设备型号
    color = models.CharField(max_length=50,default='', verbose_name="设备颜色")
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="设备状态")  # 设备状态

    class Meta:
        db_table = 't_huawei_devices'  # 指定数据库表名
        verbose_name = "华为设备"  # 模型的单数名称
        verbose_name_plural = "华为设备列表"  # 模型的复数名称

    def __str__(self):
        return f"{self.model_name} - {self.imei_sn} ({self.get_status_display()})"

    def is_available(self):
        """检查设备是否可借用"""
        return self.status in [0, 1]  # 状态为在库（0）或已归还（1）时可借用

    def mark_as_borrowed(self):
        """标记设备为借用状态"""
        if self.is_available():
            self.status = 2  # 设置为借用状态
            self.save()
            return True
        return False

    def mark_as_returned(self):
        """标记设备为已归还状态"""
        if self.status == 2:  # 只有在借用状态下才能归还
            self.status = 1  # 设置为已归还状态
            self.save()
            return True
        return False


class BorrowerInfo(models.Model):
    job_number = models.CharField(max_length=100, primary_key=True, verbose_name="工号")  # 工号，唯一性约束
    name = models.CharField(max_length=100, default='', verbose_name="用户名称")  # 用户名称
    department = models.CharField(max_length=200, default='', verbose_name="所在部门")  # 所在部门

    class Meta:
        db_table = 't_borrower_info'
        verbose_name = '借用人'
        verbose_name_plural = '借用人管理'

    def __str__(self):
        return f"{self.name} ({self.department})"

class BorrowInfo(models.Model):
    device = models.ForeignKey(HuaweiDevice, on_delete=models.CASCADE, verbose_name="关联设备")  # 关联设备
    borrower = models.ForeignKey(BorrowerInfo, on_delete=models.CASCADE, verbose_name="关联借机信息")  # 关联借用人
    borrow_time = models.DateTimeField(auto_now_add=True)  # 借用时间
    borrow_days = models.PositiveIntegerField()  # 借用天数
    borrow_reason = models.TextField(blank=True)  # 借用原因
    back_time = models.DateTimeField(null=True, blank=True)  # 还机时间，允许为空
    borrow_operator = models.CharField(max_length=100,default='', verbose_name="操作人")  # 负责借出的操作人

    class Meta:
        db_table = 't_borrow_info'  # 指定数据库表名

    def __str__(self):
        return f"{self.device.model} borrowed by {self.user} for {self.borrow_days} days"

    @property
    def is_overdue(self):
        """判断是否超期"""
        if self.back_time:
            return False  # 已归还的不需要再判断是否超期
        due_date = self.borrow_time + timedelta(days=self.borrow_days)
        return timezone.now() > due_date

    @property
    def overdue_days(self):
        """计算超期天数"""
        if not self.is_overdue:
            return 0  # 未超期则返回 0 天
        due_date = self.borrow_time + timedelta(days=self.borrow_days)
        overdue_days = (timezone.now() - due_date).days
        return max(0, overdue_days)

class StockInInfo(models.Model):
    device = models.ForeignKey(HuaweiDevice, on_delete=models.CASCADE)  # 关联设备
    stock_in_time = models.DateTimeField(auto_now_add=True)  # 入库时间
    stock_in_person = models.CharField(max_length=100)  # 入库人
    stock_Remark=models.CharField(max_length=200,default='', verbose_name="设备备注")  # 入库人

    class Meta:
        db_table = 't_stock_in_info'  # 指定数据库表名

    def __str__(self):
        return f"{self.device.model} stocked in by {self.stock_in_person} at {self.stock_in_time}"
class StockOutInfo(models.Model):
    device = models.ForeignKey(HuaweiDevice, on_delete=models.CASCADE)  # 关联设备
    stock_out_time = models.DateTimeField(auto_now_add=True)  # 入库时间
    stock_out_person = models.CharField(max_length=100)  # 入库人
    stock_Remark=models.CharField(max_length=200,default='', verbose_name="设备备注")  # 入库人
    class Meta:
        db_table = 't_stock_out_info'  # 指定数据库表名

    def __str__(self):
        return f"{self.device.model} stocked in by {self.stock_out_person} at {self.stock_out_time}"

