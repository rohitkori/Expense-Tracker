from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker.views import CreateUserView, ExpenseViewSet, GetIndividualExpensesView, GetOverallExpensesView, GetBalanceSheetView, GetUserView, MyObtainTokenPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = DefaultRouter()

urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('get-user/', GetUserView.as_view(), name='get-user'),
    path('', include(router.urls)),
    path('add-expense/', ExpenseViewSet.as_view(), name='add-expense'),
    path('get-individual-expenses/', GetIndividualExpensesView.as_view(), name='get-individual-expenses'),
    path('get-overall-expenses/', GetOverallExpensesView.as_view(), name='get-overall-expenses'),
    path('get-balance-sheet/', GetBalanceSheetView.as_view(), name='get-balance-sheet'),
    path('login/', MyObtainTokenPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]