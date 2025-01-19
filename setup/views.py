from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse, FileResponse
from .forms import VendedoraForm, ProdutoForm, CustomUserCreationForm, ClienteForm, NovaVendaForm
from .models import Vendedora, Produto, Cliente, EstoqueVendedora, Acerto, ItemAcerto, Compra, ItemCompra
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Sum, Avg, Max, F
from django.db import transaction
from decimal import Decimal
from django.views.decorators.http import require_http_methods
import os
import json


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
    
    valor_total_estoque = produtos.aggregate(
        total=Sum(F('preco') * F('quantidade'))
    )['total'] or 0

    numero_produtos = produtos.count()
    preco_medio = produtos.aggregate(avg_price=Avg('preco'))['avg_price'] or 0
    produto_maior_qtd = produtos.order_by('-quantidade').first()

    for produto in produtos:
        produto.valor_total = produto.preco * produto.quantidade

    context = {
        'produtos': produtos,
        'valor_total_estoque': valor_total_estoque,
        'numero_produtos': numero_produtos,
        'preco_medio': preco_medio,
        'produto_maior_qtd': produto_maior_qtd,
    }

    return render(request, 'estoque.html', context)

@login_required
def atualizar_quantidade_produto(request):
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        nova_quantidade = request.POST.get('quantidade')
        
        try:
            produto = Produto.objects.get(id=produto_id)
            produto.quantidade = int(nova_quantidade)
            produto.save()
            return JsonResponse({'success': True, 'message': 'Quantidade atualizada com sucesso.'})
        except Produto.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Produto não encontrado.'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Quantidade inválida.'})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

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
def clientes(request):
    clientes = Cliente.objects.all()
    form = ClienteForm()
    return render(request, 'clientes.html', {'clientes': clientes, 'form': form})

@login_required
def cadastro_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'success': True,
                'id': cliente.id,
                'nome': cliente.nome,
                'logradouro': cliente.logradouro,
                'bairro': cliente.bairro,
                'cidade': cliente.cidade,
                'uf': cliente.uf,
                'telefone': cliente.telefone,
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'success': True,
                'id': cliente.id,
                'nome': cliente.nome,
                'logradouro': cliente.logradouro,
                'bairro': cliente.bairro,
                'cidade': cliente.cidade,
                'uf': cliente.uf,
                'telefone': cliente.telefone,
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
@require_POST
def excluir_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.delete()
    return JsonResponse({'success': True, 'message': 'Cliente excluído com sucesso'})

@login_required
@require_POST
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    form = ProdutoForm(request.POST, request.FILES, instance=produto)
    if form.is_valid():
        produto = form.save()
        return JsonResponse({
            'success': True,
            'id': produto.id,
            'nome': produto.nome,
            'codigo': produto.codigo,
            'preco': str(produto.preco),
            'quantidade': produto.quantidade,
            'foto_url': produto.foto.url if produto.foto else None
        })
    else:
        return JsonResponse({'success': False, 'errors': form.errors})

@login_required
def novo_acerto(request):
    vendedoras = Vendedora.objects.all()
    return render(request, 'novo_acerto.html', {'vendedoras': vendedoras})

@login_required
def acerto_vendedora(request, vendedora_id=None):
    vendedoras = Vendedora.objects.all()
    context = {'vendedoras': vendedoras}
    
    if vendedora_id:
        vendedora = get_object_or_404(Vendedora, id=vendedora_id)
        estoque_vendedora = EstoqueVendedora.objects.filter(vendedora=vendedora).select_related('produto')
        context.update({
            'vendedora': vendedora,
            'estoque_vendedora': estoque_vendedora,
        })
    
    return render(request, 'acerto_vendedora.html', context)

@login_required
def get_vendedora_info(request):
    vendedora_id = request.GET.get('vendedora_id')
    vendedora = get_object_or_404(Vendedora, id=vendedora_id)
    estoque_vendedora = EstoqueVendedora.objects.filter(vendedora=vendedora).select_related('produto')

    produtos = [
        {
            'id': item.produto.id,
            'nome': item.produto.nome,
            'quantidade': item.quantidade,
            'preco': float(item.produto.preco)
        }
        for item in estoque_vendedora
    ]
    
    produtos_disponiveis = [
        {
            'id': produto.id,
            'nome': produto.nome,
            'preco': float(produto.preco)
        }
        for produto in Produto.objects.all()
    ]
    
    return JsonResponse({
        'id': vendedora.id,
        'nome': vendedora.nome,
        'logradouro': vendedora.logradouro,
        'bairro': vendedora.bairro,
        'cidade': vendedora.cidade,
        'telefone1': vendedora.telefone1,
        'produtos': produtos,
        'produtos_disponiveis': produtos_disponiveis
    })

@require_POST
@login_required
def concluir_acerto(request):
    data = json.loads(request.body)
    
    try:
        with transaction.atomic():
            # Create Acerto
            acerto = Acerto.objects.create(
                vendedora_id=data['vendedora_id'],
                numero_pedido=data['order_number'],
                data_pedido=timezone.now().date(),
                data_acerto=data['data_acerto'],
                cidade=data['cidade'],
                total=Decimal(data['total'])
            )
            
            # Process each item
            for item in data['items']:
                produto = Produto.objects.get(codigo=item['ref'])
                
                # Create ItemAcerto
                ItemAcerto.objects.create(
                    acerto=acerto,
                    produto=produto,
                    quantidade=item['quantity'],
                    valor_unitario=Decimal(item['price']),
                    valor_total=Decimal(item['total'])
                )
                
                # Update product stock
                produto.quantidade -= int(item['quantity'])
                produto.save()
                
                # Update or create EstoqueVendedora
                estoque_vendedora, created = EstoqueVendedora.objects.get_or_create(
                    vendedora_id=data['vendedora_id'],
                    produto=produto,
                    defaults={'quantidade': 0}
                )
                estoque_vendedora.quantidade += int(item['quantity'])
                estoque_vendedora.save()
            
            return JsonResponse({'success': True})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_produto_info(request):
    codigo = request.GET.get('codigo')
    try:
        produto = Produto.objects.get(codigo=codigo)
        return JsonResponse({
            'success': True,
            'id': produto.id,
            'nome': produto.nome,
            'preco': str(produto.preco),
            'quantidade_disponivel': produto.quantidade
        })
    except Produto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Produto não encontrado'
        })

