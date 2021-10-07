from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Family, UserProfile, ExpenseRecord

RECORD_URL = reverse('expense:summary-list')


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
        'date': '2021-10-01',
        'amount': 123.2,
        'notes': 'Dinner at Restuarant A'
    }
    defaults.update(params)
    return ExpenseRecord.objects.create(**defaults)


class PublicRecordSummaryApiTests(TestCase):
    """Test the publicly available expense record API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving categories"""
        res = self.client.get(RECORD_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecordSummaryApiTests(TestCase):
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

    def test_all_records_summary_by_category(self):
        """Test all record summary"""
        cat_food = Category.objects.create(name='Food', isPublic=True)
        cat_car = Category.objects.create(name='Car', isPublic=True)
        cat_sport = Category.objects.create(name='Sport', isPublic=True)

        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_food,
                                     amount='100')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_food,
                                     amount='100')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_sport,
                                     amount='100')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_car,
                                     amount='50')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        answer = {
            cat_food.id: 200,
            cat_sport.id: 100,
            cat_car.id: 50
        }

        res = self.client.get(RECORD_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for data in res.data:
            self.assertEqual(str(data['total_amount']),
                             "{:.2f}".format(answer[data['cat_id']]))

    def tes_personal_record_summary_by_category(self):
        """
        Test retrieving all personal expense records
        summary by category
        """
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password'
        )
        create_user_profile(user2, self.family)

        cat_food = Category.objects.create(name='Food', isPublic=True)
        cat_car = Category.objects.create(name='Car', isPublic=True)
        cat_sport = Category.objects.create(name='Sport', isPublic=True)

        # self + family
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_food,
                                     amount='100')
        # self
        create_sample_expense_record(user=self.user,
                                     category=cat_food,
                                     amount='100')
        create_sample_expense_record(user=self.user,
                                     category=cat_sport,
                                     amount='100')
        create_sample_expense_record(user=self.user,
                                     category=cat_car,
                                     amount='50')
        # family member + family
        create_sample_expense_record(user=user2,
                                     family=self.family,
                                     category=cat_food,
                                     amount='100')
        # other
        create_sample_expense_record(user=user2,
                                     category=cat_food,
                                     amount='100')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        answer = {
            cat_food.id: 100,
            cat_sport.id: 100,
            cat_car.id: 50
        }

        res = self.client.get(RECORD_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for data in res.data:
            self.assertEqual(str(data['total_amount']),
                             "{:.2f}".format(answer[data['cat_id']]))

    def test_date_range_records_summary_by_category(self):
        """Test all record summary"""
        cat_food = Category.objects.create(name='Food', isPublic=True)
        cat_car = Category.objects.create(name='Car', isPublic=True)
        cat_sport = Category.objects.create(name='Sport', isPublic=True)

        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_food,
                                     date='2021-09-20',
                                     amount='100')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_food,
                                     date='2021-10-01',
                                     amount='100')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_sport,
                                     date='2021-10-02',
                                     amount='100')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_car,
                                     date='2021-10-03',
                                     amount='50')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        answer = {
            cat_food.id: 100,
            cat_sport.id: 100,
            cat_car.id: 50
        }

        params = {
            'date_range': '2021-10-01,2021-10-31'
        }

        res = self.client.get(RECORD_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for data in res.data:
            self.assertEqual(str(data['total_amount']),
                             "{:.2f}".format(answer[data['cat_id']]))
