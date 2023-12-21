from django.db import models
import datetime

class PageView(models.Model):
    page_name = models.CharField(max_length=255)  #頁面名稱
    total_views = models.IntegerField(default=0)  # 累計瀏覽次數
    date = models.DateField(default=datetime.date.today)  # 日期
    daily_views = models.IntegerField(default=0)  # 當日瀏覽次數

class registered_user(models.Model):
    Username = models.CharField(max_length=20, null=False) #會員姓名
    Usersex = models.CharField(max_length=2, default='M', null=False) #會員性別
    Passwd = models.CharField(max_length=128, null=False) #會員密碼
    Userbirthday = models.DateField(null=False) #會員生日
    Usermail = models.EmailField(max_length=100, blank=True, default='') #會員信箱
    Usertel = models.CharField(max_length=50, blank=True, default='') #會員手機
    Useraddress = models.CharField(max_length=255,blank=True, default='') #會員地址
    Isblacklisted = models.BooleanField(default=False)  # 黑名單欄位

class OrdersModel(models.Model):
    subtotal = models.IntegerField(default=0) #購物金額
    shipping = models.IntegerField(default=0) #運費
    grandtotal = models.IntegerField(default=0) #購物總金額
    customname =  models.CharField(max_length=100, default='') #購買者姓名
    customemail = models.ForeignKey('registered_user', on_delete=models.CASCADE, related_name='orders') #購買者信箱
    customaddress =  models.CharField(max_length=100, default='') #購買者地址
    customphone =  models.CharField(max_length=100, default='') #購買者手機
    shipping_method = models.CharField(max_length=50, default='') #寄送方式
    paytype =  models.CharField(max_length=50, default='') #付款方式
     
class DetailModel(models.Model):
    dorder = models.ForeignKey('OrdersModel', on_delete=models.CASCADE) #訂單
    dname = models.CharField(max_length=100, default='') #商品名稱
    dcolor = models.CharField(max_length=50, default='')  # 顏色
    dsize = models.CharField(max_length=20, default='')   # 尺寸
    dunitprice = models.IntegerField(default=0) #商品單價
    dquantity = models.IntegerField(default=0) #商品數量
    dtotal = models.IntegerField(default=0) #商品總價
    
#商品分類
class ProductTypeModel(models.Model):
    TypeID = models.AutoField(primary_key=True, verbose_name='分類ID')
    TypeName = models.CharField(max_length=50, verbose_name='分類名稱')

#顏色
class ColorModel(models.Model):
    ColorID = models.AutoField(primary_key=True, verbose_name='顏色ID')
    ColorName = models.CharField(max_length=50, verbose_name='顏色名稱')

#尺寸 
class SizeModel(models.Model):
    SizeID = models.AutoField(primary_key=True, verbose_name='尺寸ID')
    SizeName = models.CharField(max_length=50, verbose_name='尺寸名稱')

#商品資訊
class Products(models.Model):
    ProductID = models.AutoField(primary_key=True, verbose_name='商品ID')
    ProductName = models.CharField(max_length=100, verbose_name='商品名稱' , default='')
    Price = models.IntegerField(default=0, verbose_name='價格') 
    Type_id = models.ForeignKey(ProductTypeModel, on_delete=models.CASCADE, verbose_name='分類ID')

#圖片
class ImageModel(models.Model):
    ImageID = models.AutoField(primary_key=True, verbose_name='圖片ID')
    Product_id = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='商品ID', related_name='images')
    ImageName = models.CharField(max_length=100, verbose_name='圖片名稱')

#敘述
class DescriptionModel(models.Model):
    DescriptionID = models.AutoField(primary_key=True, verbose_name='敘述ID')
    Product_id = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='商品ID', related_name='descriptions')
    Description = models.TextField(verbose_name='敘述')
  
#商品顏色尺寸庫存
class ProductColorSizeStockModel(models.Model):
    InventoryID = models.AutoField(primary_key=True, verbose_name='ID')
    Product_id = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='商品ID', related_name='productcolorsizestocks')
    Color_id = models.ForeignKey(ColorModel, on_delete=models.CASCADE, verbose_name='顏色ID', related_name='productcolorsizestocks')
    Size_id = models.ForeignKey(SizeModel, on_delete=models.CASCADE, verbose_name='尺寸ID', related_name='productcolorsizestocks')
    Stock = models.PositiveIntegerField(default=0, verbose_name='庫存')    
