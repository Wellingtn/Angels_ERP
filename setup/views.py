import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Sum, Avg, Max, F
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.template.defaultfilters import register

from decimal import Decimal
from io import BytesIO
import os

from .forms import VendedoraForm, ProdutoForm, CustomUserCreationForm, ClienteForm, NovaVendaForm
from .models import Vendedora, Produto, Cliente, EstoqueVendedora, Acerto, ItemAcerto, Compra, ItemCompra

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


register.filter('multiply', lambda value, arg: value * arg)

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

def detalhes_vendedora(request, vendedora_id):
    vendedora = get_object_or_404(Vendedora, id=vendedora_id)
    estoque_vendedora = EstoqueVendedora.objects.filter(vendedora=vendedora).select_related('produto')
    acertos = Acerto.objects.filter(vendedora=vendedora).order_by('-data_acerto')

    context = {
        'vendedora': vendedora,
        'estoque_vendedora': estoque_vendedora,
        'acertos': acertos,
    }
    return render(request, 'detalhes_vendedora.html', context)

@login_required
def cadastro_vendedora(request):
    if request.method == 'POST':
        form = VendedoraForm(request.POST, request.FILES)
        if form.is_valid():
            vendedora = form.save()
            
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
            
            vendedora.contrato.save(f'contrato_{vendedora.id}.pdf', BytesIO(buffer.getvalue()))
            vendedora.save()
            
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

