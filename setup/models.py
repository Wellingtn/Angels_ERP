from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Vendedora(models.Model):
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='vendedoras/', null=True, blank=True)
    logradouro = models.CharField(max_length=200)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    telefone1 = models.CharField(max_length=20)
    telefone2 = models.CharField(max_length=20, blank=True, null=True)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return self.nome

