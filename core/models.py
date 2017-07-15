from django.db import models


class Account(models.Model):
    email = models.EmailField()
    amount = models.IntegerField(default=0)

    def __str__(self):
        return '%s: %d' % (self.email, self.amount)


class LoginToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=300)
    expire_on = models.DateField()

    def __str__(self):
        return '%s: %s' % (self.email, self.token)
