import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                            PermissionsMixin
from django.conf import settings
from django.contrib.auth import get_user_model


def record_image_file_path(instance, filename):
    """Generate file path for new record image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/record/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        # Create and saves a new user
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        # Create and save a new super user
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Cusom user model that supports using email instead of username
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Family(models.Model):
    """Family of users"""
    name = models.CharField(max_length=255)
    avatar = models.ImageField(null=True, upload_to=record_image_file_path)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extending user model with a user profile model"""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, upload_to=record_image_file_path)

    def __str__(self):
        return self.user.name


class Category(models.Model):
    """Category for expenses"""
    name = models.CharField(max_length=255)
    isPublic = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    family = models.ForeignKey(Family, on_delete=models.CASCADE,
                               blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.user:
            self.user = None
        if not self.family:
            self.family = None
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ExpenseRecord(models.Model):
    """record for each expense"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    family = models.ForeignKey(Family, on_delete=models.CASCADE,
                               blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 blank=False, null=False)
    date = models.DateField(blank=False)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True)
    image = models.ImageField(null=True, upload_to=record_image_file_path)
