from django.db import models
from django.db.models import Avg

from apps.CustomManager.models import UserProfile


class StoreIdCounter(models.Model):
    counter_name = models.CharField(max_length=50, unique=True)
    current_value = models.PositiveIntegerField(default=100000)  #

    class Meta:
        db_table = 't_store_idcounter'
        verbose_name = "商店iD管理"
        verbose_name_plural = "商店管理ID"
# 店铺表
class Store(models.Model):
    store_id = models.CharField(max_length=255, unique=True, primary_key=True,verbose_name="用户唯一标识符")
    store_name = models.CharField(max_length=255,verbose_name="store name")  # 店铺名称
    address = models.CharField(max_length=255)  # 店铺地址
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # 店铺电话（可选）
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # 纬度
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # 经度
    district_code = models.IntegerField(unique=True, verbose_name="district code")  # 区号字段
    category = models.CharField(max_length=50)  # 店铺类别（如：奶茶店、果茶店等）
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # 评分
    price_range = models.CharField(max_length=50, blank=True, null=True)  # 价格区间（如：中等、便宜、贵）
    opening_hours = models.CharField(max_length=100, blank=True, null=True)  # 营业时间
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    class Meta:
        db_table = 't_store_manager'
        verbose_name = "store information"

    def __str__(self):
        return self.store_name

    def update_average_rating(self):
        """
        计算并更新平均评分
        """
        reviews = self.reviews.all()  # 获取所有关联的评论
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']  # 使用 Django ORM 聚合计算平均值
        self.average_rating = round(average_rating, 2) if average_rating is not None else 0
        self.save()
    def generate_store_id(self):
        # 获取计数器
        counter, created = StoreIdCounter.objects.get_or_create(counter_name='store_id')
        new_id = counter.current_value
        counter.current_value += 1
        counter.save()
        return f"{new_id:07d}"

    def save(self, *args, **kwargs):
        if not self.store_id:
            self.store_id = self.generate_store_id()
        super().save(*args, **kwargs)
# 店铺标签表
class StoreTag(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='tags')  # 外键关联店铺
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='tags')  # 可为空，关联用户
    tag = models.CharField(max_length=50)  # 标签内容
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    class Meta:
        db_table = 't_store_tag'
        verbose_name = "店铺标签表"
    def __str__(self):
        return f'{self.store.store_name} - {self.tag}'

    constraints = [
        models.UniqueConstraint(fields=['store', 'tag'], name='unique_store_tag')
    ]
# 用户评论表
class Review(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='reviews')  # 外键关联店铺
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # 外键关联用户
    rating = models.IntegerField()  # 评分（1-5）
    comment = models.TextField()  # 评论内容
    created_at = models.DateTimeField(auto_now_add=True)  # 评论时间
    class Meta:
        db_table = 't_store_review'
        verbose_name = "店铺标签表"
    def __str__(self):
        return f'{self.user.name} - {self.store.store_name}'

# 店铺图片表
class StoreImage(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='images')  # 外键关联店铺
    image_url = models.URLField()  # 图片URL
    image_type = models.CharField(max_length=50)  # 图片类型（如：店面、产品等）
    created_at = models.DateTimeField(auto_now_add=True)  # 上传时间
    class Meta:
        db_table = 't_store_image'
        verbose_name = "店铺标签表"
    def __str__(self):
        return f'{self.store.store_name} - {self.image_type}'

# 附近店铺查询日志表
class NearbyQuery(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='queries')  # 外键关联用户
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # 用户查询地点的纬度
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # 用户查询地点的经度
    radius = models.IntegerField()  # 查询半径（米）
    created_at = models.DateTimeField(auto_now_add=True)  # 查询时间
    class Meta:
        db_table = 't_store_nearby_query'
        verbose_name = "店铺标签表"
    def __str__(self):
        return f'Query by {self.user.name} at {self.created_at}'

# 店铺促销活动表
class StorePromotion(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='promotions')  # 外键关联店铺
    promotion_type = models.CharField(max_length=50)  # 促销类型（如：打折、满减等）
    description = models.TextField()  # 促销描述
    start_date = models.DateTimeField()  # 促销开始时间
    end_date = models.DateTimeField()  # 促销结束时间
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    class Meta:
        db_table = 't_store_promotion'
        verbose_name = "店铺标签表"
    def __str__(self):
        return f'{self.store.store_name} - {self.promotion_type}'

# 店铺推荐表
class StoreRecommendation(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recommendations')  # 外键关联用户
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='recommendations')  # 外键关联店铺
    reason = models.TextField()  # 推荐原因
    created_at = models.DateTimeField(auto_now_add=True)  # 推荐时间
    class Meta:
        db_table = 't_store_recommendation'
        verbose_name = "店铺标签表"
    def __str__(self):
        return f'{self.user.name} recommends {self.store.store_name}'
