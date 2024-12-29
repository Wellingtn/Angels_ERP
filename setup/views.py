from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse, FileResponse
from .forms import VendedoraForm, ProdutoForm, CustomUserCreationForm
from .models import Vendedora, Produto, Cliente
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
import os
from django.conf import settings
from django.utils import timezone

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

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

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def estoque(request):
    produtos = Produto.objects.all()
    return render(request, 'estoque.html', {'produtos': produtos})

@login_required
def catalogo(request):
    produtos = Produto.objects.all()
    return render(request, 'catalogo.html', {'produtos': produtos})

@login_required
def vendedoras(request):
    vendedoras = Vendedora.objects.all()
    return render(request, 'vendedoras.html', {'vendedoras': vendedoras})

@login_required
def detalhes_vendedora(request, vendedora_id):
    vendedora = get_object_or_404(Vendedora, id=vendedora_id)
    return render(request, 'detalhes_vendedora.html', {'vendedora': vendedora})

@login_required
def cadastro_vendedora(request):
    if request.method == 'POST':
        form = VendedoraForm(request.POST, request.FILES)
        if form.is_valid():
            vendedora = form.save()
            
            # Gerar o contrato
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=18)
            
            Story = []
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Justify', alignment=4))
            
            title = 'CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE VENDEDORA AUTÔNOMA'
            Story.append(Paragraph(title, styles['Title']))
            Story.append(Spacer(1, 12))
            
            ptext = f'''
            Pelo presente instrumento particular de contrato de prestação de serviços, de um lado {vendedora.nome}, 
            residente e domiciliada em {vendedora.logradouro}, {vendedora.bairro}, {vendedora.cidade} - {vendedora.uf}, 
            doravante denominada CONTRATADA, e de outro lado ANGELS LINGERIE, pessoa jurídica de direito privado, 
            inscrita no CNPJ sob o nº XX.XXX.XXX/XXXX-XX, com sede na Rua XXXXXX, nº XXX, Bairro XXXXX, 
            Cidade XXXXX - XX, doravante denominada CONTRATANTE, têm entre si justo e contratado o seguinte:
            '''
            Story.append(Paragraph(ptext, styles['Justify']))
            Story.append(Spacer(1, 12))
            
            ptext = '1. OBJETO DO CONTRATO'
            Story.append(Paragraph(ptext, styles['Heading2']))
            ptext = '''1.1 O presente contrato tem como objeto a prestação de serviços de vendedora autônoma pela CONTRATADA 
            à CONTRATANTE, para a comercialização dos produtos da marca Angels Lingerie.'''
            Story.append(Paragraph(ptext, styles['Justify']))
            Story.append(Spacer(1, 12))
            
            ptext = '2. OBRIGAÇÕES DA CONTRATADA'
            Story.append(Paragraph(ptext, styles['Heading2']))
            ptext = '''2.1 A CONTRATADA se compromete a:
            a) Comercializar os produtos da CONTRATANTE com zelo e dedicação;
            b) Cumprir as metas de vendas estabelecidas pela CONTRATANTE;
            c) Participar de treinamentos e reuniões quando solicitado pela CONTRATANTE;
            d) Zelar pela imagem e reputação da marca Angels Lingerie;
            e) Prestar contas das vendas realizadas conforme acordado com a CONTRATANTE.'''
            Story.append(Paragraph(ptext, styles['Justify']))
            Story.append(Spacer(1, 12))
            
            ptext = '3. OBRIGAÇÕES DA CONTRATANTE'
            Story.append(Paragraph(ptext, styles['Heading2']))
            ptext = '''3.1 A CONTRATANTE se compromete a:
            a) Fornecer os produtos para comercialização;
            b) Oferecer treinamento e suporte necessários para a realização das vendas;
            c) Pagar as comissões devidas à CONTRATADA conforme acordado.'''
            Story.append(Paragraph(ptext, styles['Justify']))
            Story.append(Spacer(1, 12))
            
            ptext = '4. REMUNERAÇÃO'
            Story.append(Paragraph(ptext, styles['Heading2']))
            ptext = '''4.1 A CONTRATADA receberá comissão sobre as vendas realizadas, conforme percentual acordado entre as partes.
            4.2 O pagamento das comissões será realizado mensalmente, até o 5º dia útil do mês subsequente às vendas.'''
            Story.append(Paragraph(ptext, styles['Justify']))
            Story.append(Spacer(1, 12))
            
            ptext = '5. PRAZO'
            Story.append(Paragraph(ptext, styles['Heading2']))
            ptext = '''5.1 O presente contrato tem prazo indeterminado, podendo ser rescindido por qualquer das partes mediante 
            aviso prévio de 30 (trinta) dias.'''
            Story.append(Paragraph(ptext, styles['Justify']))
            Story.append(Spacer(1, 12))
            
            ptext = '6. DISPOSIÇÕES GERAIS'
            Story.append(Paragraph(ptext, styles['Heading2']))
            ptext = '''6.1 A CONTRATADA declara-se ciente de que o presente contrato não gera vínculo empregatício entre as partes.
            6.2 Qualquer modificação neste contrato só terá validade se feita por escrito e assinada por ambas as partes.'''
            Story.append(Paragraph(ptext, styles['Justify']))
            Story.append(Spacer(1, 12))
            
            ptext = f'''E, por estarem assim justas e contratadas, as partes assinam o presente instrumento em duas vias de igual 
            teor e forma, na presença das testemunhas abaixo.

            {vendedora.cidade}, {timezone.now().strftime("%d de %B de %Y")}.

            _______________________________
            CONTRATADA: {vendedora.nome}

            _______________________________
            CONTRATANTE: ANGELS LINGERIE

            TESTEMUNHAS:
            1. ____________________________
            Nome:
            CPF:

            2. ____________________________
            Nome:
            CPF:'''
            Story.append(Paragraph(ptext, styles['Justify']))
            
            doc.build(Story)
            
            buffer.seek(0)
            
            # Salvar o contrato no campo 'contrato' da vendedora
            vendedora.contrato.save(f'contrato_{vendedora.id}.pdf', BytesIO(buffer.getvalue()))
            vendedora.save()
            
            # Retornar o PDF diretamente
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename=contrato_{vendedora.nome}.pdf'
            return response
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@login_required
def download_contrato(request, vendedora_id):
    vendedora = get_object_or_404(Vendedora, id=vendedora_id)
    if vendedora.contrato:
        return FileResponse(vendedora.contrato, as_attachment=True, filename=f'contrato_{vendedora.nome}.pdf')
    return HttpResponse("Contrato não encontrado", status=404)

@login_required
def cadastro_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save()
            return JsonResponse({
                'success': True,
                'id': produto.id,
                'nome': produto.nome,
                'codigo': produto.codigo,
                'preco': str(produto.preco),
                'foto_url': produto.foto.url if produto.foto else None
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
def atualizar_quantidade_produto(request):
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        quantidade = request.POST.get('quantidade')
        try:
            produto = Produto.objects.get(id=produto_id)
            produto.quantidade = quantidade
            produto.save()
            return JsonResponse({'success': True})
        except Produto.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Produto não encontrado'})
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
def clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes.html', {'clientes': clientes})

@login_required
def cadastro_cliente(request):
    if request.method == 'POST':
        # Implement client registration logic here
        pass
    return render(request, 'cadastro_cliente.html')

@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        # Implement client editing logic here
        pass
    return render(request, 'editar_cliente.html', {'cliente': cliente})

@login_required
def excluir_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        cliente.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

