from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import User, Expense
from .serializers import UserSerializer, ExpenseSerializer

# Create your views here.

class CreateUserView(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request):
        users = User.objects.all()
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddExpenseView(APIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        data['user'] = request.user.id
        
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            expense = serializer.save()
            return Response({
                'message': 'Expense added and split successfully!',
                'expense': ExpenseSerializer(expense).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       


class GetExpensesView(APIView):
    def get(self, request):
        expenses = Expense.objects.filter(user=request.user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
