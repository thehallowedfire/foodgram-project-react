from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import USER_FIRST_NAME_MAX_LENGTH, USER_LAST_NAME_MAX_LENGTH


class CustomUser(AbstractUser):
    first_name = models.CharField('Имя',
                                  max_length=USER_FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField('Фамилия',
                                 max_length=USER_LAST_NAME_MAX_LENGTH)
    email = models.EmailField('Email',
                              unique=True)
    subscriptions = models.ManyToManyField(to='self',
                                           through='CustomUserSubscribe',
                                           verbose_name='Подписки')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']


class CustomUserSubscribe(models.Model):
    user = models.ForeignKey(to=CustomUser,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    author = models.ForeignKey(to=CustomUser,
                               on_delete=models.CASCADE,
                               related_name='subscribers',
                               verbose_name='Автор')
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        # Вася Пупкин (ID:5) подписан на пользователя Петя Иванов (ID:3)
        return (f'{self.user} (ID:{self.user.id}) подписан '
                f'на пользователя {self.author} (ID:{self.author.id})')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-created']
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='Unique subscriptions')]
