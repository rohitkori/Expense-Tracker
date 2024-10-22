from django.urls import path
from tracker.views import CreateUserView, AddExpenseView, GetExpensesView


urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('add-expense/', AddExpenseView.as_view(), name='add-expense'),
    path('expenses/', GetExpensesView.as_view(), name='get-expenses'),
]