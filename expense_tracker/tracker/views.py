from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from decimal import Decimal

from .models import User, Expense, Participant
from .serializers import UserSerializer, ExpenseSerializer, ParticipantSerializer

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


class ExpenseViewSet(APIView):
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetIndividualOweExpensesView(APIView):
    serializer_class = ParticipantSerializer
    queryset = Participant.objects.all()

    def post(self, request):
        user_id = request.data['user_id']
        participants = Participant.objects.filter(user_id=user_id)
        serializer = self.serializer_class(participants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


