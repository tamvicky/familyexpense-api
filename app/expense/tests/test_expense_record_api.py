from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Family, UserProfile, ExpenseRecord

RECORD_URL = reverse('expense:expenserecord-list')


def detail_url(record_id):
    """Return category detail URL"""
    return reverse('expense:expense-record-detail', args=[record_id])


def create_user_profile(_user, _family):
    UserProfile.objects.create(user=_user, family=_family)


def create_sample_public_category(**params):
    """Create sample pubic category"""
    defaults = {
        'name': 'Food',
        'isPublic': True
    }
    defaults.update(params)
    return Category.objects.create(**defaults)


def create_sample_expense_record(user, **params):
    """Create sample expense record"""
    cat = Category.objects.create(name='Food', isPublic=True)

    defaults = {
        'user': user,
        'family': None,
        'category': cat,
        'amount': 123.2,
        'notes': 'Dinner at Restuarant A'
    }
    defaults.update(params)
    return ExpenseRecord.objects.create(**defaults)


class PublicExpenseRecordApiTests(TestCase):
    """Test the publicly available expense record API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving categories"""
        res = self.client.get(RECORD_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateExpenseRecordApiTests(TestCase):
    """Test the expense record API after login"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )
        self.family = Family.objects.create(name='Test family')
        create_user_profile(self.user, self.family)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_all_my_expense_record(self):
        """
        Test retrieving all expense records by the authenticated user
        """
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password'
        )
        create_user_profile(user2, self.family)

        create_sample_expense_record(user=self.user, family=self.family)
        create_sample_expense_record(user=self.user)
        create_sample_expense_record(user=user2, family=self.family)
        create_sample_expense_record(user=user2)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        res = self.client.get(RECORD_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_personal_expense_record(self):
        """
        Test retrieving all personal expense records
        by the authenticated user
        """
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password'
        )
        create_user_profile(user2, self.family)

        create_sample_expense_record(user=self.user, family=self.family)
        create_sample_expense_record(user=self.user)
        create_sample_expense_record(user=user2, family=self.family)
        create_sample_expense_record(user=user2)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        res = self.client.get(RECORD_URL, {'type': 'personal'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_family_expense_record(self):
        """
        Test retrieving all family expense records
        by the authenticated user's family
        """
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password'
        )
        create_user_profile(user2, self.family)

        create_sample_expense_record(user=self.user, family=self.family)
        create_sample_expense_record(user=self.user)
        create_sample_expense_record(user=user2, family=self.family)
        create_sample_expense_record(user=user2)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        res = self.client.get(RECORD_URL, {'type': 'family'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
