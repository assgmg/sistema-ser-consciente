import streamlit as st
import streamlit.components.v1 as components

html_content = """
<div style="font-family: Arial, sans-serif; font-size: 11pt; color: #222222; max-width: 800px; margin: 0 auto; background: #ffffff; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
    
    <div style="border-bottom: 2px solid #333333; padding-bottom: 10px; margin-bottom: 15px;">
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="vertical-align: top;">
                    <div style="font-size: 16pt; font-weight: bold; color: #1a365d; margin-bottom: 4px;">Instituto Ser Consciente Ltda</div>
                    <div style="font-size: 9pt; color: #555555;">CNPJ: 04.000.917/0001-47</div>
                    <div style="font-size: 9pt; color: #555555;">Rua Inconfidentes, Contagem - MG</div>
                </td>
                <td style="vertical-align: top; text-align: right;">
                    <div style="font-size: 14pt; font-weight: bold; color: #2c5282;">FATURA DE CESSÃO DE ESPAÇO</div>
                    <div style="font-size: 10pt; color: #666666; margin-top: 4px;">Nº 2026/0402</div>
                    <div style="font-size: 10pt; color: #666666; margin-top: 2px;">Data de Emissão: 08/09/2026</div>
                    <div style="font-size: 10pt; color: #666666; margin-top: 2px;">Vencimento: 15/09/2026</div>
                </td>
            </tr>
        </table>
    </div>

    <div style="font-size: 12pt; font-weight: bold; background-color: #edf2f7; color: #2d3748; padding: 6px 8px; margin-top: 15px; margin-bottom: 8px; border-left: 4px solid #3182ce;">Dados do Profissional / Colaborador</div>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
        <tr>
            <th style="width: 25%; border: 1px solid #cbd5e0; padding: 8px 10px; text-align: left; font-size: 10pt; background-color: #f7fafc; color: #2d3748;">Nome / Razão Social:</th>
            <td style="width: 75%; border: 1px solid #cbd5e0; padding: 8px 10px; text-align: left; font-size: 10pt;">Dr(a). Profissional Colaborador(a)</td>
        </tr>
        <tr>
            <th style="border: 1px solid #cbd5e0; padding: 8px 10px; text-align: left; font-size: 10pt; background-color: #f7fafc; color: #2d3748;">Natureza da Operação:</th>
            <td style="border: 1px solid #cbd5e0; padding: 8px 10px; text-align: left; font-size: 10pt;">Cessão de Espaço Físico e Apoio Administrativo</td>
        </tr>
    </table>

    <div style="font-size: 12pt; font-weight: bold; background-color: #edf2f7; color: #2d3748; padding: 6px 8px; margin-top: 15px; margin-bottom: 8px; border-left: 4px solid #3182ce;">Discriminação da Cessão</div>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
        <thead>
            <tr>
                <th style="border: 1px solid #cbd5e0; padding: 8px 10px; text-align: left; font-size: 10pt; background-color: #f7fafc; color: #2d3748;">Descrição do Item</th>
                <th style="border: 1px solid #cbd5e0; padding: 8px 10px; text-align: right; font-size: 10pt; background-color: #f7fafc; color: #2d3748; width: 15%;">Qtd / Blocos</th>
                <th style="border: 1px solid #cbd5e0; padding: 8px 10px; text-align: right; font-size: 10pt; background-color: #f7fafc; color: #2d3748; width: 20%;">Valor por Bloco</th>
                <th style="border: 1px solid #cbd5e0; padding: 8px 10px; text-align: right; font-size: 10pt; background-color: #f7fafc; color: #2d3748; width: 20%;">Total</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid #cbd5e0; padding: 8px 10px; font-size: 10pt;">Cessão de Espaço para Atendimento Ambulatorial (Bloco de Horários)</td>
                <td style="border: 1px solid #cbd5e0; padding: 8px 10px; text-align: right; font-size: 10pt;">1</td>
                <td style="border: 1px solid #cbd5e0; padding: 8px 10px; text-align: right; font-size: 10pt;">R$ 300,00</td>
                <td style="border: 1px solid #cbd5e0; padding: 8px 10px; text-align: right; font-size: 10pt;">R$ 300,00</td>
            </tr>
        </tbody>
    </table>

    <div style="float: right; width: 280px; margin-bottom: 20px;">
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="border: 1px solid #cbd5e0; padding: 8px; font-size: 11pt; font-weight: bold; background-color: #f7fafc;">Valor Total da Cessão:</td>
                <td style="border: 1px solid #cbd5e0; padding: 8px; font-size: 11pt; font-weight: bold; text-align: right; color: #2c5282;">R$ 300,00</td>
            </tr>
        </table>
    </div>
    <div style="clear: both;"></div>

    <div style="margin-top: 25px; max-width: 350px; margin-left: auto; margin-right: auto;">
        <div style="border: 1px solid #cbd5e0; padding: 15px; text-align: center; background-color: #f7fafc; border-radius: 6px;">
            <div style="font-size: 9pt; font-weight: bold; color: #2d3748; margin-bottom: 8px;">PAGAMENTO VIA PIX (QR CODE ESTÁTICO)</div>
            <div style="width: 130px; height: 130px; margin: 0 auto 10px auto; border: 1px solid #a0aec0; background-color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 8pt; color: #718096; line-height: 130px; text-align: center;">
                [QR CODE PIX]
            </div>
            <div style="font-size: 9pt; color: #4a5568;">Chave Pix (CNPJ): <strong>04.000.917/0001-47</strong></div>
            <div style="font-size: 8pt; color: #718096; margin-top: 3px;">Instituto Ser Consciente Ltda</div>
        </div>
    </div>

    <div style="margin-top: 20px; font-size: 9pt; color: #718096; line-height: 1.4;">
        <strong>Instruções e Regras de Operação:</strong><br>
        Documento referente exclusivamente à cessão de espaço e infraestrutura para atendimento, conforme normas internas da instituição.<br>
        Pagamento realizado diretamente via Pix utilizando a chave CNPJ informada acima.
    </div>

</div>
"""

components.html(html_content, height=750, scrolling=True)
