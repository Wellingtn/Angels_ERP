from django import forms
from django.forms import inlineformset_factory
from .models import Compra, ItemCompra, Cliente, Produto, Vendedora

class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)

class CustomAuthenticationForm(forms.Form):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

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

class NovaVendaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), empty_label="Selecione um cliente")
    produtos = forms.ModelMultipleChoiceField(queryset=Produto.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Compra
        fields = ['cliente', 'data', 'valor_total']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_compra_formset = inlineformset_factory(
            Compra, ItemCompra, fields=('produto', 'quantidade', 'preco_unitario'), extra=1
        )

    def save(self, commit=True):
        compra = super().save(commit=False)
        if commit:
            compra.save()
            self.item_compra_formset.instance = compra
            self.item_compra_formset.save()
        return compra

