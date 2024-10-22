from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker.views import CreateUserView, ExpenseViewSet, GetIndividualExpensesView, GetOverallExpensesView

router = DefaultRouter()

urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('', include(router.urls)),
    path('add-expense/', ExpenseViewSet.as_view(), name='add-expense'),
    path('get-individual-expenses/', GetIndividualExpensesView.as_view(), name='get-individual-expenses'),
    path('get-overall-expenses/', GetOverallExpensesView.as_view(), name='get-overall-expenses'),

]