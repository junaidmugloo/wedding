from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db import transaction, IntegrityError
from django.conf import settings
import logging
import json
import hmac
import hashlib
import shortuuid
from cryptography.hazmat.primitives import hashes
from pymongo import MongoClient
from su_admin.models import Category, Products, Order_items,Review,Order
from textblob import TextBlob
from cryptography.hazmat.backends import default_backend
import uuid
import base64
import requests

client = MongoClient('mongodb://localhost:27017/')
category_db = client['wedding']
logger = logging.getLogger(__name__)

#generate order code
def generate_order_code():
    while True:
        code = str(uuid.uuid4()).replace("-", "").upper()[:20]
        if not Order.objects.filter(order_code=code).exists():
            return code


# Create your views here.

def front_index(res):
    cat=Products.objects.all() 
    cart=Order_items.objects.filter(user_id=res.user.id,status="cart").count(); 
    dict = {
        'dict': cat,
        'cart':cart
        }
    return render(res,'index2.html',context=dict);

def front_login(res):
    if res.method == 'POST':
        form = AuthenticationForm(res, data=res.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and not user.is_superuser:
                login(res, user)
                return redirect('home')
            else:
                return render(res,"login2.html",{'error': 'Admin account can''t login '})
        else:
            return render(res,"login2.html",{'error': 'Wrong username or password'})
    else:
        form = AuthenticationForm()
        return render(res,"login2.html",{'form': form})

def front_signup(request):
   
   
    if request.method == 'POST':
        email=request.POST.get('email')
        username=request.POST.get('username')
        password=request.POST.get('password')
        first_name = request.POST.get('first_name')
        user=User.objects.filter(username=username)
        userEmail=User.objects.filter(email=email)
        if username!="" and email!="" and password!="":
            if user.count()>0:
                messages.info(request,"Username already taken")
                return JsonResponse({"error": "This username is already taken"}, status=400)
            elif userEmail.count()>0:
                return JsonResponse({"error": "This email is already taken"}, status=400)
            user=User.objects.create(email=email,username=username,first_name=first_name)
            user.set_password(password)
            user.save()
            return render(request,"signup2.html",{'success': 'Account created successfully'})
        else:
            return JsonResponse({"error": "error occurred"}, status=400)
    return render(request, 'signup2.html')


def product_detail(res,id):
    cart=Products.objects.filter(id=id);
    review=Review.objects.filter(product_id=id)
    cart_data={
    'cart':cart,
    'review':review
    }
    return render(res,"detail2.html",context=cart_data)

def product_shop(res):
    return render(res,"shop.html")

def product_cart(res):
    if res.method=='POST' and Order_items.objects.filter(status="cart",product_id=res.POST.get('product_id'),user_id=res.POST.get('user_id')).count()==0: 
        qty_str=res.POST.get('product_qty')
        price_str=res.POST.get('product_price')
        try:
            qty = int(qty_str) if qty_str is not None else 0
        except ValueError:
            qty = 0

        try:
            price = float(price_str) if price_str is not None else 0.0
        except ValueError:
            price = 0.0
        
        total = price * qty
        product = get_object_or_404(Products, id=res.POST.get('product_id'))
        cart=Order_items.objects.create(product=product,
                                        user_id=res.POST.get('user_id'),
                                        qty=qty_str,
                                        price=price_str,
                                        total=total,
                                        status="cart",
                                        discount=""

                                        )
        cart.save()
    subtotal=0;
    cart=Order_items.objects.filter(user_id=res.user.id,status="cart");  
    for i in cart:
        subtotal= subtotal + float(i.total)
    
    cart_data={
    'cart':cart,
    'sub':subtotal
    }

    return render(res,"cart.html",context=cart_data)



def myorders(res,id):
    subtotal=0;
    cart=Order_items.objects.filter(order_code=id,status="order");  
    for i in cart:
        subtotal= subtotal + float(i.total)
    
    cart_data={
    'cart':cart,
    'sub':subtotal
    }

    return render(res,"myorders.html",context=cart_data)

def orders(res):
    order=Order.objects.filter(user_id=res.user.id);      
    order_data={
    'order':order,
    }

    return render(res,"orders.html",context=order_data)

def product_review(res):
    if res.method=="POST":
        text = res.POST.get('subject')
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity
        flag= Review.objects.filter(user_id=res.POST.get('user_id'),product_id=res.POST.get('product_id')).count()
        if  sentiment_score > 0.9 and blob.sentiment.subjectivity > 0.6:
            return JsonResponse({'success': 'Suspicious review detected'})
        elif sentiment_score == 0 or blob.sentiment.subjectivity == 0:
            return JsonResponse({'success': 'Dont write fake Review'})
        elif flag > 0:
            return JsonResponse({'success': 'Your have already done your Review'})
        else:
            product = get_object_or_404(Products, id=res.POST.get('product_id'))
            review=Review.objects.create(product=product,
                                        user_id=res.POST.get('user_id'),
                                        rating=res.POST.get('rating'),
                                        message=res.POST.get('subject'),
                                        status=sentiment_score,
                                        subject=blob.sentiment.subjectivity,
                                        )
            review.save()
            return JsonResponse({'success': 'Thank for your Review'})


@csrf_exempt
def update_cart(res,id):
    if res.method=="POST":
         data = json.loads(res.body)
         qty = data.get('qty')
         print("hello sir",qty)
         cart=Order_items.objects.get(id=id)
         cart.qty=qty
         cart.total=float(cart.price)*float(qty)
         cart.save()
         return JsonResponse({'message': 'Data updated successfully'}, status=200)


def delete_cart(res,id):
    item=Order_items.objects.filter(id=id);
    item.delete();
    return redirect('product_cart');


def product_contact(res):
    return render(res,"contact.html")

def product_checkout(res):
    if res.method=='POST':
        cart=Order_items.objects.filter(user_id=res.user.id);
        cart_data={
            'cart':cart,
             'tot':res.POST.get('Subtotal')
        }
        return render(res,"checkout.html",context=cart_data)
    return redirect('product_cart');

def place_order(res):
     if res.method=="POST":
       
        code=generate_order_code()
        order_item=Order_items.objects.filter(user_id=res.user.id,status='cart')
        for item in order_item:
            item.order_code=code
            item.status='order'
            item.save()
            
        order = Order.objects.create(
        order_code=code,
        user_id=res.user.id,
        delivery_address=res.POST.get('address'),
        status="order_confirmed",
        contact_number=res.POST.get('contact'),
        delivery_mode=res.POST.get('selector'),
        state=res.POST.get('stt'),
        pincode=res.POST.get('zip'),
        country=res.POST.get('state'),
        order_total=res.POST.get('total'),
        )
        order.save()
        return render(res,'thanks.html')
     return render(res,'thanks.html')

#analyzer
def analyze_sentiment(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity
       
        rating=0
   
        if sentiment_score >= 0.5:
         rating= 5
        elif sentiment_score >= 0.2:
         rating= 4
        elif sentiment_score >= -0.2:
         rating= 3
        elif sentiment_score >= -0.5:
         rating= 2
        else:
         rating= 1
       
        return render(request, 'analyzer/result.html', {'text': text,'rating':blob.sentiment, 'sentiment_score': sentiment_score})

    return render(request, 'analyzer/setup.html')



#test case


def signup_view(request):
    if request.method == 'POST':
        email=request.POST.get('email');
        username=request.POST.get('username');
        password=request.POST.get('password');
        user=User.objects.create(email=email,username=username)
        user.set_password(password)
        user.save()
    else:
       return render(request, 'signup2.html')



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'check2.html', {'form': form})

def front_logout(request):
    logout(request)
    return redirect('home')


#test case end












#payment gateway

# views.py



# Initialize logger

def generate_checksum(data, salt_key, salt_index):
    string_to_hash = f"{data}/pg/v1/pay{salt_key}"
    sha256 = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
    return f"{sha256}###{salt_index}"

@csrf_exempt
def payy(request):
    if request.method == "POST":
        try:
            
            # Generate unique IDs
            merchant_transaction_id = str(uuid.uuid4())
            merchant_order_id = str(uuid.uuid4())
            amount_in_paise = 1000

            # Build redirect and callback URLs
            redirect_url = request.build_absolute_uri(reverse('callback'))
            callback_url = request.build_absolute_uri(reverse('callback'))

            # Prepare data payload
            data = {
                'merchantId': 'PGTESTPAYUAT',
                'merchantTransactionId': merchant_transaction_id,
                'merchantUserId': 'MUID123',
                'merchantOrderId': merchant_order_id,
                'amount': amount_in_paise,
                'redirectUrl': redirect_url,
                'redirectMode': 'POST',
                'callbackUrl': callback_url,
                'mobileNumber': '1234567890',
                'paymentInstrument': {
                    'type': 'PAY_PAGE',
                },
            }

            # Encode data payload
            encoded_data = base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')

            # Generate checksum
            salt_key = '099eb0cd-02cf-4e2a-8aca-3e6c6aff0399'
            salt_index = 1
            final_x_header = generate_checksum(encoded_data, salt_key, salt_index)

            # Make payment request
            headers = {
                'Content-Type': 'application/json',
                'X-VERIFY': final_x_header
            }
            response = requests.post(
                'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay',
                json={'request': encoded_data},
                headers=headers
            )

            # Handle payment response
            response_data = response.json()
            if response.status_code == 200 and response_data.get('success', False):
                redirect_urll = response_data['data']['instrumentResponse']['redirectInfo']['url']
                return HttpResponseRedirect(redirect_urll)
            else:
                return JsonResponse({'error': 'Payment initiation failed', 'data': response_data}, status=response.status_code)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# Callback view
@csrf_exempt
def callback(request):
    if request.method == "POST":
        try:
            input_data = request.POST

            merchant_id = input_data.get('merchantId')
            transaction_id = input_data.get('transactionId')
            order_data = input_data.get('order_data')

            if not all([merchant_id, transaction_id, order_data]):
                return JsonResponse({'error': 'Missing parameters'}, status=400)

            salt_key = '099eb0cd-02cf-4e2a-8aca-3e6c6aff0399'
            salt_index = 1

            string_to_hash = f"/pg/v1/status/{merchant_id}/{transaction_id}{salt_key}"
            sha256 = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
            final_x_header = f"{sha256}###{salt_index}"

            headers = {
                'Content-Type': 'application/json',
                'accept': 'application/json',
                'X-VERIFY': final_x_header,
                'X-MERCHANT-ID': transaction_id,
                'merchantOrderId': order_data,
            }

            url = f"https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay/{merchant_id}/{transaction_id}/"
            response = requests.get(url, headers=headers)

            response_data = response.json()

            if response.status_code == 200:
                # Perform actions based on the response data
                if response_data.get('code') == 'PAYMENT_SUCCESS':
                    # Payment is successful
                    # Perform necessary actions
                    pass
                else:
                    # Payment is not successful
                    # Perform necessary actions
                    pass

                return JsonResponse({'success': True, 'data': response_data})
            else:
                return JsonResponse({'error': 'Failed to fetch status', 'data': response_data}, status=response.status_code)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# Render payment page
def payment(request):
    return render(request, 'payment.html')

# Dummy view for handling payment response
def response_back(request):
    return JsonResponse({'message': 'Payment response received'})

# Dummy view for handling payment callback
def pay_callback(request):
    return JsonResponse({'message': 'Payment callback received'})