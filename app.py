import streamlit as st

html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Fatura de Cessão de Espaço - Instituto Ser Consciente</title>
    <style>
        @page {
            size: A4;
            margin: 15mm 15mm;
            background-color: #ffffff;
        }
        *, *::before, *::after {
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 11pt;
            color: #222222;
            margin: 0;
            padding: 0;
            line-height: 1.25;
        }
        .invoice-box {
            background: #ffffff;
            padding: 10px;
            margin: 0 auto;
        }
        .header {
            border-bottom: 2px solid #333333;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .header table {
            width: 100%;
            border-collapse: collapse;
        }
        .header td {
            vertical-align: top;
        }
        .clinic-name {
            font-size: 16pt;
            font-weight: bold;
            color: #1a365d;
            margin-bottom: 4px;
        }
        .clinic-info {
            font-size: 9pt;
            color: #555555;
        }
        .invoice-title {
            text-align: right;
            font-size: 14pt;
            font-weight: bold;
            color: #2c5282;
        }
        .invoice-number {
            text-align: right;
            font-size: 10pt;
            color: #666666;
            margin-top: 4px;
        }
        .section-title {
            font-size: 12pt;
            font-weight: bold;
            background-color: #edf2f7;
            color: #2d3748;
            padding: 6px 8px;
            margin-top: 15px;
            margin-bottom: 8px;
            border-left: 4px solid #3182ce;
        }
        table.data-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        table.data-table th, table.data-table td {
            border: 1px solid #cbd5e0;
            padding: 8px 10px;
            text-align: left;
            font-size: 10pt;
        }
        table.data-table th {
            background-color: #f7fafc;
            color: #2d3748;
            font-weight: bold;
        }
        table.data-table td.num, table.data-table th.num {
            text-align: right;
        }
        .total-section {
            float: right;
            width: 280px;
            margin-bottom: 20px;
        }
        .total-table {
            width: 100%;
            border-collapse: collapse;
        }
        .total-table td {
            border: 1px solid #cbd5e0;
            padding: 8px;
            font-size: 11pt;
        }
        .total-table td.label {
            font-weight: bold;
            background-color: #f7fafc;
        }
        .total-table td.value {
            text-align: right;
            font-weight: bold;
            color: #2c5282;
        }
        .clear {
            clear: both;
        }
        .payment-container {
            margin-top: 25px;
            max-width: 350px;
            margin-left: auto;
            margin-right: auto;
        }
        .pix-section {
            border: 1px solid #cbd5e0;
            padding: 15px;
            text-align: center;
            background-color: #f7fafc;
        }
        .qrcode-box {
            width: 130px;
            height: 130px;
            margin: 0 auto 10px auto;
            border: 1px solid #a0aec0;
            background-color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8pt;
            color: #718096;
            text-align: center;
        }
        .instructions {
            margin-top: 20px;
            font-size: 9pt;
            color: #718096;
            line-height: 1.4;
        }
    </style>
</head>
<body>

    <div class="invoice-box">
        <div class="header">
            <table>
                <tr>
                    <td>
                        <div class="clinic-name">Instituto Ser Consciente Ltda</div>
                        <div class="clinic-info">CNPJ: 04.000.917/0001-47</div>
                        <div class="clinic-info">Rua Inconfidentes, Contagem - MG</div>
                    </td>
                    <td>
                        <div class="invoice-title">FATURA DE CESSÃO DE ESPAÇO</div>
                        <div class="invoice-number">Nº 2026/0402</div>
                        <div class="invoice-number">Data de Emissão: 08/09/2026</div>
                        <div class="invoice-number">Vencimento: 15/09/2026</div>
                    </td>
                </tr>
            </table>
        </div>

        <div class="section-title">Dados do Profissional / Colaborador</div>
        <table class="data-table">
            <tr>
                <th style="width: 25%;">Nome / Razão Social:</th>
                <td style="width: 75%;">Dr(a). Profissional Colaborador(a)</td>
            </tr>
            <tr>
                <th>Natureza da Operação:</th>
                <td>Cessão de Espaço Físico e Apoio Administrativo</td>
            </tr>
        </table>

        <div class="section-title">Discriminação da Cessão</div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Descrição do Item</th>
                    <th class="num" style="width: 15%;">Qtd / Blocos</th>
                    <th class="num" style="width: 20%;">Valor por Bloco</th>
                    <th class="num" style="width: 20%;">Total</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Cessão de Espaço para Atendimento Ambulatorial (Bloco de Horários)</td>
                    <td class="num">1</td>
                    <td class="num">R$ 300,00</td>
                    <td class="num">R$ 300,00</td>
                </tr>
            </tbody>
        </table>

        <div class="total-section">
            <table class="total-table">
                <tr>
                    <td class="label">Valor Total da Cessão:</td>
                    <td class="value">R$ 300,00</td>
                </tr>
            </table>
        </div>
        <div class="clear"></div>

        <div class="payment-container">
            <div class="pix-section">
                <div style="font-size: 9pt; font-weight: bold; color: #2d3748; margin-bottom: 8px;">PAGAMENTO VIA PIX (QR CODE ESTÁTICO)</div>
                <div class="qrcode-box">
                    <!-- Substituir pela tag <img> com o base64 ou link do QR Code real -->
                    [QR CODE PIX]
                </div>
                <div style="font-size: 9pt; color: #4a5568;">Chave Pix (CNPJ): <strong>04.000.917/0001-47</strong></div>
                <div style="font-size: 8pt; color: #718096; margin-top: 3px;">Instituto Ser Consciente Ltda</div>
            </div>
        </div>

        <div class="instructions">
            <strong>Instruções e Regras de Operação:</strong><br>
            Documento referente exclusivamente à cessão de espaço e infraestrutura para atendimento, conforme normas internas da instituição.<br>
            Pagamento realizado diretamente via Pix utilizando a chave CNPJ informada acima.
        </div>
    </div>

</body>
</html>
"""

st.markdown(html_content, unsafe_allow_html=True)