@transaction.atomic
def concluir_acerto(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        vendedora_id = data['vendedora_id']
        data_acerto = data['data_acerto']
        produtos_vendedora = data['produtos_vendedora']
        novos_produtos = data['novos_produtos']
        comissao = data['comissao']
        total_acerto = data['total_acerto']

        try:
            vendedora = Vendedora.objects.get(id=vendedora_id)
            
            # Converter comissao e total_acerto para Decimal
            comissao = Decimal(comissao) if comissao else Decimal('0')
            total_acerto = Decimal(total_acerto) if total_acerto else Decimal('0')

            # Criar novo acerto
            acerto = Acerto.objects.create(
                vendedora=vendedora,
                data_acerto=data_acerto,
                comissao=comissao,
                total=total_acerto,
                numero_pedido=f"A{vendedora_id}-{data_acerto}",  # Gerar um número de pedido único
                data_pedido=data_acerto,  # Usar a mesma data do acerto como data do pedido
                cidade=vendedora.cidade  # Usar a cidade da vendedora
            )

            # Processar produtos vendidos e devolvidos
            for produto in produtos_vendedora:
                try:
                    estoque_item = EstoqueVendedora.objects.get(vendedora=vendedora, produto_id=produto['id'])
                    quantidade_vendida = int(produto['quantidade_vendida'])
                    quantidade_devolvida = int(produto['quantidade_devolvida'])

                    # Atualizar estoque da vendedora
                    estoque_item.quantidade -= (quantidade_vendida + quantidade_devolvida)
                    estoque_item.save()

                    # Atualizar estoque geral
                    produto_obj = estoque_item.produto
                    produto_obj.quantidade += quantidade_devolvida
                    produto_obj.save()

                    # Registrar item do acerto
                    ItemAcerto.objects.create(
                        acerto=acerto,
                        produto=produto_obj,
                        quantidade=quantidade_vendida,  # Usamos quantidade_vendida aqui
                        valor_unitario=produto_obj.preco,
                        valor_total=Decimal(quantidade_vendida) * produto_obj.preco
                    )
                except EstoqueVendedora.DoesNotExist:
                    print(f"Erro: Produto {produto['id']} não encontrado no estoque da vendedora {vendedora_id}")
                except Exception as e:
                    print(f"Erro ao processar produto {produto['id']}: {str(e)}")

            # Processar novos produtos
            for novo_produto in novos_produtos:
                try:
                    produto_obj = Produto.objects.get(id=novo_produto['id'])
                    quantidade = int(novo_produto['quantidade'])

                    # Atualizar estoque da vendedora
                    EstoqueVendedora.objects.update_or_create(
                        vendedora=vendedora,
                        produto=produto_obj,
                        defaults={'quantidade': F('quantidade') + quantidade}
                    )

                    # Atualizar estoque geral
                    produto_obj.quantidade -= quantidade
                    produto_obj.save()

                    # Registrar item do acerto
                    ItemAcerto.objects.create(
                        acerto=acerto,
                        produto=produto_obj,
                        quantidade=quantidade,
                        valor_unitario=produto_obj.preco,
                        valor_total=Decimal(quantidade) * produto_obj.preco
                    )
                except Produto.DoesNotExist:
                    print(f"Erro: Novo produto {novo_produto['id']} não encontrado")
                except Exception as e:
                    print(f"Erro ao processar novo produto {novo_produto['id']}: {str(e)}")

            return JsonResponse({'success': True, 'message': 'Acerto concluído com sucesso.'})
        except Vendedora.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'Vendedora com ID {vendedora_id} não encontrada.'}, status=404)
        except Exception as e:
            print(f"Erro ao concluir acerto: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Método não permitido.'}, status=405)

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
                'id': produto.id,
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

@require_http_methods(["POST"])
def atualizar_vendedora(request):
    try:
        data = json.loads(request.body)
        vendedora_id = data.get('id')
        vendedora = get_object_or_404(Vendedora, id=vendedora_id)
        
        vendedora.nome = data.get('nome', vendedora.nome)
        vendedora.telefone1 = data.get('telefone1', vendedora.telefone1)
        vendedora.telefone2 = data.get('telefone2', vendedora.telefone2)
        vendedora.email = data.get('email', vendedora.email)
        vendedora.bairro = data.get('bairro', vendedora.bairro)
        vendedora.cidade = data.get('cidade', vendedora.cidade)
        vendedora.uf = data.get('uf', vendedora.uf)
        
        vendedora.save()
        
        return JsonResponse({'success': True, 'message': 'Informações da vendedora atualizadas com sucesso.'})
    except Vendedora.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Vendedora não encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def get_acerto_details(request, acerto_id):
    try:
        acerto = Acerto.objects.get(id=acerto_id)
        itens = acerto.itemacerto_set.all().select_related('produto')
        
        data = {
            'data_acerto': acerto.data_acerto.strftime('%d/%m/%Y'),
            'comissao': float(acerto.comissao),
            'total': float(acerto.total),
            'itens': [
                {
                    'produto': item.produto.nome,
                    'quantidade_vendida': item.quantidade_vendida,
                    'quantidade_devolvida': item.quantidade_devolvida,
                    'quantidade_adicionada': item.quantidade_adicionada,
                    'preco_unitario': float(item.preco_unitario)
                }
                for item in itens
            ]
        }
        return JsonResponse(data)
    except Acerto.DoesNotExist:
        return JsonResponse({'error': 'Acerto não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_produtos_vendedora(request, vendedora_id):
    try:
        estoque_vendedora = EstoqueVendedora.objects.filter(vendedora_id=vendedora_id).select_related('produto')
        produtos = [
            {
                'id': item.produto.id,
                'nome': item.produto.nome,
                'quantidade': item.quantidade,
                'preco': float(item.produto.preco)
            }
            for item in estoque_vendedora
        ]
        return JsonResponse(produtos, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_acerto_details(request, acerto_id):
    try:
        acerto = Acerto.objects.get(id=acerto_id)
        itens = acerto.items.all().select_related('produto')
        
        data = {
            'data_acerto': acerto.data_acerto.strftime('%d/%m/%Y'),
            'comissao': float(acerto.comissao),
            'total': float(acerto.total),
            'status': 'Concluído',  # Você pode ajustar isso se tiver um campo de status no modelo Acerto
            'itens': [
                {
                    'produto': item.produto.nome,
                    'quantidade': item.quantidade,
                    'valor_unitario': float(item.valor_unitario),
                    'valor_total': float(item.valor_total)
                }
                for item in itens
            ]
        }
        return JsonResponse(data)
    except Acerto.DoesNotExist:
        return JsonResponse({'error': 'Acerto não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)