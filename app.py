import io
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st

# --- LÓGICA DE EXPORTAÇÃO PARA PDF COMPLETA ---
# Adicione ou substitua o bloco de exportação do PDF pelo código abaixo:

pdf_buffer = io.BytesIO()
doc = SimpleDocTemplate(
    pdf_buffer,
    pagesize=landscape(A4),
    rightMargin=20,
    leftMargin=20,
    topMargin=20,
    bottomMargin=20,
)

elements = []
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleStyle", parent=styles["Heading1"], fontSize=14, leading=16, alignment=1
)
cell_style = ParagraphStyle(
    "CellStyle", parent=styles["Normal"], fontSize=8, leading=10, alignment=1
)
cell_bold = ParagraphStyle(
    "CellBold", parent=styles["Normal"], fontSize=8, leading=10, alignment=1, fontName="Helvetica-Bold"
)

# Título do Relatório
elements.append(
    Paragraph(
        f"Conferência de Carga Horária - {st.session_state.turma_atual} ({st.session_state.ano_letivo})",
        title_style,
    )
)
elements.append(Spacer(1, 15))

# Cabeçalho da Tabela PDF
pdf_table_data = [
    [
        Paragraph("<b>Componente Curricular</b>", cell_bold),
        Paragraph("<b>Etapa</b>", cell_bold),
        Paragraph("<b>Seg</b>", cell_bold),
        Paragraph("<b>Ter</b>", cell_bold),
        Paragraph("<b>Qua</b>", cell_bold),
        Paragraph("<b>Qui</b>", cell_bold),
        Paragraph("<b>Sex</b>", cell_bold),
        Paragraph("<b>Tot. Etapa</b>", cell_bold),
        Paragraph("<b>Tot. Anual</b>", cell_bold),
        Paragraph("<b>Previsto</b>", cell_bold),
        Paragraph("<b>Situação</b>", cell_bold),
    ]
]

# Preenchimento dos dados da tabela no PDF
for orig_idx, item in lancamentos_turma:
    mat = item["materia"]
    prev = item["previsto"]
    s_a, t_a, q_a, qui_a, sex_a = (
        item["Seg"],
        item["Ter"],
        item["Qua"],
        item["Qui"],
        item["Sex"],
    )

    tot_anual = 0
    for e in [1, 2, 3]:
        s_d = dias_map.loc["Segunda", f"Etapa {e}"]
        t_d = dias_map.loc["Terça", f"Etapa {e}"]
        q_d = dias_map.loc["Quarta", f"Etapa {e}"]
        qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
        sex_d = dias_map.loc["Sexta", f"Etapa {e}"]
        tot_anual += (
            (s_a * s_d)
            + (t_a * t_d)
            + (q_a * q_d)
            + (qui_a * qui_d)
            + (sex_a * sex_d)
        )

    dif = tot_anual - prev
    sit_txt = (
        "OK"
        if dif == 0
        else (f"EXCESSO (+{dif})" if dif > 0 else f"FALTA ({dif})")
    )

    for e in [1, 2, 3]:
        s_d = dias_map.loc["Segunda", f"Etapa {e}"]
        t_d = dias_map.loc["Terça", f"Etapa {e}"]
        q_d = dias_map.loc["Quarta", f"Etapa {e}"]
        qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
        sex_d = dias_map.loc["Sexta", f"Etapa {e}"]
        tot_etapa = (
            (s_a * s_d)
            + (t_a * t_d)
            + (q_a * q_d)
            + (qui_a * qui_d)
            + (sex_a * sex_d)
        )

        pdf_table_data.append([
            Paragraph(mat if e == 1 else "", cell_bold),
            Paragraph(str(e), cell_style),
            Paragraph(str(s_a), cell_style),
            Paragraph(str(t_a), cell_style),
            Paragraph(str(q_a), cell_style),
            Paragraph(str(qui_a), cell_style),
            Paragraph(str(sex_a), cell_style),
            Paragraph(str(tot_etapa), cell_style),
            Paragraph(str(tot_anual) if e == 1 else "", cell_bold),
            Paragraph(str(prev) if e == 1 else "", cell_bold),
            Paragraph(sit_txt if e == 1 else "", cell_bold),
        ])

# Renderização e estilização da tabela no ReportLab
pdf_grid = Table(
    pdf_table_data,
    colWidths=[150, 40, 40, 40, 40, 40, 40, 80, 70, 70, 90],
)
pdf_grid.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b55a8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ])
)

elements.append(pdf_grid)
doc.build(elements)

# Botão de Download para o Streamlit
st.download_button(
    label="📄 Baixar Relatório PDF (.pdf)",
    data=pdf_buffer.getvalue(),
    file_name=f"Conferencia_{st.session_state.turma_atual}_{st.session_state.ano_letivo}.pdf",
    mime="application/pdf",
)