from django.http import JsonResponse
from .models import Cliente, Compra  # Certifique-se de importar o modelo Compra

@login_required
def historico_compras_cliente(request, cliente_id):
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        compras = Compra.objects.filter(cliente=cliente).order_by('-data')
        
        historico = [
            {
                'data': compra.data.strftime('%Y-%m-%d'),
                'valor': float(compra.valor)
            }
            for compra in compras
        ]
        
        return JsonResponse(historico, safe=False)
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


#====================nova venda==========================
@login_required
@require_http_methods(["GET", "POST"])
def nova_venda(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente_id = data.get('cliente_id')
            data_venda = data.get('data_venda')
            produtos = data.get('produtos', [])
            valor_total = data.get('valor_total')

            print(f"Dados recebidos: {data}")  # Log dos dados recebidos

            with transaction.atomic():
                cliente = Cliente.objects.get(id=cliente_id)
                compra = Compra.objects.create(
                    cliente=cliente,
                    data=data_venda,
                    valor_total=valor_total
                )

                for produto_data in produtos:
                    produto = Produto.objects.get(codigo=produto_data['codigo'])
                    ItemCompra.objects.create(
                        compra=compra,
                        produto=produto,
                        quantidade=produto_data['quantidade'],
                        preco_unitario=produto_data['preco_unitario']
                    )
                    # Atualizar o estoque
                    produto.quantidade -= produto_data['quantidade']
                    produto.save()

            return JsonResponse({'success': True, 'message': 'Venda concluída com sucesso!'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)
        except Cliente.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cliente não encontrado'}, status=404)
        except Produto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Produto não encontrado'}, status=404)
        except Exception as e:
            print(f"Erro ao processar venda: {str(e)}")  # Log do erro
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        clientes = Cliente.objects.all()
        produtos = Produto.objects.all()
        context = {
            'clientes': clientes,
            'produtos': produtos,
        }
        return render(request, 'nova_venda.html', context)


def get_produto_info(request, codigo):
    try:
        produto = Produto.objects.get(codigo=codigo)
        return JsonResponse({
            'success': True,
            'nome': produto.nome,
            'preco': float(produto.preco),
            'quantidade_disponivel': produto.quantidade
        })
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produto não encontrado'})


def historico_compras_cliente(request, cliente_id):
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        compras = cliente.historico_compras()
        
        data = []
        for compra in compras:
            data.append({
                'id': compra.id,
                'data': compra.data.strftime('%d/%m/%Y'),
                'valor': float(compra.valor_total),
                'itens': [
                    {
                        'produto': item.produto.nome,
                        'quantidade': item.quantidade,
                        'preco_unitario': float(item.preco_unitario)
                    } for item in compra.itens.all()
                ]
            })
        
        return JsonResponse({'success': True, 'compras': data})
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cliente não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def editar_produto(request, produto_id):
    try:
        produto = Produto.objects.get(id=produto_id)
        produto.nome = request.POST.get('nome')
        produto.codigo = request.POST.get('codigo')
        produto.preco = request.POST.get('preco')
        if 'foto' in request.FILES:
            produto.foto = request.FILES['foto']
        produto.save()
        return JsonResponse({'success': True})
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produto não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def excluir_produto(request, produto_id):
    try:
        produto = Produto.objects.get(id=produto_id)
        produto.delete()
        return JsonResponse({'success': True})
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produto não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

@require_http_methods(["POST"])
def atualizar_preco_produto(request):
    produto_id = request.POST.get('produto_id')
    novo_preco = request.POST.get('novo_preco')
    
    try:
        produto = Produto.objects.get(id=produto_id)
        produto.preco = novo_preco
        produto.save()
        return JsonResponse({'success': True, 'message': 'Preço atualizado com sucesso.'})
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_http_methods(["POST"])
def excluir_produto(request):
    produto_id = request.POST.get('produto_id')
    
    try:
        produto = Produto.objects.get(id=produto_id)
        produto.delete()
        return JsonResponse({'success': True, 'message': 'Produto excluído com sucesso.'})
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_http_methods(["POST"])
def atualizar_produto(request):
    produto_id = request.POST.get('produto_id')
    nome = request.POST.get('nome')
    codigo = request.POST.get('codigo')
    preco = request.POST.get('preco')
    quantidade = request.POST.get('quantidade')
    
    try:
        produto = Produto.objects.get(id=produto_id)
        produto.nome = nome
        produto.codigo = codigo
        produto.preco = preco
        produto.quantidade = quantidade
        produto.save()
        return JsonResponse({
            'success': True, 
            'message': 'Produto atualizado com sucesso.',
            'produto': {
                'nome': produto.nome,
                'codigo': produto.codigo,
                'preco': float(produto.preco),
                'quantidade': produto.quantidade
            }
        })
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})