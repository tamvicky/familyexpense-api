import tempfile
import os
from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
import datetime

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Family, UserProfile, ExpenseRecord

RECORD_URL = reverse('expense:expenserecord-list')


def image_upload_url(record_id):
    """Return URL for expense record image upload"""
    return reverse('expense:expenserecord-upload-image', args=[record_id])


def detail_url(record_id):
    """Return category detail URL"""
    return reverse('expense:expenserecord-detail', args=[record_id])


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
        for data in res.data:
            self.assertTrue(data['user']['email'] == self.user.email and
                            not data['family'])

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
        for data in res.data:
            self.assertEqual(data['family']['id'], self.family.id)

    def test_retrieve_all_expense_record_by_day(self):
        """
        Test retrieving all expense records
        by day
        """

        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     date='2021-10-5')
        create_sample_expense_record(user=self.user,
                                     date='2021-10-5')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     date='2021-10-4')
        create_sample_expense_record(user=self.user,
                                     date='2021-10-4')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        params = {
            'year': '2021',
            'month': '10',
            'day': '5'
        }

        res = self.client.get(RECORD_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for data in res.data:
            self.assertEqual(data['date'], '2021-10-05')

    def test_retrieve_all_expense_record_by_month(self):
        """
        Test retrieving all expense records
        by month
        """

        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     date='2021-10-5')
        create_sample_expense_record(user=self.user,
                                     date='2021-10-5')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     date='2021-09-4')
        create_sample_expense_record(user=self.user,
                                     date='2021-08-4')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        params = {
            'year': '2021',
            'month': '10',
        }

        res = self.client.get(RECORD_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for data in res.data:
            self.assertIn('2021-10-', data['date'])

    def test_retrieve_all_expense_record_by_year(self):
        """
        Test retrieving all expense records
        by year
        """

        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     date='2021-10-5')
        create_sample_expense_record(user=self.user,
                                     date='2021-10-5')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     date='2020-10-4')
        create_sample_expense_record(user=self.user,
                                     date='2020-10-4')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        params = {
            'year': '2021',
        }

        res = self.client.get(RECORD_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for data in res.data:
            self.assertIn('2021-', data['date'])

    def test_retrieve_all_expense_record_by_date_range(self):
        """
        Test retrieving all expense records
        by year
        """

        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     date='2021-10-5')
        create_sample_expense_record(user=self.user,
                                     date='2021-09-5')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     date='2021-08-4')
        create_sample_expense_record(user=self.user,
                                     date='2021-07-4')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        date1 = datetime.date(2021, 9, 1)
        date2 = datetime.date(2021, 10, 30)
        date_range_str = date1.strftime(
            "%Y-%m-%d") + "," + date2.strftime("%Y-%m-%d")

        # date-range f
        params = {
            'date_range': date_range_str
        }

        res = self.client.get(RECORD_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for data in res.data:
            data_date = datetime.datetime.strptime(data['date'],
                                                   "%Y-%m-%d").date()
            self.assertTrue(data_date >= date1 and
                            data_date <= date2)

    def test_retrieve_all_expense_record_by_category(self):
        """
        Test retrieving all expense records
        by category
        """
        cat_sport = Category.objects.create(name='Sport', isPublic=True)
        cat_car = Category.objects.create(name='Car', isPublic=True)

        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_sport)
        create_sample_expense_record(user=self.user,
                                     category=cat_sport)
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_car)
        create_sample_expense_record(user=self.user,
                                     category=cat_car)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        params = {
            'category': cat_sport.id,
        }

        res = self.client.get(RECORD_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for data in res.data:
            self.assertEqual(data['category']['id'], cat_sport.id)

    def test_retrieve_expense_record_by_mutliple_query_fields(self):
        """
        Test retrieving expense records
        by type, year, month, category
        """
        cat_sport = Category.objects.create(name='Sport', isPublic=True)
        cat_car = Category.objects.create(name='Car', isPublic=True)
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password'
        )
        create_user_profile(user2, self.family)

        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_sport,
                                     date='2021-10-05')
        create_sample_expense_record(user=self.user,
                                     category=cat_sport,
                                     date='2021-10-03')
        create_sample_expense_record(user=self.user,
                                     family=self.family,
                                     category=cat_car,
                                     date='2021-09-10')
        create_sample_expense_record(user=self.user,
                                     category=cat_car,
                                     date='2021-08-20')
        create_sample_expense_record(user=user2,
                                     family=self.family,
                                     category=cat_sport,
                                     date='2021-10-05')
        create_sample_expense_record(user=user2,
                                     category=cat_sport,
                                     date='2021-10-03')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        params = {
            'type': 'personal',
            'category': cat_sport.id,
            'year': '2021',
            'month': '10'
        }

        res = self.client.get(RECORD_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for data in res.data:
            self.assertEqual(data['category']['id'], cat_sport.id)
            self.assertIn('2021-10-', data['date'])
            self.assertEqual(data['user']['email'], self.user.email)

    def test_create_expense_record_family(self):
        """Test creating expense record"""
        cat = Category.objects.create(name='Food', isPublic=True)
        payload = {
            'user': self.user.id,
            'family': self.family.id,
            'category': cat.id,
            'date': '2021-10-01',
            'amount': 123.2,
            'notes': 'Dinner at Restuarant A'
        }
        res = self.client.post(RECORD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        record = ExpenseRecord.objects.get(id=res.data['id'])
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.family, self.family)
        self.assertEqual(record.category, cat)
        self.assertEqual(str(record.amount),
                         "{:.2f}".format(payload['amount']))
        self.assertEqual(record.date.strftime("%Y-%m-%d"),
                         payload['date'])
        self.assertEqual(record.notes, payload['notes'])

    def test_create_expense_record_personal(self):
        """Test creating expense record"""
        cat = Category.objects.create(name='Food', isPublic=True)
        payload = {
            'user': self.user.id,
            'category': cat.id,
            'date': '2021-10-01',
            'amount': 123.2,
        }
        res = self.client.post(RECORD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        record = ExpenseRecord.objects.get(id=res.data['id'])
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.family, None)
        self.assertEqual(record.category, cat)
        self.assertEqual(str(record.amount),
                         "{:.2f}".format(payload['amount']))
        self.assertEqual(record.date.strftime("%Y-%m-%d"),
                         payload['date'])
        self.assertEqual(record.notes, '')

    def test_partial_update_expense_record(self):
        """Test updating a record with patch"""
        cat_food = Category.objects.create(name='Food', isPublic=True)
        record = create_sample_expense_record(user=self.user,
                                              family=self.family,
                                              date='2021-10-05')

        payload = {'category': cat_food.id, 'notes': 'Dinner'}
        url = detail_url(record.id)
        self.client.patch(url, payload)

        record.refresh_from_db()
        self.assertEqual(record.notes, payload['notes'])
        self.assertEqual(record.category, cat_food)

    def test_full_update_expense_record(self):
        """Test updating a record with put"""
        cat_car = Category.objects.create(name='Car', isPublic=True)
        record = create_sample_expense_record(user=self.user,
                                              family=self.family)

        payload = {
            'user': self.user.id,
            'family': self.family.id,
            'category': cat_car.id,
            'date': '2021-09-02',
            'amount': 60,
            'notes': 'Parking'
        }

        url = detail_url(record.id)
        self.client.put(url, payload)

        record.refresh_from_db()
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.family, self.family)
        self.assertEqual(record.category, cat_car)
        self.assertEqual(str(record.amount),
                         "{:.2f}".format(payload['amount']))
        self.assertEqual(record.date.strftime("%Y-%m-%d"),
                         payload['date'])
        self.assertEqual(record.notes, payload['notes'])

    def test_patial_update_expense_record_exception(self):
        """Test updating a record with put"""
        cat_car = Category.objects.create(name='Car', isPublic=True)
        record = create_sample_expense_record(user=self.user,
                                              family=self.family,
                                              category=cat_car)
        defaults = {
            'date': '2021-10-01',
            'amount': 123.2,
            'notes': 'Dinner at Restuarant A'
        }

        payload = {'date': ''}

        url = detail_url(record.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        record.refresh_from_db()
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.family, self.family)
        self.assertEqual(record.category, cat_car)
        self.assertEqual(str(record.amount),
                         "{:.2f}".format(defaults['amount']))
        self.assertEqual(record.date.strftime("%Y-%m-%d"),
                         defaults['date'])
        self.assertEqual(record.notes, defaults['notes'])

    def test_full_update_expense_record_exception(self):
        """Test updating a record with put"""
        cat_car = Category.objects.create(name='Car', isPublic=True)
        record = create_sample_expense_record(user=self.user,
                                              family=self.family,
                                              category=cat_car)
        defaults = {
            'date': '2021-10-01',
            'amount': 123.2,
            'notes': 'Dinner at Restuarant A'
        }

        payload = {}

        url = detail_url(record.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        record.refresh_from_db()
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.family, self.family)
        self.assertEqual(record.category, cat_car)
        self.assertEqual(str(record.amount),
                         "{:.2f}".format(defaults['amount']))
        self.assertEqual(record.date.strftime("%Y-%m-%d"),
                         defaults['date'])
        self.assertEqual(record.notes, defaults['notes'])

    def test_delete_expense_record_exception(self):
        """Test updating a record with put"""
        record = create_sample_expense_record(user=self.user,
                                              family=self.family)

        record_count = ExpenseRecord.objects.all().count()
        url = detail_url(record.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        record_count2 = ExpenseRecord.objects.all().count()
        self.assertEqual(record_count-1, record_count2)


class RecordImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.record = create_sample_expense_record(user=self.user)

    def tearDown(self):
        self.record.image.delete()

    def test_upload_image_to_record(self):
        """Test uploading an image to record"""
        url = image_upload_url(self.record.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.record.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.record.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.record.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
