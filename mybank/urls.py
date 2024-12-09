from django.urls import path, include
from mybank.views import AccountViewSet, CustomerViewSet, TransactionViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'transactions', TransactionViewSet)


urlpatterns = [
    path('',include(router.urls)),
]