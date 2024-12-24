from django.forms import forms

from apps.StoresManager.models import Store


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['store_name', 'address', 'phone_number', 'latitude', 'longitude', 'category', 'rating', 'price_range', 'opening_hours']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入店铺名称'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入店铺地址'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入店铺电话'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '请输入纬度'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '请输入经度'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入店铺类别'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '请输入评分'}),
            'price_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入价格区间'}),
            'opening_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入营业时间'}),
        }

    # 你也可以根据需要自定义表单验证
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and len(phone_number) < 10:
            raise forms.ValidationError("电话号码长度不足，请检查！")
        return phone_number