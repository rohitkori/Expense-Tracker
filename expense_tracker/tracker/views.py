from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
import csv
from io import StringIO
from django.core.files.base import ContentFile
from django.conf import settings
import os

from .models import User, Expense, Participant
from .serializers import UserSerializer, ExpenseSerializer, ParticipantSerializer, ParticipantOwedSerializer, UserDetailSerializer, MyTokenObtainPairSerializer

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
    

class GetUserView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MyObtainTokenPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


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


class GetBalanceSheetView(APIView):
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
                

        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(['Type', 'Created By', 'Title', 'Amount', 'Settled'])

        for item in owed:
            writer.writerow(['Owed', item['split_created_by'], item['split_title'], item['split_amount'], item['is_settled']])
        for item in owned:
            writer.writerow(['Owned', user.email, item['split_title'], item['split_amount'], item['is_settled']])

        writer.writerow([])
        writer.writerow(['Total Owed', owed_amount])
        writer.writerow(['Total Owned', owned_amount])
        writer.writerow(['Net Balance', owned_amount - owed_amount])

        filename = f"{user.email}_balance_sheet.csv"
        
        user.balance_sheet.save(filename, ContentFile(csv_buffer.getvalue().encode()), save=True)

        balance_sheet_url = user.balance_sheet.url

        balance_sheet_url = settings.BACKEND_URL + balance_sheet_url
            
        return Response({'balance_sheet': balance_sheet_url}, status=status.HTTP_200_OK)
