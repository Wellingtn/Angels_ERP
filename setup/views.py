from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, VendedoraForm
from .models import Vendedora

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
def estoque(request):
    return render(request, 'estoque.html')

@login_required
def catalogo(request):
    return render(request, 'catalogo.html')

@login_required
def vendedoras(request):
    vendedoras = Vendedora.objects.all()
    return render(request, 'vendedoras.html', {'vendedoras': vendedoras})

@login_required
def cadastro_vendedora(request):
    if request.method == 'POST':
        form = VendedoraForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Formulário inválido. Verifique os dados.'})
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
def clientes(request):
    return render(request, 'clientes.html')

@login_required
def detalhes_vendedora(request, vendedora_id):
    vendedora = get_object_or_404(Vendedora, id=vendedora_id)
    return render(request, 'detalhes_vendedora.html', {'vendedora': vendedora})

