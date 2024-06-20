import os
from djongo import models



class Category(models.Model):
    name = models.CharField(max_length=100)

class Products(models.Model):
     name = models.CharField(max_length=100)
     description = models.CharField(max_length=255)
     image = models.ImageField(upload_to="uploads", height_field=None, width_field=None, max_length=None)
     category = models.CharField(max_length=100)
     selling_price = models.CharField(max_length=100)
     mrp = models.CharField(max_length=100)

def __str__(self):
        return self.name

def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super(Products, self).delete(*args, **kwargs)



class Order_items(models.Model):
    order_code = models.CharField(max_length=20, editable=False,default=None)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    order_code=models.CharField(max_length=255, default=None)
    user_id = models.CharField(max_length=255)
    qty = models.CharField(max_length=255)
    price= models.CharField(max_length=255)
    total = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    discount= models.CharField(max_length=255,default=None)

class Review(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user_id=models.CharField(max_length=255, default=None)
    message = models.CharField(max_length=255,default=None)
    status = models.CharField(max_length=255,default=None)
    rating = models.CharField(max_length=255,default=None)
    subject=models.CharField(max_length=255,default=None)

class Order(models.Model):
      order_code = models.CharField(max_length=20,default=None)
      created_at = models.DateTimeField(auto_now_add=True)
      user_id=models.CharField(max_length=255, default=None)
      delivery_address=models.CharField(max_length=255, default=None)
      order_total=models.CharField(max_length=255, default=None)
      status = models.CharField(max_length=255,default=None)
      contact_number = models.CharField(max_length=255,default=None)
      delivery_mode = models.CharField(max_length=255,default=None)
      pincode = models.CharField(max_length=255,default=None)
      state = models.CharField(max_length=255,default=None)
      country = models.CharField(max_length=255,default=None)

      


