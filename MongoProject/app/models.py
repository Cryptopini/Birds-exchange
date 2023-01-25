import random
from django.db import models
from djongo.models.fields import ObjectIdField
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Customer(models.Model):
    _id = ObjectIdField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    balance_BTC = models.FloatField(default=random.randint(1, 10))
    balance_USD = models.FloatField(default=0)
    trend_BTC = models.FloatField(default=0, null=False)
    trend_USD = models.FloatField(default=0, null=False)
    
    def __str__(self):
        return str(self._id)
    
@receiver(post_save, sender=User)
def update_customer_receiver(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)
    instance.profile.save()
    

class Order(models.Model):
    _id = ObjectIdField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, unique=False)
    initial_want_to_sell = models.FloatField(max_length=32)
    want_to_sell = models.FloatField(max_length=32)
    initial_want_to_buy = models.FloatField(max_length=32)
    want_to_buy = models.FloatField(max_length=32)
    initial_price = models.FloatField(max_length=32)
    price = models.FloatField(max_length=32)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32)
    
    def __str__(self):
        return str(self._id)