import io
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Conferência dos Diários",
    page_icon="📊",
    layout="wide"
)

# --- INICIALIZAÇÃO DO SESSION STATE ---
if "ano_letivo" not in st.session_state:
    st.session_state.ano_letivo = 2026

if "turma_atual" not in st.session_state:
    st.session_state.turma_atual = "1º ANO A"

if "lancamentos" not in st.session_state:
    st.session_state.lancamentos = []

if "dias_map" not in st.session_state:
    st.session_state.dias_map = pd.DataFrame(
        {
            "Etapa 1": [40, 40, 40, 40, 40],
            "Etapa 2": [35, 35, 35, 35, 35],
            "Etapa 3": [45, 45, 45, 45, 45],
        },
        index=["Segunda", "Terça", "Quarta", "Quinta", "Sexta"],
    )

# --- LISTA DE MATÉRIAS PADRÃO ---
MATERIAS_PADRAO = [
    "MATEMATICA",
    "PORTUGUES",
    "HISTORIA",
    "GEOGRAFIA",
    "CIENCIAS",
    "BIOLOGIA",
    "FISICA",
    "QUIMICA",
    "EDUCACAO FISICA",
    "ARTE",
    "INGLES",
    "FILOSOFIA",
    "SOCIOLOGIA"
]

# --- TÍTULO PRINCIPAL ---
st.title(f"📊 Conferência dos Diários - {st.session_state.ano_letivo}")

# --- ABAS DA APLICAÇÃO ---
aba_grade, aba_config = st.tabs(["📝 Grade de Aulas (Visualização)", "⚙️ Configurações"])

# ==============================================================================
# ABA 2: CONFIGURAÇÕES
# ==============================================================================
with aba_config:
    st.subheader("⚙️ Configurações Gerais")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.session_state.ano_letivo = st.number_input(
            "Ano Letivo:", value=int(st.session_state.ano_letivo), step=1
        )
    with col_c2:
        st.session_state.turma_atual = st.text_input(
            "Turma Atual:", value=st.session_state.turma_atual
        )

    st.markdown("---")
    st.subheader("📅 Dias Letivos por Etapa")
    st.caption("Ajuste a quantidade de dias letivos por dia da semana em cada etapa:")
    
    edited_dias = st.data_editor(
        st.session_state.dias_map,
        use_container_width=True,
        key="editor_dias_letivos"
    )
    st.session_state.dias_map = edited_dias


