from django.contrib import admin
from django.urls import path
from su_admin import views as su
from su_frontend import views as front
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('su/',su.index),

    #admin login from admin panel or django admin
    path('su/login',su.login),
    path('su/logout',su.logout_view),

    #user routing
     path('su/view/users',su.view_users),
   
    #product routing
    path('su/add/products',su.add_product),
    path('su/view/products',su.view_product),
    path('su/products/delete/<id>',su.delete_product),
    path('su/view/review',su.view_review),
    #orders routing
     path('su/view/orders',su.view_orders),
     path('su/view/orders/change',su.change_order),
     
     path('su/view/order_details/<id>',su.order_details),
    # category routing
    path('su/category',su.category),
    path('su/category/delete/<id>',su.category_delete),


    #front end routing
     path('', front.front_index, name='home'),
     path('login/', front.front_login, name='front_login'),
     path('logout/', front.front_logout, name='front_logout'),
     path('signup/', front.front_signup, name='front_signup'),
     path('product/detail/<int:id>', front.product_detail, name='product_detail'),
     path('product/review/', front.product_review, name='product_review'),
     
     path('shop/', front.product_shop, name='product_shop'),
     path('contact/', front.product_contact, name='product_contact'),
     path('cart/', front.product_cart, name='product_cart'),
     path('cart_delete/<int:id>', front.delete_cart, name='cart_delete'),
     path('cart_update/<int:id>',front.update_cart, name='cart_update'),
     path('checkout/', front.product_checkout, name='product_checkout'),
     path('place_order/', front.place_order, name='place_order'),
     path('myorders/<id>', front.myorders, name='myorders'),
     path('orders/', front.orders, name='orders'),
    


#analyze
 path('analyze/', front.analyze_sentiment, name='analyze_sentiment'),

#test case start
 path('test/', front.signup_view, name='signup_view'),
 path('test2/', front.login_view, name='login_view'),
#test case end

#payment gateway
    path('payy/', front.payy, name='payy'),
    path('callback/', front.callback, name='callback'),
    path('payment/', front.payment, name='payment'),
    path('response_back/', front.response_back, name='pay_response_back'),
    path('pay_callback/', front.pay_callback, name='pay_callback'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
