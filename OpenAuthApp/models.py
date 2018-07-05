from django.db import models
from django.contrib.auth.models import User


class CustomUser(User):
    user_params = models.TextField(null=True,
    							   blank=True)
    def save(self, *args, **kwargs):
        self.set_password(self.password)
        super(CustomUser, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(CustomUser, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"
