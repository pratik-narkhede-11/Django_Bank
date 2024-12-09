from django.db import models

class Customer(models.Model):
    id = models.AutoField(auto_created=True, unique=True, primary_key=True)
    name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=20)
    create_date_time = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

        
    def __str__(self):
        return self.name


class Account(models.Model):
    id = models.AutoField(auto_created=True, unique=True, primary_key=True)
    pin = models.CharField(max_length=4, null=False)
    balance = models.FloatField(default=0)
    type = models.CharField(max_length=10, choices=(('SAVING','SAVING'),('CURRENT','CURRENT')))
    create_date_time = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    
class Transaction(models.Model):
    id = models.AutoField(auto_created=True, unique=True, primary_key=True)
    create_date_time = models.DateTimeField(auto_now=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    initial_balance = models.FloatField()
    final_balance = models.FloatField()
    type = models.CharField(max_length=20, choices=(('DEPOSIT','DEPOSIT'),('WITHDRAW','WITHDRAW'),('TRANSFER_IN','TRANSFER_IN'),('TRANSFER_OUT','TRANSFER_OUT')))
