from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import User, Expense, Participant

class UserAPITestCase(APITestCase):
    def setUp(self):
        self.create_user_url = reverse('create-user')
        self.login_url = reverse('login')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'mobile_number': '1234567890'
        }

    def test_create_user(self):
        response = self.client.post(self.create_user_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_login(self):
        # Create a user first
        self.client.post(self.create_user_url, self.user_data)
        
        # Attempt to login
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class ExpenseAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword123')
        self.client.force_authenticate(user=self.user)
        self.add_expense_url = reverse('add-expense')

    def test_add_expense(self):
        expense_data = {
            'title': 'Test Expense',
            'amount': '100.00',
            'description': 'Test description',
            'splitting_method': 'EQUAL',
            'participants': [
                {'user': self.user.id}
            ]
        }
        response = self.client.post(self.add_expense_url, expense_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Participant.objects.count(), 1)

class GetIndividualExpensesTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com', password='password123')
        self.client.force_authenticate(user=self.user1)
        self.get_individual_expenses_url = reverse('get-individual-expenses')

        # Create an expense
        self.expense = Expense.objects.create(
            user=self.user1,
            title='Test Expense',
            amount=Decimal('100.00'),
            splitting_method='EQUAL'
        )
        Participant.objects.create(expense=self.expense, user=self.user1, split_amount=Decimal('50.00'))
        Participant.objects.create(expense=self.expense, user=self.user2, split_amount=Decimal('50.00'))

    def test_get_individual_expenses(self):
        response = self.client.post(self.get_individual_expenses_url, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_owned'], Decimal('100.00'))
        self.assertEqual(response.data['total_owed'], Decimal('0.00'))
        self.assertEqual(response.data['net_balance'], Decimal('100.00'))

class GetBalanceSheetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.client.force_authenticate(user=self.user)
        self.get_balance_sheet_url = reverse('get-balance-sheet')

        # Create an expense
        self.expense = Expense.objects.create(
            user=self.user,
            title='Test Expense',
            amount=Decimal('100.00'),
            splitting_method='EQUAL'
        )
        Participant.objects.create(expense=self.expense, user=self.user, split_amount=Decimal('100.00'))

    def test_get_balance_sheet(self):
        response = self.client.post(self.get_balance_sheet_url, {'user_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('balance_sheet', response.data)
        self.assertTrue(response.data['balance_sheet'].endswith('.csv'))

# Unit tests
class ExpenseModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.expense = Expense.objects.create(
            user=self.user,
            title='Test Expense',
            amount=Decimal('100.00'),
            description='Test description',
            splitting_method='EQUAL'
        )

    def test_expense_creation(self):
        self.assertEqual(self.expense.title, 'Test Expense')
        self.assertEqual(self.expense.amount, Decimal('100.00'))
        self.assertEqual(self.expense.user, self.user)

class ParticipantModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.expense = Expense.objects.create(
            user=self.user,
            title='Test Expense',
            amount=Decimal('100.00'),
            splitting_method='EQUAL'
        )
        self.participant = Participant.objects.create(
            expense=self.expense,
            user=self.user,
            split_amount=Decimal('50.00')
        )

    def test_participant_creation(self):
        self.assertEqual(self.participant.expense, self.expense)
        self.assertEqual(self.participant.user, self.user)
        self.assertEqual(self.participant.split_amount, Decimal('50.00'))
