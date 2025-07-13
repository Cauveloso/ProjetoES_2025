import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from controler.pedido_controler import PedidoControler
from controler.item_controler import ItemControler

class RelatorioControler:

    @staticmethod
    def preparar_dados_relatorio(database_name: str) -> Dict[str, Any]:
        """
        Coleta e organiza os dados para o relatório.
        """
        try:
            pedidos = PedidoControler.search_in_pedidos_all(database_name)
            if not pedidos:
                return {"pedidos": [], "faturamento_total": 0.0}
            
            dados_relatorio = []
            faturamento_total = 0.0
            
            for pedido in pedidos:
                itens_pedido = ItemControler.search_into_itens_pedidos_id(database_name, pedido['id'])
                
                itens_formatados = []
                for item in itens_pedido:
                    if len(item) >= 4:
                        itens_formatados.append({
                            "id": item[0],
                            "nome": item[1],
                            "quantidade": item[2],
                            "preco_unitario": item[3],
                            "subtotal": item[2] * item[3]
                        })
                
                try:
                    data_pedido = datetime.strptime(pedido['data'], "%Y-%m-%d %H:%M:%S")
                    data_formatada = data_pedido.strftime("%d/%m/%Y %H:%M")
                except:
                    data_formatada = pedido['data']
                
                dados_relatorio.append({
                    "id": pedido['id'],
                    "data": data_formatada,
                    "cliente": pedido['cliente'],
                    "valor": float(pedido['valor_total']),
                    "status": pedido['status'],
                    "itens": itens_formatados
                })
                
                faturamento_total += float(pedido['valor_total'])
            
            return {
                "pedidos": dados_relatorio,
                "faturamento_total": round(faturamento_total, 2)
            }
            
        except Exception as e:
            print(f"Erro ao preparar dados para relatório: {str(e)}")
            return {"pedidos": [], "faturamento_total": 0.0}

    @staticmethod
    def gerar_pdf(nome_arquivo: str, dados: Dict[str, Any]) -> bool:
        """
        Gera um relatório em PDF.
        """
        try:
            pdf = canvas.Canvas(nome_arquivo, pagesize=A4)
            width, height = A4
            
            pdf.setTitle("Relatório de Vendas")
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(100, height - 100, "Relatório de Vendas")
            
            pdf.setFont("Helvetica", 12)
            pdf.drawString(100, height - 130, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            pdf.line(100, height - 140, width - 100, height - 140)
            
            y_position = height - 170
            for pedido in dados["pedidos"]:
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(100, y_position, f"Pedido #{pedido['id']} - {pedido['data']}")
                pdf.drawString(400, y_position, f"R$ {pedido['valor']:.2f}")
                
                pdf.setFont("Helvetica", 10)
                y_position -= 20
                pdf.drawString(120, y_position, f"Cliente: {pedido['cliente']}")
                pdf.drawString(400, y_position, f"Status: {pedido['status'].capitalize()}")
                
                y_position -= 20
                for item in pedido["itens"]:
                    pdf.drawString(140, y_position, 
                                f"{item['quantidade']}x {item['nome']} - R$ {item['preco_unitario']:.2f}")
                    y_position -= 15
                    if y_position < 100:
                        pdf.showPage()
                        y_position = height - 100
                
                y_position -= 15
                if y_position < 150:
                    pdf.showPage()
                    y_position = height - 100
            
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(100, y_position - 30, f"Faturamento Total: R$ {dados['faturamento_total']:.2f}")
            
            pdf.save()
            return True
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {str(e)}")
            return False