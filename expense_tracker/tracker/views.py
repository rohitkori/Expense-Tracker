from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from decimal import Decimal

from .models import User, Expense, Participant
from .serializers import UserSerializer, ExpenseSerializer, ParticipantSerializer, ParticipantOwedSerializer

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


class GetIndividualExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data['user_id']
        user = User.objects.get(id=user_id)

        owed_amount = 0
        owed = []

        for participant in Participant.objects.filter(user=user, is_settled=False):
            if participant.expense.user != user:
                owed_amount += participant.split_amount
                owed.append(ParticipantSerializer(participant).data)
        
        owned_amount = 0
        owned = []

        for expense in Expense.objects.filter(user=user, is_settled=False):
            for participant in Participant.objects.filter(expense=expense, is_settled=False):
                owned_amount += participant.split_amount
                owned.append(ParticipantOwedSerializer(participant).data)
                

        
        return Response({
            'owed': owed,
            'owned': owned,
            'total_owed': owed_amount,
            'total_owned': owned_amount,
            'net_balance': owned_amount - owed_amount
        }, status=status.HTTP_200_OK)
    

class GetOverallExpensesView(APIView):
    def get(self, request):
        users = User.objects.all()

        response = {}

        for user in users:  

            owed_amount = 0
            owed = []

            for participant in Participant.objects.filter(user=user, is_settled=False):
                if participant.expense.user != user:
                    owed_amount += participant.split_amount
                    owed.append(ParticipantSerializer(participant).data)
            
            owned_amount = 0
            owned = []

            for expense in Expense.objects.filter(user=user, is_settled=False):
                for participant in Participant.objects.filter(expense=expense, is_settled=False):
                    owned_amount += participant.split_amount
                    owned.append(ParticipantOwedSerializer(participant).data)

            response[user.email] = {
                'owed': owed,
                'owned': owned,
                'total_owed': owed_amount,
                'total_owned': owned_amount,
                'net_balance': owned_amount - owed_amount
            }
                

        
        return Response(response, status=status.HTTP_200_OK)

    
