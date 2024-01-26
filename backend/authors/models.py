from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import USER_FIRST_NAME_MAX_LENGTH, USER_LAST_NAME_MAX_LENGTH


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=USER_FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=USER_LAST_NAME_MAX_LENGTH)
    email = models.EmailField(unique=True)
    subscriptions = models.ManyToManyField(to='self',
                                           through='CustomUserSubscribe')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class CustomUserSubscribe(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    author = models.ForeignKey(to=CustomUser,
                               on_delete=models.CASCADE,
                               related_name='subscribers')
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created']
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='Unique subscriptions')]
