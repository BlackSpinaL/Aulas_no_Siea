import io
import pandas as pd
import streamlit as st
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistema de Conferência de Carga Horária",
    page_icon="📚",
    layout="wide",
)

# Safe Session State initialization to avoid AttributeError
if "turma_atual" not in st.session_state:
    st.session_state.turma_atual = "1º Ano A"

if "ano_letivo" not in st.session_state:
    st.session_state.ano_letivo = 2026

if "lancamentos" not in st.session_state:
    # Default initial data structure
    st.session_state.lancamentos = [
        {
            "turma": "1º Ano A",
            "materia": "Língua Portuguesa",
            "previsto": 160,
            "Seg": 2,
            "Ter": 1,
            "Qua": 1,
            "Qui": 0,
            "Sex": 0,
        },
        {
            "turma": "1º Ano A",
            "materia": "Matemática",
            "previsto": 160,
            "Seg": 1,
            "Ter": 2,
            "Qua": 1,
            "Qui": 0,
            "Sex": 0,
        },
        {
            "turma": "1º Ano A",
            "materia": "História",
            "previsto": 80,
            "Seg": 0,
            "Ter": 0,
            "Qua": 1,
            "Qui": 1,
            "Sex": 0,
        },
    ]

# Default days map DataFrame per stage (Etapa 1, 2, 3)
if "dias_map" not in st.session_state:
    st.session_state.dias_map = pd.DataFrame(
        {
            "Etapa 1": [12, 12, 12, 12, 12],
            "Etapa 2": [14, 14, 14, 14, 14],
            "Etapa 3": [14, 14, 14, 14, 14],
        },
        index=["Segunda", "Terça", "Quarta", "Quinta", "Sexta"],
    )

# -----------------------------------------------------------------------------
# 2. SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações Gerais")

st.session_state.ano_letivo = st.sidebar.number_input(
    "Ano Letivo", min_value=2020, max_value=2035, value=st.session_state.ano_letivo
)

st.session_state.turma_atual = st.sidebar.text_input(
    "Turma Selecionada", value=st.session_state.turma_atual
)

st.sidebar.subheader("🗓️ Dias Letivos por Etapa")
dias_map = st.sidebar.data_editor(st.session_state.dias_map)
st.session_state.dias_map = dias_map

# -----------------------------------------------------------------------------
# 3. MAIN INTERFACE & DATA MANAGEMENT
# -----------------------------------------------------------------------------
st.title("📚 Conferência de Carga Horária Curricular")
st.caption(
    f"Visualizando dados para a turma **{st.session_state.turma_atual}** - Ano **{st.session_state.ano_letivo}**"
)

st.subheader("📝 Lançamento de Componentes Curriculares")

# Data editor for active schedule entries
df_lancamentos = pd.DataFrame(st.session_state.lancamentos)
df_filtrado = df_lancamentos[df_lancamentos["turma"] == st.session_state.turma_atual]

edited_df = st.data_editor(
    df_filtrado,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_turma",
)

# Update state back with edited values
if not edited_df.equals(df_filtrado):
    # Retain entries from other classes and append current updated class data
    outras_turmas = [
        item for item in st.session_state.lancamentos if item["turma"] != st.session_state.turma_atual
    ]
    novos_dados = edited_df.to_dict(orient="records")
    for item in novos_dados:
        item["turma"] = st.session_state.turma_atual
    st.session_state.lancamentos = outras_turmas + novos_dados
    st.rerun()

# -----------------------------------------------------------------------------
# 4. CALCULATION & PREVIEW TABLE
# -----------------------------------------------------------------------------
st.subheader("📊 Resumo de Horas Calculadas")

lancamentos_turma = [
    (idx, item)
    for idx, item in enumerate(st.session_state.lancamentos)
    if item.get("turma") == st.session_state.turma_atual
]

