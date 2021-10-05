from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Family, UserProfile

CAT_URL = reverse('expense:category-list')


def detail_url(cat_id):
    """Return category detail URL"""
    return reverse('expense:category-detail', args=[cat_id])


def create_sample_public_category(**params):
    """Create sample pubic category"""
    defaults = {
        'name': 'Food',
        'isPublic': True
    }
    defaults.update(params)
    return Category.objects.create(**defaults)


def create_sample_user_category_data(user, **params):
    """Create sample user category"""
    defaults = {
        'name': 'Food',
        'isPublic': False,
        'user': user,
        'family': None
    }

    defaults.update(params)
    return Category.objects.create(**defaults)


def create_user_profile(_user, _family):
    UserProfile.objects.create(user=_user, family=_family)


class PublicCatApiTests(TestCase):
    """Test the publicly available category API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving categories"""
        res = self.client.get(CAT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCatApiTests(TestCase):
    """Test the category API after login"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )
        self.family = Family.objects.create(name='Test family')
        create_user_profile(self.user, self.family)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_category(self):
        """Test retrieving category"""
        create_sample_public_category(name='Cat1')
        create_sample_public_category(name='Cat2')
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password2'
        )
        create_user_profile(user2, self.family)
        create_sample_user_category_data(user=self.user, family=self.family)
        create_sample_user_category_data(user=self.user)
        create_sample_user_category_data(user=user2, family=self.family)
        create_sample_user_category_data(user=user2)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        res = self.client.get(CAT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # 2 - public, 2 - user, 1 - family
        self.assertEqual(len(res.data), 5)

    def test_create_category_successful(self):
        """Test creating a new category"""
        payload = {'name': 'Test Cat', 'isPublic': False,
                   'family': self.family.id}
        self.client.post(CAT_URL, payload)

        exists = Category.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_category_invalid(self):
        """Test creating a new category with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(CAT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patial_update_category(self):
        """Test update an existing category"""
        cat = create_sample_public_category()
        payload = {'name': 'Updated Cat'}
        url = detail_url(cat.id)
        self.client.patch(url, payload)

        cat.refresh_from_db()
        self.assertEqual(cat.name, payload['name'])

    def test_full_update_category(self):
        """Test update an existing category"""
        cat = create_sample_user_category_data(
                user=self.user, family=self.family
              )
        payload = {
                'name': 'Updated Cat',
                'isPublic': False,
                'user': self.user,
                'family': ''
            }
        url = detail_url(cat.id)
        self.client.put(url, payload)

        cat.refresh_from_db()
        self.assertEqual(cat.name, payload['name'])
        self.assertEqual(cat.family, None)