# ==============================================================================
# ABA 1: GRADE DE AULAS (VISUALIZAÇÃO & LANÇAMENTO)
# ==============================================================================
with aba_grade:
    st.subheader("✏️ Lançar Matéria")

    # Form para entrada de lançamentos lado a lado
    with st.form(key="form_lancamento", clear_on_submit=False):
        c_mat, c_prev, c_seg, c_ter, c_qua, c_qui, c_sex = st.columns([2.5, 1.2, 1, 1, 1, 1, 1])

        with c_mat:
            materia_input = st.selectbox("Componente Curricular:", MATERIAS_PADRAO)
        with c_prev:
            previsto_input = st.number_input("Aulas Anual:", min_value=0, value=240, step=10)
        with c_seg:
            seg_input = st.number_input("Segunda", min_value=0, value=2, step=1)
        with c_ter:
            ter_input = st.number_input("Terça", min_value=0, value=1, step=1)
        with c_qua:
            qua_input = st.number_input("Quarta", min_value=0, value=1, step=1)
        with c_qui:
            qui_input = st.number_input("Quinta", min_value=0, value=2, step=1)
        with c_sex:
            sex_input = st.number_input("Sexta", min_value=0, value=0, step=1)

        b_col1, b_col2, _ = st.columns([1.5, 1.5, 7])
        with b_col1:
            btn_sub = st.form_submit_button("🕹️ Lançar na Grade", use_container_width=True)
        with b_col2:
            btn_limpar = st.form_submit_button("🗑️ Limpar Todos", use_container_width=True)

    if btn_sub:
        novo_item = {
            "turma": st.session_state.turma_atual,
            "materia": materia_input,
            "previsto": previsto_input,
            "Seg": seg_input,
            "Ter": ter_input,
            "Qua": qua_input,
            "Qui": qui_input,
            "Sex": sex_input
        }
        st.session_state.lancamentos.append(novo_item)
        st.success(f"Componente '{materia_input}' adicionado à turma {st.session_state.turma_atual}!")
        st.rerun()

    if btn_limpar:
        st.session_state.lancamentos = []
        st.warning("Todos os lançamentos foram limpos!")
        st.rerun()

    st.markdown("---")
    
    # --- EXIBIÇÃO DA TABELA DE CONFERÊNCIA ---
    turma_sel = st.session_state.turma_atual
    lancamentos_turma = [
        (idx, item) for idx, item in enumerate(st.session_state.lancamentos)
        if item.get("turma") == turma_sel
    ]

    st.subheader(f"📋 Tabela de Conferência - Turma: {turma_sel}")

    if not lancamentos_turma:
        st.info("Nenhuma matéria lançada para esta turma até o momento. Utilize o formulário acima para adicionar.")
    else:
        dias_map = st.session_state.dias_map

        # Construção da Tabela HTML
        html_code = """
        <style>
            .custom-table {
                width: 100%;
                border-collapse: collapse;
                font-family: Arial, sans-serif;
                font-size: 13px;
            }
            .custom-table th {
                background-color: #1b55a8;
                color: white;
                text-align: center;
                padding: 8px;
                border: 1px solid #ccc;
            }
            .custom-table td {
                text-align: center;
                padding: 6px;
                border: 1px solid #ddd;
            }
            .custom-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .sit-ok { color: green; font-weight: bold; }
            .sit-falta { color: red; font-weight: bold; }
            .sit-excesso { color: orange; font-weight: bold; }
        </style>
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Componente Curricular</th>
                    <th>Etapa</th>
                    <th>Seg</th>
                    <th>Ter</th>
                    <th>Qua</th>
                    <th>Qui</th>
                    <th>Sex</th>
                    <th>Tot. Etapa</th>
                    <th>Tot. Anual</th>
                    <th>Previsto</th>
                    <th>Situação</th>
                </tr>
            </thead>
            <tbody>
        """

        for orig_idx, item in lancamentos_turma:
            mat = item["materia"]
            prev = item["previsto"]
            s_a, t_a, q_a, qui_a, sex_a = item["Seg"], item["Ter"], item["Qua"], item["Qui"], item["Sex"]

            # Cálculo Anual
            tot_anual = 0
            for e in [1, 2, 3]:
                s_d = dias_map.loc["Segunda", f"Etapa {e}"]
                t_d = dias_map.loc["Terça", f"Etapa {e}"]
                q_d = dias_map.loc["Quarta", f"Etapa {e}"]
                qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
                sex_d = dias_map.loc["Sexta", f"Etapa {e}"]
                tot_anual += (s_a * s_d) + (t_a * t_d) + (q_a * q_d) + (qui_a * qui_d) + (sex_a * sex_d)

            dif = tot_anual - prev
            if dif == 0:
                sit_txt = '<span class="sit-ok">OK</span>'
            elif dif > 0:
                sit_txt = f'<span class="sit-excesso">EXCESSO (+{dif})</span>'
            else:
                sit_txt = f'<span class="sit-falta">FALTA ({dif})</span>'

            # Linhas de cada Etapa
            for e in [1, 2, 3]:
                s_d = dias_map.loc["Segunda", f"Etapa {e}"]
                t_d = dias_map.loc["Terça", f"Etapa {e}"]
                q_d = dias_map.loc["Quarta", f"Etapa {e}"]
                qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
                sex_d = dias_map.loc["Sexta", f"Etapa {e}"]
                tot_etapa = (s_a * s_d) + (t_a * t_d) + (q_a * q_d) + (qui_a * qui_d) + (sex_a * sex_d)

                html_code += "<tr>"
                if e == 1:
                    html_code += f'<td rowspan="3" style="vertical-align: middle; font-weight: bold;">{mat}</td>'
                
                html_code += f"<td>{e}</td>"
                html_code += f"<td>{s_a}</td>"
                html_code += f"<td>{t_a}</td>"
                html_code += f"<td>{q_a}</td>"
                html_code += f"<td>{qui_a}</td>"
                html_code += f"<td>{sex_a}</td>"
                html_code += f"<td>{tot_etapa}</td>"

                if e == 1:
                    html_code += f'<td rowspan="3" style="vertical-align: middle; font-weight: bold;">{tot_anual}</td>'
                    html_code += f'<td rowspan="3" style="vertical-align: middle; font-weight: bold;">{prev}</td>'
                    html_code += f'<td rowspan="3" style="vertical-align: middle;">{sit_txt}</td>'
                
                html_code += "</tr>"

        html_code += "</tbody></table>"
        st.markdown(html_code, unsafe_allow_html=True)

        st.markdown("---")

        # --- EXPORTAÇÃO (EXCEL & PDF) ---
        st.subheader("📥 Exportar Relatórios")
        c_exp1, c_exp2 = st.columns(2)

        # Exportar Excel
        with c_exp1:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Conferência"

            ws.append(["Componente Curricular", "Etapa", "Seg", "Ter", "Qua", "Qui", "Sex", "Tot. Etapa", "Tot. Anual", "Previsto", "Situação"])
            
            for orig_idx, item in lancamentos_turma:
                mat = item["materia"]
                prev = item["previsto"]
                s_a, t_a, q_a, qui_a, sex_a = item["Seg"], item["Ter"], item["Qua"], item["Qui"], item["Sex"]

                tot_anual = 0
                for e in [1, 2, 3]:
                    s_d = dias_map.loc["Segunda", f"Etapa {e}"]
                    t_d = dias_map.loc["Terça", f"Etapa {e}"]
                    q_d = dias_map.loc["Quarta", f"Etapa {e}"]
                    qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
                    sex_d = dias_map.loc["Sexta", f"Etapa {e}"]
                    tot_anual += (s_a * s_d) + (t_a * t_d) + (q_a * q_d) + (qui_a * qui_d) + (sex_a * sex_d)

                dif = tot_anual - prev
                sit = "OK" if dif == 0 else (f"EXCESSO (+{dif})" if dif > 0 else f"FALTA ({dif})")

                for e in [1, 2, 3]:
                    s_d = dias_map.loc["Segunda", f"Etapa {e}"]
                    t_d = dias_map.loc["Terça", f"Etapa {e}"]
                    q_d = dias_map.loc["Quarta", f"Etapa {e}"]
                    qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
                    sex_d = dias_map.loc["Sexta", f"Etapa {e}"]
                    tot_etapa = (s_a * s_d) + (t_a * t_d) + (q_a * q_d) + (qui_a * qui_d) + (sex_a * sex_d)

                    ws.append([
                        mat if e == 1 else "",
                        e, s_a, t_a, q_a, qui_a, sex_a,
                        tot_etapa,
                        tot_anual if e == 1 else "",
                        prev if e == 1 else "",
                        sit if e == 1 else ""
                    ])

            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            st.download_button(
                label="📊 Baixar Excel (.xlsx)",
                data=excel_buffer.getvalue(),
                file_name=f"Conferencia_{turma_sel}_{st.session_state.ano_letivo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # Exportar PDF
        with c_exp2:
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
            elements = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=14, leading=16, alignment=1)
            cell_style = ParagraphStyle("CellStyle", parent=styles["Normal"], fontSize=8, leading=10, alignment=1)
            cell_bold = ParagraphStyle("CellBold", parent=styles["Normal"], fontSize=8, leading=10, alignment=1, fontName="Helvetica-Bold")

            elements.append(Paragraph(f"Conferência de Carga Horária - {turma_sel} ({st.session_state.ano_letivo})", title_style))
            elements.append(Spacer(1, 15))

            pdf_table_data = [[
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
                Paragraph("<b>Situação</b>", cell_bold)
            ]]

            for orig_idx, item in lancamentos_turma:
                mat = item["materia"]
                prev = item["previsto"]
                s_a, t_a, q_a, qui_a, sex_a = item["Seg"], item["Ter"], item["Qua"], item["Qui"], item["Sex"]

                tot_anual = 0
                for e in [1, 2, 3]:
                    s_d = dias_map.loc["Segunda", f"Etapa {e}"]
                    t_d = dias_map.loc["Terça", f"Etapa {e}"]
                    q_d = dias_map.loc["Quarta", f"Etapa {e}"]
                    qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
                    sex_d = dias_map.loc["Sexta", f"Etapa {e}"]
                    tot_anual += (s_a * s_d) + (t_a * t_d) + (q_a * q_d) + (qui_a * qui_d) + (sex_a * sex_d)

                dif = tot_anual - prev
                sit_txt = "OK" if dif == 0 else (f"EXCESSO (+{dif})" if dif > 0 else f"FALTA ({dif})")

                for e in [1, 2, 3]:
                    s_d = dias_map.loc["Segunda", f"Etapa {e}"]
                    t_d = dias_map.loc["Terça", f"Etapa {e}"]
                    q_d = dias_map.loc["Quarta", f"Etapa {e}"]
                    qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
                    sex_d = dias_map.loc["Sexta", f"Etapa {e}"]
                    tot_etapa = (s_a * s_d) + (t_a * t_d) + (q_a * q_d) + (qui_a * qui_d) + (sex_a * sex_d)

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
                        Paragraph(sit_txt if e == 1 else "", cell_bold)
                    ])

            pdf_grid = Table(pdf_table_data, colWidths=[140, 40, 40, 40, 40, 40, 40, 80, 70, 70, 90])
            pdf_grid.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b55a8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            elements.append(pdf_grid)
            doc.build(elements)

            st.download_button(
                label="📄 Baixar Relatório PDF (.pdf)",
                data=pdf_buffer.getvalue(),
                file_name=f"Conferencia_{turma_sel}_{st.session_state.ano_letivo}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
