from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import auth
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTPAuthenticationError, SMTPException
from django.views.decorators.csrf import csrf_exempt
import datetime
import random
from django.urls import reverse
from shopping_app import forms
from django.db.models import Q
from .models import *
from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse
from django.db import transaction

message_purchase = ''
cartlist = []  #購買商品串列
subtotal = ''  #購物金額
shipping = ''  #運費
grandtotal = ''  #購物總金額  
customname = ''  #購買者姓名
customphone = ''  #購買者手機
shipping_method = ''  #物流
customaddress = ''  #購買者地址
customemail = ''  #購買者電子郵件
paytype = ''  #付款方式

#####################################################################################################################################

#管理者
def adduser(request):  #新增管理者
	try:
		user=User.objects.get(username="pompompurin")
	except:
		user=None
	if user!=None:
		message = user.username + " 帳號已建立!"
		return HttpResponse(message)
	else:	# 建立 test 帳號			
		user=User.objects.create_user("pompompurin","pompompurin@gmail.com.tw","19960416")
		user.first_name="purin" # 姓名
		user.last_name="pompom"  # 姓氏
		user.is_staff=True	# 工作人員狀態
		user.save()
		return redirect('/admin/')

@csrf_exempt
def adminlogin(request):  #管理者登入
    if request.method == 'POST':
        postform = forms.PostForm(request.POST)
        name = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if not name or not password:
            error_message = '管理者帳號或密碼為空!'
        else:
            user = authenticate(username=name, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    postform = forms.PostForm()
                    return redirect('/backgroundhome/')
                else:
                    error_message = '管理者帳號已停用!'
            else:
                error_message = '管理者帳號或密碼或驗證碼錯誤!'
    else:
        postform = forms.PostForm()
    return render(request, "adminlogin.html", locals())
	
def adminlogout(request):  #管理者登出
	auth.logout(request)
	return redirect('/adminlogin/')	

@csrf_exempt
def backgroundhome(request):  #後台首頁
    return render(request, "backgroundhome.html", locals())

@csrf_exempt
def managementlist(request):  #權限管理
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip() #去空白
        keywords = site_search.split(" ")#字元切割
        q_objects = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                if keyword == "是":
                    q_objects.add(Q(is_superuser=1) | Q(is_staff=1) | Q(is_active=1), Q.OR)
                elif keyword == "否":
                    q_objects.add(Q(is_superuser=0) | Q(is_staff=0) | Q(is_active=0), Q.OR)
                else:
                    q_objects.add(Q(id__contains=keyword), Q.OR)
                    q_objects.add(Q(last_login__contains=keyword), Q.OR)
                    q_objects.add(Q(username__contains=keyword), Q.OR)
                    q_objects.add(Q(first_name__contains=keyword), Q.OR)
                    q_objects.add(Q(last_name__contains=keyword), Q.OR)
                    q_objects.add(Q(email__contains=keyword), Q.OR)
                    q_objects.add(Q(date_joined__contains=keyword), Q.OR)
            resultList = User.objects.filter(q_objects)
    else:   
        resultList =  User.objects.all().order_by('id') 
    if not resultList:
        errormessage="無資料"
        status = False
    else:
        errormessage=""
        status = True
    return render(request,"managementlist.html",locals())  

@csrf_exempt
def managementcreatedata(request):  #新增權限管理
    if request.method =="POST":
        username = request.POST.get("username",None)
        password = request.POST.get("password", None)
        if password is not None:
            hashed_password = make_password(password)
        email = request.POST.get("email",None)
        first_name = request.POST.get("first_name",None)
        last_name = request.POST.get("last_name",None)
        is_superuser= request.POST.get("is_superuser",None)
        is_staff = request.POST.get("is_staff",None)
        is_active= request.POST.get("is_active",None)
        add = User(username=username,password=hashed_password,email=email,first_name=first_name,last_name=last_name,is_superuser=is_superuser,is_staff=is_staff,is_active=is_active)
        add.save()
        return redirect("/managementlist/")
    else:
        return render(request,"managementcreatedata.html",locals())   

@csrf_exempt
def managementedit(request, id=None):  #編輯權限管理
    if request.method == "POST":
        username = request.POST.get("username",None)
        password = request.POST.get("password", None)
        if password is not None:
            hashed_password = make_password(password)
        email = request.POST.get("email",None)
        first_name = request.POST.get("first_name",None)
        last_name = request.POST.get("last_name",None)
        is_superuser= int(request.POST.get("is_superuser", 0))
        is_staff = int(request.POST.get("is_staff", 0))
        is_active= int(request.POST.get("is_active", 0))
        print('is_superuser=',is_superuser,'is_staff=',is_staff,'is_active',is_active)
        update = User.objects.get(id=id)
        update.username = username
        update.password = hashed_password
        update.email = email
        update.first_name = first_name
        update.last_name = last_name
        update.is_superuser = is_superuser
        update.is_staff = is_staff
        update.is_active = is_active
        update.save()
        return redirect('/managementlist/')
    
    else:
        update = User.objects.get(id=id)
        return render(request,"managementedit.html",locals()) 

@csrf_exempt    
def managementdelete(request, id=None):  #刪除權限管理
    if request.method == "POST":
        data = User.objects.get(id=id)
        data.delete()
        return redirect("/managementlist/")
    else:
        dict_data = User.objects.get(id=id)
        return render(request,"managementdelete.html",locals())           

@csrf_exempt
def listall(request):  #會員管理
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip() #去空白
        keywords = site_search.split(" ")#字元切割
        q_objects = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                if keyword == "男":
                    keyword = "M"
                elif keyword == "女":
                    keyword = "F"
                elif keyword == "是":
                    q_objects.add(Q(Isblacklisted=1), Q.OR)
                elif keyword == "否":
                    q_objects.add(Q(Isblacklisted=0), Q.OR)
                q_objects.add(Q(Username__contains=keyword),Q.OR)
                q_objects.add(Q(Usersex__contains=keyword),Q.OR)
                q_objects.add(Q(Userbirthday__contains=keyword),Q.OR)
                q_objects.add(Q(Usertel__contains=keyword),Q.OR)
                q_objects.add(Q(Usermail__contains=keyword),Q.OR)
                q_objects.add(Q(Passwd__contains=keyword),Q.OR)
                q_objects.add(Q(Useraddress__contains=keyword),Q.OR)
            resultList = registered_user.objects.filter(q_objects)
    else:   
        resultList =  registered_user.objects.all().order_by('id') 
    #     sql = "select * from project.shopping_app_registered_user "
    #     keywords = site_search.split(" ")#字元切割
    #     print(keywords)
    #     key_index=0
    #     for keyword in keywords:
    #         if keyword != "":
    #             keyword = "%%"+keyword+"%%"
    #             if keyword == "%%男%%":
    #                 keyword = "M"
    #             elif keyword == "%%女%%":
    #                 keyword = "F"
    #             if key_index == 0:
    #                 sql +="where Username like '%s'"%(keyword)
    #             else:
    #                 sql +="or Username like '%s'"%(keyword)
    #             sql +="or Usersex like '%s'"%(keyword)
    #             sql +="or Userbirthday like '%s'"%(keyword)
    #             sql +="or Usertel like '%s'"%(keyword)
    #             sql +="or Usermail like '%s'"%(keyword)
    #             sql +="or Passwd like '%s'"%(keyword)
    #             sql +="or Useraddress like '%s'"%(keyword)
    #             key_index = key_index +1
    # else:    
    #     sql = "select * from project.shopping_app_registered_user"
    # cursor = connections["default"].cursor() #連接資料庫
    # cursor.execute(sql,[]) #執行sql語法
    # result = cursor.fetchall() #取得資料
    # #取得欄位名稱
    # field_name = cursor.description
    # # print(field_name)
    # cursor.close()
    # #轉換格式
    # resultList=[]
    # for data in result:
    #     # print(data)
    #     i=0
    #     dict_data={}
    #     for d in data:
    #         # print(d)
    #         dict_data[field_name[i][0]]=d
    #         i=i+1
    #     # print(dict_data) 
    #     resultList.append(dict_data)
    # # print(resultList)
    # data_count = len(resultList)
    # # print(data_count)

    if not resultList:
        errormessage="無資料"
        status = False
    else:
        errormessage=""
        status = True
    return render(request,"listall.html",locals())

@csrf_exempt
def createdata(request):  #新增會員管理
    if request.method =="POST":
        Username = request.POST.get("user-name",None)
        Usersex = request.POST.get("user-sex",None)
        Userbirthday = request.POST.get("user-birthday",None)
        Usertel = request.POST.get("user-tel",None)
        Usermail= request.POST.get("user-mail",None)
        Passwd = request.POST.get("pass-wd",None)
        Useraddress= request.POST.get("user-address",None)
        Isblacklisted= int(request.POST.get("Isblacklisted", 0))
        # print("{}:{}:{}:{}:{}:{}:{}".format(Username,Usersex,Userbirthday,Usertel,Usermail,Passwd,Useraddress))
        # sql = "insert into shopping_app_registered_user(Username,Usersex,Userbirthday,Usertel,Usermail,Passwd,Useraddress)"
        # sql += "values('%s','%s','%s','%s','%s','%s','%s')"
        # sql %= (Username,Usersex,Userbirthday,Usertel,Usermail,Passwd,Useraddress)
        # print(sql)
        # cursor = connections["default"].cursor() #連接資料庫
        # cursor.execute(sql,[]) #執行sql語法
        # cursor.close()
        add = registered_user(Username=Username,Usersex=Usersex,Userbirthday=Userbirthday,Usertel=Usertel,Usermail=Usermail,Passwd=Passwd,Useraddress=Useraddress,Isblacklisted=Isblacklisted)
        add.save()
        return redirect("/listall/")
        # return HttpResponse("Hello World")
    else:
        return render(request,"createdata.html",locals())
    
@csrf_exempt
def edit(request, id=None):  #編輯會員管理
    if request.method == "POST":
        Username=request.POST['Username']
        Usersex=request.POST['Usersex']
        Passwd=request.POST['Passwd']
        Userbirthday=request.POST['Userbirthday']
        Usermail=request.POST['Usermail']
        Usertel=request.POST['Usertel']
        Useraddress=request.POST['Useraddress']
        Isblacklisted= int(request.POST.get("Isblacklisted", 0))

        update = registered_user.objects.get(id=id)
        update.Username = Username
        update.Usersex = Usersex
        update.Passwd = Passwd
        update.Userbirthday = Userbirthday
        update.Usermail = Usermail
        update.Usertel = Usertel
        update.Useraddress = Useraddress
        update.Isblacklisted = Isblacklisted
        update.save()

        # sql = "update shopping_app_registered_user set "
        # sql += " Username='%s',Usersex='%s',Passwd='%s',Userbirthday='%s',Usermail='%s', Usertel='%s' , Useraddress='%s' where id=%s"
        # sql %=(Username,Usersex,Passwd,Userbirthday,Usermail,Usertel,Useraddress,id)
    
        # cursor = connections["default"].cursor() #連接資料庫
        # cursor.execute(sql,[]) #執行sql語法
        # cursor.close()
        return redirect('/listall/')
    
    else:
        # sql = "select * from shopping_app_registered_user where id = %s" %(id)
        # print(sql)
        # cursor = connections["default"].cursor() #連接資料庫
        # cursor.execute(sql,[]) #執行sql語法
        # result = cursor.fetchall() #取得資料
        # #取得欄位名稱
        # field_name = cursor.description
        # # print(field_name)
        # cursor.close()

        # dict_data={}
        # for data in result:
        #     i=0
        #     for d in data:
        #         dict_data[field_name[i][0]]=d
        #         i=i+1
        # print(dict_data) 
        update = registered_user.objects.get(id=id)
        # print(dict_data)
        return render(request,"edit.html",locals())    
    
@csrf_exempt    
def delete(request, id=None):  #刪除會員管理
    # print(id)
    if request.method == "POST":
        # sql="delete from shopping_app_registered_user where id = %s"
        # sql %=(id)
        # cursor = connections["default"].cursor() #連接資料庫
        # cursor.execute(sql,[]) #執行sql語法
        # cursor.close()
        data = registered_user.objects.get(id=id)
        data.delete()
        return redirect("/listall/")
    else:
        # sql = "select * from shopping_app_registered_user where id = %s" %(id)
        # print(sql)
        # cursor = connections["default"].cursor() #連接資料庫
        # cursor.execute(sql,[]) #執行sql語法
        # result = cursor.fetchall() #取得資料
        # #取得欄位名稱
        # field_name = cursor.description
        # cursor.close()

        # dict_data={}
        # for data in result:
        #     i=0
        #     for d in data:
        #         dict_data[field_name[i][0]]=d
        #         i=i+1
        # print(dict_data) 
        dict_data = registered_user.objects.get(id=id)
        return render(request,"delete.html",locals())
       
@csrf_exempt
def orders(request):  #收件管理
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip()  # 去空白
        keywords = site_search.split(" ")  # 字元切割
        q_objects = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                print('keyword=', keyword)
                
                if keyword == "是":
                    q_objects.add(Q(customemail__Isblacklisted=1), Q.OR)
                elif keyword == "否":
                    q_objects.add(Q(customemail__Isblacklisted=0), Q.OR)
                q_objects.add(Q(id__contains=keyword),Q.OR)
                q_objects.add(Q(customemail__Username__contains=keyword),Q.OR)
                q_objects.add(Q(customemail__Usermail__contains=keyword),Q.OR)
                q_objects.add(Q(customname__contains=keyword),Q.OR)
                q_objects.add(Q(customphone__contains=keyword),Q.OR)
                q_objects.add(Q(shipping_method__contains=keyword),Q.OR)
                q_objects.add(Q(customaddress__contains=keyword),Q.OR)
                q_objects.add(Q(paytype__contains=keyword),Q.OR)
                q_objects.add(Q(subtotal__contains=keyword),Q.OR)
                q_objects.add(Q(shipping__contains=keyword),Q.OR)
                q_objects.add(Q(grandtotal__contains=keyword),Q.OR)
        resultList = OrdersModel.objects.filter(q_objects)
        
    else:
        resultList = OrdersModel.objects.all().order_by('id')
        print('resultList=',resultList)
    if not resultList:
        errormessage = "無資料"
        status = False
    else:
        errormessage = ""
        status = True
    return render(request, "orders.html", locals())

@csrf_exempt
def ordersedit(request, id=None):  #編輯收件管理
    if request.method == "POST":
        customname = request.POST.get("customname", None)
        customphone = request.POST.get("customphone",None)
        subtotal = request.POST.get("subtotal",None)
        shipping = request.POST.get("shipping",None)
        grandtotal = request.POST.get("grandtotal",None)
        shipping_method = request.POST.get("shipping_method",None)
        customaddress = request.POST.get("customaddress",None)
        paytype = request.POST.get("paytype",None)
        update = OrdersModel.objects.get(id=id)
        update.customname = customname
        update.customphone = customphone
        update.subtotal = subtotal
        update.grandtotal = grandtotal
        update.shipping_method = shipping_method
        update.customaddress = customaddress
        update.paytype = paytype
        update.save()
        return redirect('/orders/')
    
    else:
        update = OrdersModel.objects.get(id=id)
        return render(request,"ordersedit.html",locals()) 

@csrf_exempt    
def ordersdelete(request, id=None):  #刪除收件管理
    if request.method == "POST":
        data = OrdersModel.objects.get(id=id)
        data.delete()
        return redirect("/orders/")
    else:
        dict_data = OrdersModel.objects.get(id=id)
        return render(request,"ordersdelete.html",locals())   

@csrf_exempt
def ordertable(request):  #商品訂單
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip() #去空白
        keywords = site_search.split(" ")#字元切割
        q_objects = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                q_objects.add(Q(dorder__id__contains=keyword), Q.OR)
                q_objects.add(Q(dname__contains=keyword), Q.OR)
                q_objects.add(Q(dcolor__contains=keyword), Q.OR)
                q_objects.add(Q(dsize__contains=keyword), Q.OR)
                q_objects.add(Q(dunitprice__contains=keyword), Q.OR)
                q_objects.add(Q(dquantity__contains=keyword), Q.OR)
                q_objects.add(Q(dtotal__contains=keyword), Q.OR)
            resultList = DetailModel.objects.filter(q_objects)
    else:    
        resultList = DetailModel.objects.all().order_by('dorder_id')
        print('resultList=',resultList)
    if not resultList:
        errormessage = "無資料"
        status = False
    else:
        errormessage = ""
        status = True
    return render(request,"ordertable.html",locals())  

@csrf_exempt
def ordertableedit(request, id=None):  #編輯商品訂單
    if request.method == "POST":
        dname = request.POST.get("dname", None)
        dcolor = request.POST.get("dcolor",None)
        dsize = request.POST.get("dsize",None)
        dunitprice = request.POST.get("dunitprice",0)
        dquantity = request.POST.get("dquantity",0)
        dtotal = request.POST.get("dtotal",0)
        update = DetailModel.objects.get(id=id)
        update.dname = dname
        update.dcolor = dcolor
        update.dsize = dsize
        update.dunitprice = dunitprice
        update.dquantity = dquantity
        update.dtotal = dtotal
        update.save()
        return redirect('/ordertable/')
    
    else:
        update = DetailModel.objects.get(id=id)
        return render(request,"ordertableedit.html",locals()) 


@csrf_exempt    
def ordertabledelete(request, id=None):  #刪除商品訂單
    if request.method == "POST":
        data = DetailModel.objects.get(id=id)
        data.delete()
        return redirect("/ordertable/")
    else:
        dict_data = DetailModel.objects.get(id=id)
        return render(request,"ordertabledelete.html",locals())   
    
@csrf_exempt
def inventorysheet(request):  #庫存查詢
    if 'site_search' in request.POST:
        site_search = request.POST["site_search"]
        site_search = site_search.strip() #去空白
        keywords = site_search.split(" ")#字元切割
        q_objects = Q()
        color_filter = Q()
        for keyword in keywords:
            if keyword != "":
                status = True
                q_objects.add(Q(Type_id__TypeID__contains=keyword), Q.OR)
                q_objects.add(Q(Type_id__TypeName__contains=keyword), Q.OR)
                q_objects.add(Q(ProductName__contains=keyword), Q.OR)
                q_objects.add(Q(Price__contains=keyword), Q.OR)
                q_objects.add(Q(productcolorsizestocks__Color_id__ColorName__contains=keyword), Q.OR)
                q_objects.add(Q(productcolorsizestocks__Size_id__SizeName__contains=keyword), Q.OR)
                q_objects.add(Q(productcolorsizestocks__Stock__contains=keyword), Q.OR)
        result_data1 = Products.objects.filter(q_objects).distinct('ProductID')

        # 獲取所需的資料，並連接相關的模型
        result_data2 = result_data1.values(
            'Type_id__TypeID',
            'Type_id__TypeName',
            'ProductName',
            'Price',
            'productcolorsizestocks__Color_id__ColorName',
            'productcolorsizestocks__Size_id__SizeName',
            'productcolorsizestocks__Stock'          
        )

        # 如果需要進一步過濾，可以使用這個方法
        resultList = result_data2.distinct()

        # 最後，可以使用 result_data 來顯示資料
        for item in resultList:
            print('item=',item)

        productcolorsizestocks = len(resultList)

    else:   
        result_data1 = Products.objects.all()

        # 獲取所需的資料，並連接相關的模型
        result_data2 = result_data1.values(
            'Type_id__TypeID',
            'Type_id__TypeName',
            'ProductName',
            'Price',
            'productcolorsizestocks__Color_id__ColorName',
            'productcolorsizestocks__Size_id__SizeName',
            'productcolorsizestocks__Stock'          
        )

        # 如果需要進一步過濾，可以使用這個方法
        resultList = result_data2.distinct()
        # 最後，可以使用 result_data 來顯示資料
        # for item in resultList:
        #     print(item)
        print('resultList的長度為',len(resultList))

        productcolorsizestocks = len(resultList)
    if not resultList:
        errormessage = "無資料"
        status = False
    else:
        errormessage = ""
        status = True
    return render(request,"inventorysheet.html",locals())     

#####################################################################################################################################

#使用者
def subject(request):  #首頁
    global cartlist
    if 'cartlist' in request.session:  #若session中存在cartlist就讀出
        cartlist = request.session['cartlist']
    else:  #重新購物
        cartlist = []
    images = ImageModel.objects.all()
    productall = Products.objects.all()
    descriptions = DescriptionModel.objects.all()
    first_images = {}
    for i in productall:
        product_images = images.filter(Product_id=i.ProductID)
        if product_images:
            first_images[i.ProductID] = product_images[0]
    user_id = request.session.get('user_id')
    print('user_id = ', user_id)
    if user_id:
        user = registered_user.objects.get(id=user_id)
    page_name = 'subject'  # 此處使用您的頁面名稱

    # 查找或創建 PageView
    page, created = PageView.objects.get_or_create(page_name=page_name, date=datetime.date.today())

    page.total_views = PageView.objects.aggregate(Sum('daily_views'))['daily_views__sum'] or 0

    # 增加瀏覽次數
    page.daily_views += 1
    page.total_views += 1
    page.save()

    # 從 PageView 對象中獲取累計和當日瀏覽次數
    total_views = page.total_views
    daily_views = page.daily_views

    tomorrow = timezone.now() + timezone.timedelta(days=1)
    tomorrow = timezone.datetime.replace(tomorrow, hour=0, minute=0, second=0)
    expires = timezone.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")
    response = render(request, "subject.html", {"total_views": total_views, "daily_views": daily_views})
    response.set_cookie("total_views", str(total_views), expires=expires)

    return render(request, "subject.html", locals())

@csrf_exempt
def login(request):  #登入
    if request.method == 'POST':
        postform = forms.PostForm(request.POST)
        if postform.is_valid():
            captcha_response = postform.cleaned_data.get('captcha')
            Usermail = request.POST.get("email", '')
            Passwd = request.POST.get("pass-wd", '')
            if captcha_response:  
                request.session['verified_captcha'] = True
            else:
                request.session['verified_captcha'] = False
            if Usermail == '' or Passwd == '':
                return redirect("/login/")
            else:
                try:
                    user = registered_user.objects.get(Usermail=Usermail, Passwd=Passwd)
                except registered_user.DoesNotExist:
                    user = None
                if user is not None:
                    postform = forms.PostForm()
                    request.session['user_id'] = user.id
                    return redirect("/subject/")
                else:
                    error_message = "信箱或密碼或驗證碼不正確"
                    postform = forms.PostForm()
        # 返回登入表單頁面
        error_message = "信箱或密碼或驗證碼不正確"
        return render(request, "login.html", locals())
    else:
        postform = forms.PostForm()
        return render(request, "login.html", locals())
    
@csrf_exempt
def signup(request):  #註冊
    if request.method == "POST":
        Username = request.POST.get("user-name",'')
        Usersex = request.POST.get("user-sex",'')
        Userbirthday = request.POST.get("user-birthday",'')
        Usertel = request.POST.get("user-tel",'')
        Usermail= request.POST.get("user-mail",'')
        Passwd = request.POST.get("pass-wd",'')
        Useraddress= request.POST.get("user-address",'')
        strSmtp = "smtp.gmail.com:587"  # 主機
        strAccount = "enter your account"  # 帳號
        template = loader.get_template('signupsuccessfulemail.html')
        content = ""  # 郵件內容
        msg = MIMEMultipart("alternative")  # 創建一個 MIMEMultipart 訊息
        msg["Subject"] = "註冊成功信"  # 郵件標題
        msg["From"] = strAccount
        mailto = [Usermail]
        body_part = MIMEText(template.render({}, request), "html")
        msg.attach(body_part)  # 附加 HTML 內容到訊息中
        server = SMTP(strSmtp)  # 建立SMTP連線
        server.ehlo()  # 跟主機溝通
        server.starttls()  # TTLS 安全認證
        if Username=="" or Usersex =="" or Userbirthday=="" or Usertel=="" or Usermail=="" or Passwd=="" or Useraddress=="":
            return redirect("/signup/")
        try:
            existing_user = registered_user.objects.filter(Usermail=Usermail).first()
            if  existing_user:
                return render(request, "signup.html", locals())
            else:
                unit =registered_user.objects.create(Username=Username,Usersex=Usersex,Userbirthday=Userbirthday, Usertel= Usertel,Usermail=Usermail,Passwd=Passwd,Useraddress=Useraddress)
                unit.save()
                server.login(strAccount, 'login')  # 登入 (信箱兩步驟驗證應用程式密碼)
                server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
                hint = "郵件已發送！"
                return render(request, "signupsuccessful.html", locals())
        except SMTPAuthenticationError:
            hint = "無法登入！"
        except SMTPException as e:
            hint = f"郵件發送產生錯誤: {str(e)}"
        finally:
            server.quit()  # 關閉連線  
    else:
        return render(request, "signup.html", locals())
    
@csrf_exempt
def check_email(request):  #檢查email
    if request.method == "POST":
        email = request.POST.get("email", "")
        # 檢查信箱是否已經註冊
        try:
            user = registered_user.objects.get(Usermail=email)
            return JsonResponse({'email': email})
        except registered_user.DoesNotExist:
            return JsonResponse({'email': ''})

    return render(request, "signup.html", locals())     
    
def signupsuccessfulemail(request):  #註冊成功信
    return render(request, "signupsuccessfulemail.html", locals())      
    
@csrf_exempt
def getpassword(request):  #忘記密碼
    if request.method == "POST":
        Usermail= request.POST.get("user-email",'')
        if Usermail=="":
            return redirect("/getpassword/")
        try:
            user = registered_user.objects.get(Usermail=Usermail)
        except registered_user.DoesNotExist:
            message = "此信箱尚未註冊過!"
            return render(request, "getpassword.html", locals())
        random_password = ''.join(str(random.randint(0, 9)) for _ in range(8))
        user.Passwd = random_password
        user.save()
    
        strSmtp = "smtp.gmail.com:587"  # 主機
        strAccount = "enter your account"  # 帳號
        template = loader.get_template('resetpasswordemail.html')
        content = ""  # 郵件內容
        msg = MIMEMultipart("alternative")  # 創建一個 MIMEMultipart 訊息
        msg["Subject"] = "重設密碼信"  # 郵件標題
        msg["From"] = strAccount
        mailto = [Usermail]
        body_part = MIMEText(template.render({}, request), "html")
        msg.attach(body_part)  # 附加 HTML 內容到訊息中
        server = SMTP(strSmtp)  # 建立SMTP連線
        server.ehlo()  # 跟主機溝通
        server.starttls()  # TTLS 安全認證
        try:
            server.login(strAccount, 'login')  # 登入 (信箱兩步驟驗證應用程式密碼)
            server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
            hint = "郵件已發送！"
        except SMTPAuthenticationError:
            hint = "無法登入！"
        except SMTPException as e:
            hint = f"郵件發送產生錯誤: {str(e)}"
        finally:
            server.quit()  # 關閉連線
        return render(request, "resetpasswordemail.html", locals())
    return render(request, "getpassword.html", locals())    

def resetpasswordemail(request):  #重設密碼信
    return render(request, "resetpasswordemail.html", locals())  

@csrf_exempt
def resetpassword(request):  #重設Encounter U服飾會員
    if request.method == "POST":
        Usermail= request.POST.get("user-mail",None)
        Passwd = request.POST.get("verification-code", None)
        Newpasswd = request.POST.get("pass-wd",None)
        if Usermail=="" or Passwd=="" or Newpasswd=="":
            return redirect("/resetpassword/")
        else:
            try:
                user = registered_user.objects.get(Usermail=Usermail, Passwd=Passwd)
            except registered_user.DoesNotExist:
                user = None
                message_user = "信箱或驗證碼輸入錯誤!"
            if user is not None:
                update = registered_user.objects.get(Usermail=Usermail, Passwd=Passwd) 
                update.Passwd = Newpasswd 
                update.save() 
                strSmtp = "smtp.gmail.com:587"  # 主機
                strAccount = "enter your account"  # 帳號
                template = loader.get_template('resetpasswordsuccessfulemail.html')
                content = ""  # 郵件內容
                msg = MIMEMultipart("alternative")  # 創建一個 MIMEMultipart 訊息
                msg["Subject"] = "重設密碼成功信"  # 郵件標題
                msg["From"] = strAccount
                mailto = [Usermail]
                body_part = MIMEText(template.render({}, request), "html")
                msg.attach(body_part)  # 附加 HTML 內容到訊息中
                server = SMTP(strSmtp)  # 建立SMTP連線
                server.ehlo()  # 跟主機溝通
                server.starttls()  # TTLS 安全認證
                try:
                    server.login(strAccount, 'login')  # 登入 (信箱兩步驟驗證應用程式密碼)
                    server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
                    hint = "郵件已發送！"
                except SMTPAuthenticationError:
                    hint = "無法登入！"
                except SMTPException as e:
                    hint = f"郵件發送產生錯誤: {str(e)}"
                finally:
                    server.quit()  # 關閉連線
                return redirect(reverse('resetpasswordsuccessfulemail'))
            else:
                return render(request, "resetpassword.html", locals())
    else:
        return render(request, "resetpassword.html", locals())
    
def resetpasswordsuccessfulemail(request):  #重設密碼成功信
    return render(request, "resetpasswordsuccessfulemail.html", locals())

def logout(request):  #登出
    global cartlist
    if 'cartlist' in request.session: 
        cartlist = request.session['cartlist']
        cartlist = []
    user_id = request.session.get('user_id')
    request.session.pop('cartlist', None)
    images = ImageModel.objects.all()
    productall = Products.objects.all()
    descriptions = DescriptionModel.objects.all()
    first_images = {}
    for i in productall:
        product_images = images.filter(Product_id=i.ProductID)
        if product_images:
            first_images[i.ProductID] = product_images[0]
    page_name = 'subject'  # 此處使用您的頁面名稱

    # 查找或創建 PageView 對象
    page, created = PageView.objects.get_or_create(page_name=page_name, date=datetime.date.today())

    # 增加瀏覽次數
    page.total_views += 1
    page.daily_views += 1
    page.save()

    # 從 PageView 對象中獲取累計和當日瀏覽次數
    total_views = page.total_views
    daily_views = page.daily_views

    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    tomorrow = datetime.datetime.replace(tomorrow, hour=0, minute=0, second=0)
    expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")
    response = render(request, "subject.html", {"total_views": total_views, "daily_views": daily_views})
    response.set_cookie("total_views", str(total_views), expires=expires)

    if 'user_id' in request.session:
        del request.session['user_id']
    if 'verified_captcha' in request.session:
        del request.session['verified_captcha']
    # return render(request, "subject.html",locals())
    return redirect('subject')

def classification(request, type=None):  #分類頁面
    user_id = request.session.get('user_id')
    if user_id:
        user = registered_user.objects.get(id=user_id)
    products = Products.objects.all()  #取得資料庫所有商品
    images = ImageModel.objects.all()
    descriptions = DescriptionModel.objects.all()
    first_images = {}
    for i in products:
        product_images = images.filter(Product_id=i.ProductID)
        if product_images:
            first_images[i.ProductID] = product_images[0]
    page_name = 'subject'  # 此處使用您的頁面名稱

    # 查找或創建 PageView
    page, created = PageView.objects.get_or_create(page_name=page_name, date=datetime.date.today())

    page.total_views = PageView.objects.aggregate(Sum('daily_views'))['daily_views__sum'] or 0
    # 增加瀏覽次數
    page.daily_views += 1
    page.total_views += 1
    page.save()

    # 從 PageView 對象中獲取累計和當日瀏覽次數
    total_views = page.total_views
    daily_views = page.daily_views

    tomorrow = timezone.now() + timezone.timedelta(days=1)
    tomorrow = timezone.datetime.replace(tomorrow, hour=0, minute=0, second=0)
    expires = timezone.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")
    response = render(request, "subject.html", {"total_views": total_views, "daily_views": daily_views})
    response.set_cookie("total_views", str(total_views), expires=expires)
    if type == 'brand':
        type = 'EncounterU品牌款'
        products = products.filter(Type_id__TypeName='EncounterU品牌款')
    elif type == 'hot':
        type = '熱賣商品'
        products = products.filter(Type_id__TypeName='熱賣商品')
    elif type == 'caot':
        type = '外套'
        products = products.filter(Type_id__TypeName='外套')
    elif type == 'short':
        type = '短袖'
        products = products.filter(Type_id__TypeName='短袖') 
    elif type == 'sleeves':
        type = '長袖 / 7分袖'
        products = products.filter(Type_id__TypeName='長袖 / 7分袖') 
    elif type == 'vest':
        type = '背心'
        products = products.filter(Type_id__TypeName='背心') 
    elif type == 'shirt':
        type = '襯衫'
        products = products.filter(Type_id__TypeName='襯衫') 
    elif type == 'shorts':
        type = '短褲'
        products = products.filter(Type_id__TypeName='短褲') 
    elif type == 'pants':
        type = '長褲'
        products = products.filter(Type_id__TypeName='長褲') 
    elif type == 'jeans':
        type = '牛仔褲'
        products = products.filter(Type_id__TypeName='牛仔褲') 
    elif type == 'culottes':
        type = '短/長/褲裙'
        products = products.filter(Type_id__TypeName='短/長/褲裙') 
    elif type == 'overalls':
        type = '短/長吊帶褲'
        products = products.filter(Type_id__TypeName='短/長吊帶褲')
    elif type == 'sleevelessdress':
        type = '無袖洋裝'
        products = products.filter(Type_id__TypeName='無袖洋裝') 
    elif type == 'shortsleevedress':
        type = '短袖洋裝'
        products = products.filter(Type_id__TypeName='短袖洋裝') 
    elif type == 'longsleevedress':
        type = '長袖洋裝'
        products = products.filter(Type_id__TypeName='長袖洋裝') 
    elif type == 'jumpsuit':
        type = '連身套裝'
        products = products.filter(Type_id__TypeName='連身套裝') 
    elif type == 'suit':
        type = '無袖套裝'
        products = products.filter(Type_id__TypeName='無袖套裝') 
    elif type == 'shortsleevedresssuit':
        type = '短袖套裝'
        products = products.filter(Type_id__TypeName='短袖套裝') 
    elif type == 'longsleevedresssuit':
        type = '長袖套裝'
        products = products.filter(Type_id__TypeName='長袖套裝') 
    elif type == 'bag':
        type = '包包'
        products = products.filter(Type_id__TypeName='包包') 
    elif type == 'discount':
        type = '特價商品'
        products = products.filter(Type_id__TypeName='特價商品') 
   
    return render(request, "classification.html", locals())

@csrf_exempt     
def productcontent(request,productid=None):  #商品資訊
    user_id = request.session.get('user_id')
    if user_id:
        user = registered_user.objects.get(id=user_id)
    productall = Products.objects.all()
    product = Products.objects.get(ProductID=productid)  #取得商品
    images = ImageModel.objects.filter(Product_id=product)
    description = DescriptionModel.objects.get(Product_id=product)
    color_set = set()  # 創建一個空集合來儲存唯一的顏色
    unique_colors = []  # 創建一個空列表來儲存唯一的顏色
    size_set = set()  # 創建一個空集合來儲存唯一的尺寸
    unique_sizes = []  # 創建一個空列表來儲存唯一的尺寸
    stocks = ProductColorSizeStockModel.objects.filter(Product_id=product)
    for stock in stocks:
        color_name = stock.Color_id.ColorName
        size_name = stock.Size_id.SizeName
        if color_name not in color_set:
        # 如果顏色名稱不在集合中，將其添加到集合和唯一顏色列表
            color_set.add(color_name)
            unique_colors.append(color_name)
        if size_name not in size_set:
        # 如果尺寸名稱不在集合中，將其添加到集合和唯一尺寸列表
            size_set.add(size_name)
            unique_sizes.append(size_name)
    page_name = 'subject'  # 頁面名稱

    # 查找或創建 PageView
    page, created = PageView.objects.get_or_create(page_name=page_name, date=datetime.date.today())

    page.total_views = PageView.objects.aggregate(Sum('daily_views'))['daily_views__sum'] or 0

    # 增加瀏覽次數
    page.daily_views += 1
    page.total_views += 1
    page.save()

    # 從 PageView 對象中獲取累計和當日瀏覽次數
    total_views = page.total_views
    daily_views = page.daily_views

    tomorrow = timezone.now() + timezone.timedelta(days=1)
    tomorrow = timezone.datetime.replace(tomorrow, hour=0, minute=0, second=0)
    expires = timezone.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")
    response = render(request, "subject.html", {"total_views": total_views, "daily_views": daily_views})
    response.set_cookie("total_views", str(total_views), expires=expires)

    return render(request, "productcontent.html", locals())

def get_stock(request):  #獲取庫存數量
    Product_id = request.GET.get('Product_id')
    Color_id = request.GET.get('Color_id')
    Size_id = request.GET.get('Size_id')
    Color_id = ColorModel.objects.get(ColorName=Color_id).ColorID
    Size_id = SizeModel.objects.get(SizeName=Size_id).SizeID
    try:
        stock = ProductColorSizeStockModel.objects.get(Product_id=Product_id, Color_id=Color_id, Size_id=Size_id)
        stock_quantity = stock.Stock
    except ProductColorSizeStockModel.DoesNotExist:
        stock_quantity = 0

    return JsonResponse({'stock_quantity': stock_quantity})

@csrf_exempt
def addtocart(request, ctype=None, productid=None):  #加入購物車
    global cartlist
    if ctype == 'add':
        productall = Products.objects.all()
        product = Products.objects.get(ProductID=productid)
        selected_color = request.POST.get('selectedColor')
        selected_size = request.POST.get('selectedSize')
        select_number = int(request.POST.get('stock'))
        Color_id = ColorModel.objects.get(ColorName=selected_color).ColorID
        Size_id = SizeModel.objects.get(SizeName=selected_size).SizeID
        stock = ProductColorSizeStockModel.objects.get(Product_id=product, Color_id=Color_id, Size_id=Size_id)
        stock_quantity = stock.Stock
        images = ImageModel.objects.filter(Product_id=product)
        first_images = {}
        for i in productall:
            product_images = images.filter(Product_id=i.ProductID)
            if product_images:
                first_images[i.ProductID] = product_images[0]
        image = first_images.get(product.ProductID, None)
        # existing_item 設為 None
        existing_item = None
        for unit in cartlist:
            # 檢查購物車中是否已存在相同商品、顏色和尺寸的項目
            if (
                unit[0] == product.ProductName
                and unit[5] == selected_color
                and unit[6] == selected_size
            ):
                existing_item = unit
                break
        if existing_item:
            # 如果該項目已存在，更新其數量
            existing_item[2] = str(int(existing_item[2]) + select_number)
            existing_item[3] = str(int(existing_item[1]) * int(existing_item[2]))
        else:
            # 如果該項目不存在，將新項目添加到購物車
            temlist = [
                product.ProductName,
                str(product.Price),
                str(select_number),
                str(product.Price * select_number),
                image.ImageName if image else "",  # 使用 image 變數的值，如果不存在，則為空字符串
                selected_color,
                selected_size,
                str(select_number),
                str(stock_quantity),
            ]
            cartlist.append(temlist)
        request.session['cartlist'] = cartlist
        return redirect('/cart/')
    elif ctype == 'update':
        updated_cartlist = []
        for index, unit in enumerate(cartlist):
            newnumber = request.POST.get(f'newnumber_{index}')
            checkout = request.POST.get(f'checkout_{index}')
            if newnumber is not None:
                newnumber = int(newnumber)
                if newnumber > 0 and checkout == 'on':
                    unit[2] = str(newnumber)
                    unit[3] = str(int(unit[1]) * int(unit[2]))
                    unit[7] = str(newnumber)
                    updated_cartlist.append(unit)
        cartlist = updated_cartlist
        request.session['cartlist'] = cartlist
        return redirect('/cartorder/')
    elif ctype == 'empty':  #清空購物車
        cartlist = []  #設購物車為空串列
        request.session['cartlist'] = cartlist
        return redirect('/cart/')
    elif ctype == 'remove':  #刪除購物車中商品
        del cartlist[int(productid)]  #從購物車串列中移除商品
        request.session['cartlist'] = cartlist
        return redirect('/cart/')    

@csrf_exempt
def cart(request):  #購物車
    global cartlist
    user_id = request.session.get('user_id')
    if user_id:
        user = registered_user.objects.get(id=user_id)
    products = Products.objects.all().order_by('?')[:2] #隨機排序並只取出2筆商品資訊
    images = ImageModel.objects.all()
    productall = Products.objects.all()
    descriptions = DescriptionModel.objects.all()
    first_images = {}
    for i in productall:
        product_images = images.filter(Product_id=i.ProductID)
        if product_images:
            first_images[i.ProductID] = product_images[0]
    cartnum = len(cartlist)  #購買商品筆數
    cartlist1 = cartlist  # 以區域變數傳給模版
    total = 0
    for unit in cartlist:  # 計算商品總金額
        total += int(unit[3])
        # for item in unit:
        #     print(item)
    return render(request, "cart.html", locals())

@csrf_exempt
def cartorder(request):  #確認訂單
    user_id = request.session.get('user_id')
    if user_id:
        user = registered_user.objects.get(id=user_id)
    global cartlist, message_purchase, customname, customphone, customaddress, customemail
    cartlist1 = request.session['cartlist']
    total = 0
    for unit in cartlist1:  #計算商品總金額
        unit[3] = str(int(unit[1]) * int(unit[2]))
        total += int(unit[1]) * int(unit[2])
    print(cartlist1)
    if request.method == 'POST':
        selected_shipping_method = request.POST.get('selected_shipping_method')
        # 根據 selected_shipping_method 計算運費
        if selected_shipping_method == '7-11':
            shipping_fee = 60
        elif selected_shipping_method == '黑貓宅急便':
            shipping_fee = 200
        else:
            shipping_fee = 0
        grand_total = total + shipping_fee
        print('selected_shipping_method=', selected_shipping_method)
        print('shipping_fee=', shipping_fee)
        print('grand_total=', grand_total)
        # 返回 JSON 響應，包含 shipping_fee 和 grand_total
        response_data = {
            'shipping_fee': shipping_fee,
            'grand_total': grand_total,
        }
        return JsonResponse(response_data)   
    user = registered_user.objects.get(id=user_id)
    customname1 = user.Username
    customphone1 = user.Usertel
    customemail1 = user.Usermail
    message1 = message_purchase
    return render(request, "cartorder.html", locals())

@csrf_exempt
def cartok(request):  #訂購完成
	user_id = request.session.get('user_id')
	if user_id:
		user = registered_user.objects.get(id=user_id)
	user = registered_user.objects.get(id=user_id)
	global cartlist, message_purchase, subtotal, shipping, grandtotal, customname, customemail, customaddress, customphone, shipping_method, paytype
	total = 0
	cartlist = request.session['cartlist']
	for unit in cartlist:
		unit[2] = unit[7]
		unit[3] = str(int(unit[1]) * int(unit[7]))
		total += int(unit[1]) * int(unit[7])
	subtotal = total
	selected_shipping_method = request.POST.get('selected_shipping_method')
	if selected_shipping_method == '7-11':
		shipping_fee = 60
	elif selected_shipping_method == '黑貓宅急便':
		shipping_fee = 200
	else:
		shipping_fee = 0
	shipping =  shipping_fee
	grandtotal = subtotal + shipping
	customname = request.POST.get('CustomerName', '')
	customemail_str = user.Usermail
	customaddress = request.POST.get('city', '') + request.POST.get('district', '') + request.POST.get('addressDetail', '')
	customphone = request.POST.get('CustomerPhone', '')
	shipping_method= request.POST.get('selected_shipping_method', '')
	paytype = request.POST.get('payMethod', '')
	print('subtotal=',subtotal,',shipping=',shipping,',grandtotal=',grandtotal,',customname=',customname,',customemail=',customemail_str,'\n,customaddress=',customaddress,',customphone=',customphone,',shipping_method=',shipping_method,',paytype=',paytype)
	username = user.Username
	if customname=='' or customphone=='' or shipping_method=='' or customaddress=='' or paytype=='':
		message_purchase = '姓名、手機、物流、地址及付款方式皆需選擇與輸入'
		return redirect('/cartorder/')
	else:
		customemail = registered_user.objects.get(Usermail=customemail_str)
		unitorder = OrdersModel.objects.create(subtotal=subtotal, shipping=shipping, grandtotal=grandtotal, customname=customname, customemail=customemail, customaddress=customaddress, customphone=customphone,  shipping_method=shipping_method, paytype=paytype) #建立訂單
		for unit in cartlist:
			unit[2] = unit[7]
			unit[3] = str(int(unit[1]) * int(unit[7]))
			unitdetail = DetailModel.objects.create(dorder=unitorder, dname=unit[0], dcolor=unit[5], dsize=unit[6], dunitprice=unit[1], dquantity=unit[2], dtotal=unit[3])
		orderid = unitorder.id  #取得訂單id
		strSmtp = "smtp.gmail.com:587"  # 主機
		strAccount = "enter your account"  # 帳號
		template = loader.get_template('ordernotificationemail.html')
		context = {
        'username' : username,
        'orderid': orderid, 
        }
		body_part = MIMEText(template.render(context, request), "html")
		msg = MIMEMultipart("alternative")  # 創建一個 MIMEMultipart 訊息
		msg["Subject"] = "訂單通知信"  # 郵件標題
		msg["From"] = strAccount
		mailto = [customemail.Usermail]
		msg.attach(body_part)  # 附加 HTML 內容到訊息中
		server = SMTP(strSmtp)  # 建立SMTP連線
		server.ehlo()  # 跟主機溝通
		server.starttls()  # TTLS 安全認證
		try:
			server.login(strAccount, 'login')  # 登入 (信箱兩步驟驗證應用程式密碼)
			server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
			hint = "郵件已發送！"
		except SMTPAuthenticationError:
			hint = "無法登入！"
		except SMTPException as e:
			hint = f"郵件發送產生錯誤: {str(e)}"
		finally:
			server.quit()  # 關閉連線
		cartlist = []
	request.session['cartlist'] = cartlist
	return render(request, "cartok.html", locals())

def ordernotificationemail(request):  #訂單通知信
    return render(request, "ordernotificationemail.html", locals())

@csrf_exempt
def cartordercheck(request):  #訂單查詢
	user_id = request.session.get('user_id')
	if user_id:
		user = registered_user.objects.get(id=user_id)	
	user = registered_user.objects.get(id=user_id)
	orderid = request.POST.get('orderid', '')  #取得輸入id
	customemail = request.POST.get('customemail', '')  #取得輸入email
	firstsearch = 0
	notfound = 0
	if orderid == '' and customemail == '':  #按查詢訂單鈕
		firstsearch = 1
	else:
		if orderid:
			order = OrdersModel.objects.filter(id=orderid).first()
			if not order:
				notfound = 1
			else:
				details = DetailModel.objects.filter(dorder=order)
		elif customemail:
			orders = OrdersModel.objects.filter(customemail=customemail)
			if not orders:
				notfound = 1
			else:
				details = DetailModel.objects.filter(dorder__in=orders)

	return render(request, "cartordercheck.html", locals())

@csrf_exempt
def modifymemberprofile(request, id=None):  #修改資料
    user_id = request.session.get('user_id', None)
    print('user_id = ',user_id)
    if 'user_id' in request.session:
        if request.method == 'POST':
            Usersex = request.POST['Usersex']
            Userbirthday = request.POST['Userbirthday']
            Usertel = request.POST['Usertel']
            Useraddress = request.POST['Useraddress']
            update = registered_user.objects.get(id=user_id)
            update.Username = update.Username
            update.Usersex = Usersex
            update.Passwd = update.Passwd
            update.Userbirthday = Userbirthday
            update.Usermail = update.Usermail
            update.Usertel = Usertel
            update.Useraddress = Useraddress
            update.save()
            return redirect('/subject/')
        else:
            update = registered_user.objects.get(id=user_id)
            return render(request, "modifymemberprofile.html", locals())
    else:
        return render(request, "login.html", locals())


        


  

 
            
            



 

















