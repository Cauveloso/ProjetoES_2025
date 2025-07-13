import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Configuração de imports e caminhos
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from controler.pedido_controler import PedidoControler
from controler.item_controler import ItemControler

class RelatorioControler:
    
    # ==================== PREPARAÇÃO DE DADOS ====================
    
    @staticmethod
    def preparar_dados_relatorio(database_name: str) -> Dict[str, Any]:
        """
        Coleta e organiza dados de pedidos para geração de relatórios
        
        Args:
            database_name: Nome do arquivo do banco de dados
            
        Returns:
            Dicionário contendo:
            - pedidos: Lista de dicionários com informações dos pedidos
            - faturamento_total: Valor total acumulado dos pedidos
        """
        try:
            # Obtém todos os pedidos, incluindo os entregues
            pedidos = PedidoControler.search_in_pedidos_all(database_name, incluir_entregues=True)
            
            if not pedidos:
                return {"pedidos": [], "faturamento_total": 0.0}
            
            dados_relatorio = []
            faturamento_total = 0.0
            
            for pedido in pedidos:
                if not isinstance(pedido, dict):
                    continue
                    
                # Obtém valor do pedido com tratamento para diferentes nomes de campo
                valor_pedido = float(pedido.get('total') or pedido.get('valor_total') or 0.0)
                
                # Obtém itens associados ao pedido
                itens_pedido = ItemControler.search_into_itens_pedidos_id(database_name, pedido.get('id')) or []

                # Formata os itens do pedido
                itens_formatados = []
                for item in itens_pedido:
                    try:
                        if len(item) >= 4:  # Verifica se tem todos os campos necessários
                            itens_formatados.append({
                                "id": item[0],
                                "nome": item[1],
                                "quantidade": item[2],
                                "preco_unitario": item[3],
                                "subtotal": item[2] * item[3]
                            })
                    except (IndexError, TypeError):
                        continue
                
                # Formata a data do pedido
                try:
                    data_formatada = datetime.strptime(
                        pedido.get('data', ''), 
                        "%Y-%m-%d %H:%M:%S"
                    ).strftime("%d/%m/%Y %H:%M")
                except (ValueError, AttributeError):
                    data_formatada = str(pedido.get('data', 'Data inválida'))
                
                # Adiciona pedido formatado à lista
                dados_relatorio.append({
                    "id": pedido.get('id', 0),
                    "data": data_formatada,
                    "cliente": pedido.get('cliente', 'Cliente não informado'),
                    "valor": valor_pedido,
                    "status": pedido.get('status', 'Status desconhecido'),
                    "itens": itens_formatados
                })
                
                faturamento_total += valor_pedido
            
            return {
                "pedidos": dados_relatorio,
                "faturamento_total": round(faturamento_total, 2)
            }
            
        except Exception as e:
            print(f"Erro ao preparar dados para relatório: {str(e)}")
            return {"pedidos": [], "faturamento_total": 0.0}

    # ==================== VERIFICAÇÃO DE DADOS ====================
    
    @staticmethod
    def verificar_dados_relatorio(database_name: str) -> None:
        """
        Realiza diagnóstico dos dados para identificar possíveis problemas
        
        Args:
            database_name: Nome do arquivo do banco de dados
            
        Returns:
            None (os resultados são impressos no console)
        """
        try:
            print("\n=== VERIFICAÇÃO DE DADOS ===")
            
            # Obtém pedidos ativos (não entregues)
            pedidos_ativos = PedidoControler.search_in_pedidos_all(database_name, incluir_entregues=False)
            print(f"Pedidos ativos (não entregues): {len(pedidos_ativos)}")
            
            # Obtém todos os pedidos (incluindo entregues)
            todos_pedidos = PedidoControler.search_in_pedidos_all(database_name, incluir_entregues=True)
            print(f"Total de pedidos realizados: {len(todos_pedidos)}")
            
            # Filtra pedidos entregues
            pedidos_entregues = [p for p in todos_pedidos if p.get('status') == 'entregue']
            print(f"Pedidos entregues: {len(pedidos_entregues)}")
            
            print("\n=== FIM DA VERIFICAÇÃO ===")
            input("Pressione Enter para continuar...")
            
        except Exception as e:
            print(f"Erro durante a verificação de dados: {str(e)}")

    # ==================== GERAÇÃO DE PDF ====================
    
    @staticmethod
    def gerar_pdf(nome_arquivo: str, dados: Dict[str, Any]) -> bool:
        """
        Gera um relatório em PDF com os dados fornecidos
        
        Args:
            nome_arquivo: Caminho/nome do arquivo PDF a ser gerado
            dados: Dicionário contendo os dados do relatório
            
        Returns:
            bool: True se o PDF foi gerado com sucesso, False caso contrário
        """
        try:
            # Validação dos dados de entrada
            if not dados or not isinstance(dados, dict):
                raise ValueError("Dados inválidos para geração de PDF")
                
            if not dados.get("pedidos"):
                print("⚠️ Nenhum pedido encontrado para gerar relatório")
                return False

            # Configuração inicial do PDF
            pdf = canvas.Canvas(nome_arquivo, pagesize=A4)
            width, height = A4
            
            # Cabeçalho do relatório
            pdf.setTitle("Relatório de Vendas")
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(100, height - 100, "Relatório de Vendas")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(100, height - 130, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            pdf.line(100, height - 140, width - 100, height - 140)
            
            # Variável para controlar a posição vertical no PDF
            y_position = height - 170
            
            # Adiciona cada pedido ao PDF
            for pedido in dados["pedidos"]:
                try:
                    # Cabeçalho do pedido
                    pdf.setFont("Helvetica-Bold", 12)
                    pdf.drawString(100, y_position, f"Pedido #{pedido.get('id', 'N/A')}")
                    pdf.drawString(400, y_position, f"R$ {pedido.get('valor', 0):.2f}")
                    
                    # Detalhes do pedido
                    pdf.setFont("Helvetica", 10)
                    y_position -= 20
                    pdf.drawString(120, y_position, f"Cliente: {pedido.get('cliente', 'Não informado')}")
                    
                    # Itens do pedido
                    y_position -= 20
                    for item in pedido.get("itens", []):
                        pdf.drawString(
                            140, y_position, 
                            f"{item.get('quantidade', 0)}x {item.get('nome', 'Item sem nome')} - R$ {item.get('preco_unitario', 0):.2f}"
                        )
                        y_position -= 15
                        
                        # Verifica se precisa criar nova página
                        if y_position < 100:
                            pdf.showPage()
                            y_position = height - 100
                            pdf.setFont("Helvetica", 10)  # Mantém o estilo após nova página
                    
                    y_position -= 15  # Espaço entre pedidos
                    
                except Exception as e:
                    print(f"⚠️ Erro ao processar pedido {pedido.get('id')}: {str(e)}")
                    continue
            
            # Rodapé com total faturado
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(100, y_position - 30, f"Total Faturado: R$ {dados.get('faturamento_total', 0):.2f}")
            
            # Finaliza e salva o PDF
            pdf.save()
            print(f"✅ Relatório PDF gerado com sucesso: '{nome_arquivo}'")
            return True
            
        except Exception as e:
            print(f"❌ Falha crítica ao gerar PDF: {str(e)}")
            return False