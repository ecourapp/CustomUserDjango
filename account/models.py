from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext as _


class MyAccountManager(BaseUserManager):
    # Create a new user
    def create_user(self, email, uname, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not uname:
            raise ValueError("Users must have an username")
        user = self.model(
            email=self.normalize_email(email),
            uname=uname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Create a new superuser
    def create_superuser(self, email, uname, password):
        user = self.create_user(
            email=self.normalize_email(email),
            uname=uname,
            password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def get_profile_image_filepath(self, filename):
    return f'profiles/{self.pk}/{"profile_image.png"}'


def get_default_profile_image():
    return f'profiles/{"default.png"}'


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name=_("Email"), max_length=60, unique=True)
    uname = models.CharField(verbose_name=_("Username"), max_length=16, unique=True)
    date_joined = models.DateTimeField(verbose_name=_("Date Joined"), auto_now=False, auto_now_add=True)
    last_login = models.DateTimeField(verbose_name=_("Last Entry"), auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_image = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True, blank=True,
                                      default=get_default_profile_image)
    hide_email = models.BooleanField(default=True)

    objects = MyAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['uname']

    def __str__(self):
        return self.uname

    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index(f'profiles/{self.pk}/'):]

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
