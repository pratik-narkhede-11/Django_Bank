from rest_framework import serializers
from mybank.models import Account, Customer, Transaction

class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Customer
        fields = "__all__"

class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account with nested Customer details."""
    customer = CustomerSerializer()  # Include customer details as a nested serializer

    class Meta:
        model = Account
        fields = "__all__"

    def create(self, validated_data):
        """Custom create method to handle nested customer data."""
        customer_data = validated_data.pop('customer')  # Extract nested customer data
        customer = Customer.objects.create(**customer_data)  # Create the customer instance
        account = Account.objects.create(customer=customer, **validated_data)  # Create the account linked to the customer
        return account

    def update(self, instance, validated_data):
        """Custom update method to handle nested customer data."""
        customer_data = validated_data.pop('customer', None)

        # Update customer data if provided
        if customer_data:
            customer = instance.customer
            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()

        # Update account data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
        
        
class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Transaction
        fields = "__all__"