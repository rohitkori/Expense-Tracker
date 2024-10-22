from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker.views import CreateUserView, ExpenseViewSet, GetIndividualOweExpensesView

router = DefaultRouter()

urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('', include(router.urls)),
    path('add-expense/', ExpenseViewSet.as_view(), name='add-expense'),
    path('get-individual-expenses/', GetIndividualOweExpensesView.as_view(), name='get-individual-expenses'),
]