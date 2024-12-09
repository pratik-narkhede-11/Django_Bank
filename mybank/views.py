from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Account, Customer, Transaction
from .serializer import AccountSerializer, CustomerSerializer, TransactionSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    
    @action(detail=False, methods=['post'])
    def create_account_with_customer(self, request):
        try:
            # Extract customer and account data from request
            customer_data = request.data.get('customer')
            account_data = request.data.get('account')

            if not customer_data or not account_data:
                return Response({'message': 'Customer and Account details are required'}, status=400)

            # Create customer
            customer_serializer = CustomerSerializer(data=customer_data)
            if customer_serializer.is_valid():
                customer = customer_serializer.save()
            else:
                return Response({'message': 'Invalid customer data', 'errors': customer_serializer.errors}, status=400)

            # Create account linked to the customer
            account_data['customer'] = customer.id  # Associate customer with account
            account_serializer = AccountSerializer(data=account_data)
            if account_serializer.is_valid():
                account = account_serializer.save()
            else:
                return Response({'message': 'Invalid account data', 'errors': account_serializer.errors}, status=400)

            return Response({
                'message': 'Account created successfully',
                'customer': customer_serializer.data,
                'account': account_serializer.data
            }, status=201)
        except Exception as e:
            return Response({'message': 'Something went wrong', 'error': str(e)}, status=500)
    
    @action(detail = True, methods = ['get'])
    def accounts(self, request, pk=None):
        try:
            account = Account.objects.filter(pk = pk)
            account_serializers = AccountSerializer(account, many=False, context={'request': request})
            return Response(account_serializers.data, status=200)
        except Exception as e:
            return Response({'message':'Account not exist'}, status=404)
        
        
class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    @action(detail=False, methods=['get'])
    def customers(self, request):
        try:
            phone = request.query_params.get('phone', None)
            if phone:
                customer = Customer.objects.filter(phone__iexact = phone)
                customer_serializer = CustomerSerializer(customer, many=False, context={'request': request})
                return Response(customer_serializer.data, status=200)
            else:
                return Response({'message':'Phone number is required'}, status=400)
        except Exception as e:
            return Response({'message':'Something went wrong'}, status=500)
            
            
            
class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    @action(detail=False, methods=['get'])
    def transaction(self, request):
        try:
            account_id = request.query_params.get('accountId', None)
            if account_id:
                transactions = Transaction.objects.filter(account__id__iexact = account_id)
                transaction_serializer = TransactionSerializer(transactions, many=True, context=({'request':request}))
                return Response(transaction_serializer.data, status=200)
            else:   
                return Response({'message':'Account id is required'}, status=400)
        except Exception as e:
            return Response({'message':'Something went wrong'}, status=500)
        
        
    def validate_pin(self, account, provided_pin):
        """Helper method to validate pin"""
        if account.pin != provided_pin:
            return False
        return True
        

    @action(detail=False, methods=['post'], url_path='deposit')
    def deposit(self, request):
        try:
            account_id = request.data.get('accountId')
            amount = request.data.get('amount')

            pin = request.data.get('pin')

            if not account_id or not amount or not pin:
                return Response({'message': 'Account ID, amount, and pin are required'}, status=400)

            account = get_object_or_404(Account, id=account_id)

            # Validate the pin
            if not self.validate_pin(account, pin):
                return Response({'message': 'Invalid pin'}, status=400)

            initial_balance = account.balance
            final_balance = initial_balance + float(amount)

            # Update the account balance
            account.balance = final_balance
            account.save()

            # Log the transaction
            Transaction.objects.create(
                account=account,
                initial_balance=initial_balance,
                final_balance=final_balance,
                type='DEPOSIT'
            )

            return Response({'message': f'Deposited {amount} to account {account_id}', 'new_balance': account.balance}, status=200)
        except Exception as e:
            return Response({'message': 'Something went wrong', 'error': str(e)}, status=500)

    @action(detail=False, methods=['post'], url_path='withdraw')
    def withdraw(self, request):
        try:
            account_id = request.data.get('accountId')
            amount = request.data.get('amount')

            pin = request.data.get('pin')

            if not account_id or not amount or not pin:
                return Response({'message': 'Account ID, amount, and pin are required'}, status=400)

            account = get_object_or_404(Account, id=account_id)

            # Validate the pin
            if not self.validate_pin(account, pin):
                return Response({'message': 'Invalid pin'}, status=400)

            initial_balance = account.balance

            if initial_balance < float(amount):
                return Response({'message': 'Insufficient funds'}, status=400)

            final_balance = initial_balance - float(amount)

            # Update the account balance
            account.balance = final_balance
            account.save()

            # Log the transaction
            Transaction.objects.create(
                account=account,
                initial_balance=initial_balance,
                final_balance=final_balance,
                type='WITHDRAW'
            )

            return Response({'message': f'Withdrew {amount} from account {account_id}', 'new_balance': account.balance}, status=200)
        except Exception as e:
            return Response({'message': 'Something went wrong', 'error': str(e)}, status=500)


    @action(detail=False, methods=['post'], url_path='transfer')
    def transfer(self, request):
        try:
            sender_account_id = request.data.get('sender_account')
            receiver_account_id = request.data.get('receiver_account')
            amount = request.data.get('amount')

            pin = request.data.get('pin')

            if not sender_account_id or not receiver_account_id or not amount or not pin:
                return Response({'message': 'Sender account, receiver account, amount, and pin are required'}, status=400)

            sender_account = get_object_or_404(Account, id=sender_account_id)
            receiver_account = get_object_or_404(Account, id=receiver_account_id)

            # Validate the pin for sender account
            if not self.validate_pin(sender_account, pin):
                return Response({'message': 'Invalid pin for sender account'}, status=400)

            sender_initial_balance = sender_account.balance
            receiver_initial_balance = receiver_account.balance

            if sender_initial_balance < float(amount):
                return Response({'message': 'Insufficient funds in sender account'}, status=400)

            # Perform the transfer
            sender_account.balance -= float(amount)
            receiver_account.balance += float(amount)

            # Save updated balances
            sender_account.save()
            receiver_account.save()

            # Log the transaction (for both sender and receiver)
            Transaction.objects.create(
                account=sender_account,
                initial_balance=sender_initial_balance,
                final_balance=sender_account.balance,
                type='TRANSFER_OUT'
            )
            Transaction.objects.create(
                account=receiver_account,
                initial_balance=receiver_initial_balance,
                final_balance=receiver_account.balance,
                type='TRANSFER_IN'
            )

            return Response({
                'message': f'Transferred {amount} from account {sender_account_id} to account {receiver_account_id}',
                'sender_new_balance': sender_account.balance,
                'receiver_new_balance': receiver_account.balance
            }, status=200)

        except Exception as e:
            return Response({'message': 'Something went wrong', 'error': str(e)}, status=500)