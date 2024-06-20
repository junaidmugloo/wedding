from django.shortcuts import (render,HttpResponseRedirect)
import json
from django.http import HttpResponse
from pymongo import MongoClient
from .models import Category,Products,Order,Order_items,Review
from django.contrib.auth.models import User
from django.contrib.auth import (authenticate,logout)
from django.contrib.auth import login as cslogin

client = MongoClient('mongodb://localhost:27017/')
category_db = client['wedding']

# Create your views here.

#dashboard
def index(res):
    reviews=Review.objects.all().count()
    users=User.objects.all().count()
    products=Products.objects.all().count()
    orders=Order.objects.all().count()
    pro=Products.objects.all()
    dict = {
        'reviews': reviews,
        'users':users,
        'products':products,
        'orders':orders,
        'pro':pro,
        }
    return render(res,'index.html',context=dict);
#admin login
def login(res):
    response_data = {}
    if res.method=="POST":
        user=authenticate(res, username=res.POST['username'], password=res.POST['password'])
        if res.POST['username']=="":
            response_data['message'] = 'Enter username'
            return HttpResponse(json.dumps(response_data), content_type="application/json")      
        elif res.POST['password']=="":
            response_data['message'] = 'Enter password'
            return HttpResponse(json.dumps(response_data), content_type="application/json") 
        elif user is not None and user.is_superuser:
            cslogin(res,user)
            response_data['message'] = 'Found'
            return HttpResponse(json.dumps(response_data), content_type="application/json") 
        else:
            response_data['message'] = 'Wrong Username or Password'
            return HttpResponse(json.dumps(response_data), content_type="application/json")            
    else:
        return render(res,'login.html');


def logout_view(res):
    logout(res)
    return HttpResponseRedirect("/su/login")


# add product
def add_product(res):
    response_data={}
    if res.method=="POST":
        category_db=Products(name=res.POST['name'],description=res.POST['description'],category=res.POST['category'],selling_price=res.POST['price'],mrp=res.POST['mrp'],image=res.FILES['image'])
        category_db.save()
        response_data['message'] = 'Added'
        return HttpResponse(json.dumps(response_data), content_type="application/json") 
       
        
    else:
        cat=Category.objects.all()
       
        dict = {
        'dict': cat
        }
        return render(res,'add_product.html',context=dict);

# view product
def view_product(res):
    cat=Products.objects.all()
       
    dict = {
        'dict': cat
        }
    return render(res,'view_product.html',context=dict);


def view_orders(res):
    cat=Order.objects.all()
       
    dict = {
        'dict': cat
        }
    return render(res,'view_orders.html',context=dict);

def order_details(res,id):
    cat=Order_items.objects.filter(order_code=id)
       
    dict = {
        'dict': cat
        }
    return render(res,'order_details.html',context=dict);

def change_order(res):
    if res.method=="POST":
        order=Order.objects.filter(order_code=res.POST.get('order_code'))
        order.update(status=res.POST.get('order_status'))
       
        return HttpResponseRedirect("/su/view/orders")


def delete_product(res,id):
    cat=Products.objects.get(id=id)
    cat.delete()
    return HttpResponseRedirect("/su/view/products")


# add category and view category
def category(res):
    if res.method=="POST":
        category_db= Category(name=res.POST['category'])
        category_db.save()
        return render(res,'category.html');
    else:
        cat=Category.objects.all()
       
        dict = {
        'dict': cat
        }
        return render(res,'category.html',context=dict);
#delete category
def category_delete(res,id):
    cat=Category.objects.get(id=id)
    cat.delete()
    return HttpResponseRedirect("/su/category")



def view_users(res):
    cat=User.objects.all()
    dict = {
        'dict': cat
        }
    return render(res,'view_users.html',context=dict)

def view_review(res):
    cat=Review.objects.all()
    dict = {
        'dict': cat
        }
    return render(res,'view_review.html',context=dict)