resumo_rows = []
for orig_idx, item in lancamentos_turma:
    mat = item.get("materia", "")
    prev = item.get("previsto", 0)
    s_a = item.get("Seg", 0)
    t_a = item.get("Ter", 0)
    q_a = item.get("Qua", 0)
    qui_a = item.get("Qui", 0)
    sex_a = item.get("Sex", 0)

    tot_anual = 0
    for e in [1, 2, 3]:
        s_d = dias_map.loc["Segunda", f"Etapa {e}"]
        t_d = dias_map.loc["Terça", f"Etapa {e}"]
        q_d = dias_map.loc["Quarta", f"Etapa {e}"]
        qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
        sex_d = dias_map.loc["Sexta", f"Etapa {e}"]
        tot_anual += (
            (s_a * s_d) + (t_a * t_d) + (q_a * q_d) + (qui_a * qui_d) + (sex_a * sex_d)
        )

    dif = tot_anual - prev
    sit_txt = (
        "OK"
        if dif == 0
        else (f"EXCESSO (+{dif})" if dif > 0 else f"FALTA ({dif})")
    )

    resumo_rows.append(
        {
            "Componente": mat,
            "Aulas/Semana": s_a + t_a + q_a + qui_a + sex_a,
            "Carga Prevista (h)": prev,
            "Carga Calculada (h)": tot_anual,
            "Diferença": dif,
            "Situação": sit_txt,
        }
    )

df_resumo = pd.DataFrame(resumo_rows)
st.dataframe(df_resumo, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. EXPORT OPTIONS (EXCEL & REPORTLAB PDF)
# -----------------------------------------------------------------------------
st.divider()
st.subheader("📥 Exportação de Relatórios")

col_excel, col_pdf = st.columns(2)

# --- EXCEL EXPORT (OpenPyXL) ---
with col_excel:
    excel_buffer = io.BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Carga Horaria"

    # Styles
    font_header = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="1B55A8", end_color="1B55A8", fill_type="solid")
    align_center = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style="thin", color="CCCCCC"),
        right=Side(style="thin", color="CCCCCC"),
        top=Side(style="thin", color="CCCCCC"),
        bottom=Side(style="thin", color="CCCCCC"),
    )

    # Headers
    headers = ["Componente", "Aulas/Semana", "Carga Prevista (h)", "Carga Calculada (h)", "Diferença", "Situação"]
    ws.append(headers)

    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_center

    # Rows
    for r in resumo_rows:
        ws.append([r["Componente"], r["Aulas/Semana"], r["Carga Prevista (h)"], r["Carga Calculada (h)"], r["Diferença"], r["Situação"]])

    for row in ws.iter_rows(min_row=2, max_row=len(resumo_rows) + 1, min_col=1, max_col=6):
        for cell in row:
            cell.alignment = align_center
            cell.border = thin_border

    wb.save(excel_buffer)

    st.download_button(
        label="📊 Baixar Relatório Excel (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"Conferencia_{st.session_state.turma_atual}_{st.session_state.ano_letivo}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# --- PDF EXPORT (ReportLab) ---
with col_pdf:
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(letter),
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

    # Document Header
    turma_str = st.session_state.get("turma_atual", "N/A")
    ano_str = st.session_state.get("ano_letivo", "N/A")

    elements.append(
        Paragraph(
            f"Conferência de Carga Horária - {turma_str} ({ano_str})",
            title_style,
        )
    )
    elements.append(Spacer(1, 15))

    # Table Structure for PDF
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

    for orig_idx, item in lancamentos_turma:
        mat = item.get("materia", "")
        prev = item.get("previsto", 0)
        s_a = item.get("Seg", 0)
        t_a = item.get("Ter", 0)
        q_a = item.get("Qua", 0)
        qui_a = item.get("Qui", 0)
        sex_a = item.get("Sex", 0)

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

    st.download_button(
        label="📄 Baixar Relatório PDF (.pdf)",
        data=pdf_buffer.getvalue(),
        file_name=f"Conferencia_{turma_str}_{ano_str}.pdf",
        mime="application/pdf",
    )