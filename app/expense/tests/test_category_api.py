from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Family, UserProfile

CAT_URL = reverse('expense:category-list')


def create_sample_category_data():
    Category.objects.create(name='cat1', isPublic=True, user=None, family=None)
    Category.objects.create(name='cat2', isPublic=True, user=None, family=None)


def create_sample_user_category_data(_user, _family):
    Category.objects.create(name='cat3', isPublic=False,
                            user=_user, family=_family)
    Category.objects.create(name='cat4', isPublic=False,
                            user=_user, family=None)


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
        create_sample_category_data()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password2'
        )
        family = Family.objects.create(name='Test family')
        create_user_profile(self.user, family)
        create_user_profile(user2, family)
        create_sample_user_category_data(self.user, family)
        create_sample_user_category_data(user2, family)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_cats(self):
        """Test retrieving cats"""
        res = self.client.get(CAT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # 2 - public, 2 - user, 1 - family
        self.assertEqual(len(res.data), 5)
