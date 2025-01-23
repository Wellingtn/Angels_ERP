from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import os
from django.utils import timezone

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
    contrato = models.FileField(upload_to='contratos/', null=True, blank=True)
    produtos = models.ManyToManyField('Produto', through='EstoqueVendedora')

    def __str__(self):
        return self.nome

    def delete(self, *args, **kwargs):
        if self.contrato:
            if os.path.isfile(self.contrato.path):
                os.remove(self.contrato.path)
        super(Vendedora, self).delete(*args, **kwargs)

class EstoqueVendedora(models.Model):
    vendedora = models.ForeignKey(Vendedora, on_delete=models.CASCADE)
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('vendedora', 'produto')

    def __str__(self):
        return f"{self.vendedora.nome} - {self.produto.nome}: {self.quantidade}"

class Produto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='produtos/', null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    logradouro = models.CharField(max_length=200, default="Não informado")
    bairro = models.CharField(max_length=100, default="Não informado")
    cidade = models.CharField(max_length=100, default="Não informada")
    uf = models.CharField(max_length=2, default="UF")
    telefone = models.CharField(max_length=20, default="Não informado")

    def __str__(self):
        return self.nome

    def historico_compras(self):
        return self.compras.all().order_by('-data')

class Compra(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='compras')
    data = models.DateTimeField(default=timezone.now)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Compra de {self.cliente.nome} em {self.data.strftime('%d/%m/%Y')}"

class ItemCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} em {self.compra}"

class Acerto(models.Model):
    vendedora = models.ForeignKey(Vendedora, on_delete=models.CASCADE, related_name='acertos')
    numero_pedido = models.CharField(max_length=10)
    data_pedido = models.DateField()
    data_acerto = models.DateField()
    cidade = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    comissao = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Adicione esta linha
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Acerto {self.numero_pedido} - {self.vendedora.nome}"

class ItemAcerto(models.Model):
    acerto = models.ForeignKey(Acerto, on_delete=models.CASCADE, related_name='items')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.acerto.numero_pedido} - {self.produto.nome}"

