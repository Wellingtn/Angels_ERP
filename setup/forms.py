from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Vendedora, Cliente, Produto

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2', 'profile_picture')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))

class VendedoraForm(forms.ModelForm):
    class Meta:
        model = Vendedora
        fields = ['nome', 'foto', 'logradouro', 'bairro', 'cidade', 'uf', 'telefone1', 'telefone2', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Vendedora'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Logradouro'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'uf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF'}),
            'telefone1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone 1'}),
            'telefone2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone 2'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Observações', 'rows': 3}),
        }


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['codigo', 'nome', 'foto', 'preco', 'quantidade']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código do Produto'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Produto'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade Inicial'}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'logradouro', 'bairro', 'cidade', 'uf', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Cliente'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Logradouro'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'uf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'}),
        }
