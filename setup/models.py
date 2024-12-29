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

class Produto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='produtos/', null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    logradouro = models.CharField(max_length=200, default="Não informado")
    bairro = models.CharField(max_length=100, default="Não informado")
    cidade = models.CharField(max_length=100, default="Não informada")
    uf = models.CharField(max_length=2, default="UF")
    telefone = models.CharField(max_length=20, default="Não informado")

    def __str__(self):
        return self.nome

