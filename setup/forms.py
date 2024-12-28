from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Vendedora

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

class VendedoraUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

class VendedoraRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Vendedora
        fields = ['nome', 'foto', 'logradouro', 'bairro', 'cidade', 'uf', 'telefone1', 'telefone2', 'observacoes', 'email', 'username', 'password']

    def save(self, commit=True):
        user_data = {
            'email': self.cleaned_data['email'],
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password'],
        }
        user = CustomUser.objects.create_user(**user_data)
        
        vendedora = super().save(commit=False)
        vendedora.user = user
        if commit:
            vendedora.save()
        return vendedora

