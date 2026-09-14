import io
import pandas as pd
import streamlit as st

# Tentar importar ReportLab para geração de PDF
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

st.set_page_config(
    page_title="Conferência dos Diários",
    layout="wide",
)

# Estilização CSS personalizada para a Tabela estilo Excel
st.markdown(
    """
<style>
.excel-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 13px;
}
.excel-table th {
    background-color: #1b55a8;
    color: white;
    font-weight: bold;
    text-align: center;
    border: 1px solid #103871;
    padding: 5px;
}
.excel-table .header-main {
    background-color: #0d2b59;
    color: white;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
    padding: 8px;
}
.excel-table td {
    border: 1px solid #cccccc;
    padding: 6px;
    text-align: center;
    color: #333333;
}
.row-materia-1 {
    background-color: #e8f5e9 !important; /* Verde bem claro */
}
.row-materia-0 {
    background-color: #ffffff !important; /* Branco */
}
.aula-destaque {
    font-weight: 900 !important;
    font-size: 14px !important;
    color: #000000 !important;
    background-color: #fff59d !important; /* Amarelo destaque */
}
.status-ok {
    background-color: #c8e6c9 !important;
    color: #2e7d32 !important;
    font-weight: bold;
}
.status-err {
    background-color: #ffcdd2 !important;
    color: #c62828 !important;
    font-weight: bold;
}
</style>
""",
    unsafe_allow_html=True,
)

# Inicialização do Session State
if "ano_letivo" not in st.session_state:
    st.session_state.ano_letivo = 2026

if "turmas" not in st.session_state:
    st.session_state.turmas = ["12101", "12102", "12103", "12104"]

if "turma_atual" not in st.session_state:
    st.session_state.turma_atual = "12101"

if "editing_idx" not in st.session_state:
    st.session_state.editing_idx = None

DISCIPLINAS_PADRAO = [
    "ARTE",
    "BIOLOGIA",
    "BIOLOGIA NA PRATICA",
    "C. DA NATUREZA P/ ENEM",
    "CIENCIAS",
    "DESENV. SUSTENTAVEL",
    "ED. FISICA NA PRATICA",
    "ED. PARA PROFISSOES",
    "ED. SOCIO. ENS. RELIG.",
    "EDUCACAO FINANCEIRA",
    "EDUCACAO FISICA",
    "FILOSOFIA",
    "FISICA",
    "GEOGRAFIA",
    "HISTORIA",
    "LABORATORIO / BIOLOGIA",
    "LABORATORIO / CIENCIAS",
    "LABORATORIO / FISICA",
    "LABORATORIO / QUIMICA",
    "LINGUA INGLESA",
    "LÍNGUA INGLESA NA PRATICA",
    "LINGUA PORTUGUESA",
    "LINGUA PORTUGUESA 2",
    "MAT. E ESTATISTICA",
    "MATEMATICA",
    "OFICINA DE TEXTO",
    "PROJETO DE VIDA",
    "QUIMICA",
    "QUIMICA NA PRATICA",
    "SOCIOLOGIA",
]

if "disciplinas" not in st.session_state:
    st.session_state.disciplinas = DISCIPLINAS_PADRAO.copy()

if "dias_etapas" not in st.session_state:
    st.session_state.dias_etapas = pd.DataFrame({
        "Dia da Semana": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"],
        "Etapa 1": [13, 12, 14, 14, 13],
        "Etapa 2": [15, 16, 13, 13, 14],
        "Etapa 3": [12, 12, 13, 13, 13],
    })

if "lancamentos" not in st.session_state:
    st.session_state.lancamentos = []

st.title(f"📊 Conferência dos Diários - {st.session_state.ano_letivo}")

aba1, aba2 = st.tabs(["📋 Grade de Aulas (Visualização)", "⚙️ Configurações"])

# -------------------------------------------------------------
# ABA 2: CONFIGURAÇÕES (ANO, TURMAS, MATÉRIAS E CALENDÁRIO)
# -------------------------------------------------------------
with aba2:
    st.subheader("⚙️ Configurações Gerais")
    col_cfg1, col_cfg2, col_cfg3 = st.columns([1, 1, 1])

    with col_cfg1:
        st.markdown("### 1. Ano Letivo")
        novo_ano = st.number_input(
            "Ano Letivo:",
            min_value=2020,
            max_value=2035,
            value=st.session_state.ano_letivo,
        )
        if novo_ano != st.session_state.ano_letivo:
            st.session_state.ano_letivo = novo_ano
            st.rerun()

    with col_cfg2:
        st.markdown("### 2. Gerenciar Turmas")
        nova_turma = st.text_input("Nova Turma (ex: 12105):")
        if st.button("➕ Adicionar Turma"):
            if (
                nova_turma.strip()
                and nova_turma.upper() not in st.session_state.turmas
            ):
                st.session_state.turmas.append(nova_turma.upper())
                st.session_state.turmas.sort()
                st.rerun()

        turma_rem = st.selectbox(
            "Excluir Turma Definitivamente:",
            ["-- Selecione --"] + st.session_state.turmas,
        )
        if st.button("🗑️ Deletar Turma") and turma_rem != "-- Selecione --":
            st.session_state.turmas.remove(turma_rem)
            st.session_state.lancamentos = [
                l
                for l in st.session_state.lancamentos
                if l.get("turma") != turma_rem
            ]
            if st.session_state.turmas:
                st.session_state.turma_atual = st.session_state.turmas[0]
            st.rerun()

    with col_cfg3:
        st.markdown("### 3. Gerenciar Disciplinas")
        nova_mat = st.text_input("Nova Disciplina:")
        if st.button("➕ Adicionar Disciplina"):
            if (
                nova_mat.strip()
                and nova_mat.upper() not in st.session_state.disciplinas
            ):
                st.session_state.disciplinas.append(nova_mat.upper())
                st.session_state.disciplinas.sort()
                st.rerun()

    st.markdown("---")
    st.markdown("### 4. Dias de cada Etapa (Calendário Escolar)")

    # Edição do calendário escolar
    df_editvel = st.data_editor(
        st.session_state.dias_etapas,
        num_rows="fixed",
        use_container_width=True,
        key="editor_etapas",
    )
    st.session_state.dias_etapas = df_editvel

    # Cálculo dinâmico das somas de linhas (TOTAL DIAS) e colunas (TOTAL ETAPAS)
    df_calc = df_editvel.copy()
    df_calc["TOTAL DIAS"] = df_calc[["Etapa 1", "Etapa 2", "Etapa 3"]].sum(
        axis=1
    )

    linha_total = pd.DataFrame({
        "Dia da Semana": ["TOTAL ETAPAS"],
        "Etapa 1": [df_calc["Etapa 1"].sum()],
        "Etapa 2": [df_calc["Etapa 2"].sum()],
        "Etapa 3": [df_calc["Etapa 3"].sum()],
        "TOTAL DIAS": [df_calc["TOTAL DIAS"].sum()],
    })

    df_conferencia = pd.concat([df_calc, linha_total], ignore_index=True)

    st.markdown("**📋 Tabela de Conferência (Totais Automáticos):**")
    st.dataframe(
        df_conferencia,
        use_container_width=True,
        hide_index=True,
    )

# -------------------------------------------------------------
# ABA 1: VISUALIZAÇÃO PRINCIPAL
# -------------------------------------------------------------
with aba1:
    c_t, c_dummy = st.columns([2, 4])
    with c_t:
        st.session_state.turma_atual = st.selectbox(
            "📍 Selecione a Turma para Conferência:", st.session_state.turmas
        )

    # SEÇÃO DE EDIÇÃO OU NOVO LANÇAMENTO
    if st.session_state.editing_idx is not None:
        st.markdown("### ✏️ Editando Disciplina Lançada")
        item_edit = st.session_state.lancamentos[st.session_state.editing_idx]

        c_m, c_prev, c_seg, c_ter, c_qua, c_qui, c_sex = st.columns(
            [2.5, 1.2, 1, 1, 1, 1, 1]
        )
        with c_m:
            mat_e = st.text_input(
                "Componente Curricular:",
                value=item_edit["materia"],
                disabled=True,
            )
        with c_prev:
            prev_e = st.number_input(
                "Aulas Anual:",
                min_value=0,
                value=item_edit["previsto"],
                step=10,
            )
        with c_seg:
            seg_e = st.number_input(
                "Segunda", min_value=0, max_value=10, value=item_edit["Seg"]
            )
        with c_ter:
            ter_e = st.number_input(
                "Terça", min_value=0, max_value=10, value=item_edit["Ter"]
            )
        with c_qua:
            qua_e = st.number_input(
                "Quarta", min_value=0, max_value=10, value=item_edit["Qua"]
            )
        with c_qui:
            qui_e = st.number_input(
                "Quinta", min_value=0, max_value=10, value=item_edit["Qui"]
            )
        with c_sex:
            sex_e = st.number_input(
                "Sexta", min_value=0, max_value=10, value=item_edit["Sex"]
            )

        col_sav1, col_sav2 = st.columns([1, 4])
        with col_sav1:
            if st.button("💾 Salvar Alterações"):
                st.session_state.lancamentos[st.session_state.editing_idx] = {
                    "turma": st.session_state.turma_atual,
                    "materia": item_edit["materia"],
                    "previsto": prev_e,
                    "Seg": seg_e,
                    "Ter": ter_e,
                    "Qua": qua_e,
                    "Qui": qui_e,
                    "Sex": sex_e,
                }
                st.session_state.editing_idx = None
                st.success("Alterações salvas com sucesso!")
                st.rerun()
        with col_sav2:
            if st.button("❌ Cancelar Edição"):
                st.session_state.editing_idx = None
                st.rerun()

    else:
        st.markdown("### ✏️ Lançar Matéria na Grade")
        c_m, c_prev, c_seg, c_ter, c_qua, c_qui, c_sex = st.columns(
            [2.5, 1.2, 1, 1, 1, 1, 1]
        )
        with c_m:
            mat_escolhida = st.selectbox(
                "Componente Curricular:",
                ["-- Selecione --"] + st.session_state.disciplinas,
            )
        with c_prev:
            aulas_anual_prevista = st.number_input(
                "Aulas Anual:", min_value=0, value=80, step=10
            )
        with c_seg:
            seg = st.number_input("Segunda", min_value=0, max_value=10, value=0)
        with c_ter:
            ter = st.number_input("Terça", min_value=0, max_value=10, value=0)
        with c_qua:
            qua = st.number_input("Quarta", min_value=0, max_value=10, value=0)
        with c_qui:
            qui = st.number_input("Quinta", min_value=0, max_value=10, value=0)
        with c_sex:
            sex = st.number_input("Sexta", min_value=0, max_value=10, value=0)

        if st.button("📥 Lançar na Grade"):
            if mat_escolhida != "-- Selecione --":
                st.session_state.lancamentos.append({
                    "turma": st.session_state.turma_atual,
                    "materia": mat_escolhida,
                    "previsto": aulas_anual_prevista,
                    "Seg": seg,
                    "Ter": ter,
                    "Qua": qua,
                    "Qui": qui,
                    "Sex": sex,
                })
                st.success(f"'{mat_escolhida}' lançada com sucesso!")
                st.rerun()

    st.markdown("---")

    # Filtrar lançamentos da turma selecionada
    lancamentos_turma = [
        (orig_idx, item)
        for orig_idx, item in enumerate(st.session_state.lancamentos)
        if item.get("turma", st.session_state.turma_atual)
        == st.session_state.turma_atual
    ]

    dias_map = st.session_state.dias_etapas.set_index("Dia da Semana")

    if lancamentos_turma:
        # Cabeçalho da Tabela Principal
        titulo_grade = f"TURMA: {st.session_state.turma_atual} - PREVISÃO DE AULAS - {st.session_state.ano_letivo}"

        html_code = f"""
        <table class="excel-table">
            <thead>
                <tr>
                    <th colspan="20" class="header-main">{titulo_grade}</th>
                </tr>
                <tr>
                    <th rowspan="2" style="width: 15%;">Componente Curricular</th>
                    <th rowspan="2" style="width: 4%;">Etapa</th>
                    <th colspan="3">Segunda</th>
                    <th colspan="3">Terça</th>
                    <th colspan="3">Quarta</th>
                    <th colspan="3">Quinta</th>
                    <th colspan="3">Sexta</th>
                    <th rowspan="2">Nº aulas<br>por etapa</th>
                    <th rowspan="2">TOTAL<br>AULAS</th>
                    <th rowspan="2">AULAS<br>ANUAL</th>
                    <th rowspan="2">SITUAÇÃO</th>
                </tr>
                <tr>
                    <th>Nº aulas</th><th>Nº/etapa</th><th>Total</th>
                    <th>Nº aulas</th><th>Nº/etapa</th><th>Total</th>
                    <th>Nº aulas</th><th>Nº/etapa</th><th>Total</th>
                    <th>Nº aulas</th><th>Nº/etapa</th><th>Total</th>
                    <th>Nº aulas</th><th>Nº/etapa</th><th>Total</th>
                </tr>
            </thead>
            <tbody>
        """

        for pos, (orig_idx, item) in enumerate(lancamentos_turma):
            mat = item["materia"]
            prev = item["previsto"]
            s_a, t_a, q_a, qui_a, sex_a = (
                item["Seg"],
                item["Ter"],
                item["Qua"],
                item["Qui"],
                item["Sex"],
            )

            bg_class = "row-materia-1" if pos % 2 == 0 else "row-materia-0"

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
            if dif == 0:
                sit_txt, sit_class = "✅ OK", "status-ok"
            elif dif > 0:
                sit_txt, sit_class = f"⚠️ EXCESSO (+{dif})", "status-err"
            else:
                sit_txt, sit_class = f"❌ FALTA ({dif})", "status-err"

            for e in [1, 2, 3]:
                s_d = dias_map.loc["Segunda", f"Etapa {e}"]
                t_d = dias_map.loc["Terça", f"Etapa {e}"]
                q_d = dias_map.loc["Quarta", f"Etapa {e}"]
                qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
                sex_d = dias_map.loc["Sexta", f"Etapa {e}"]

                s_t, t_t, q_t, qui_t, sex_t = (
                    s_a * s_d,
                    t_a * t_d,
                    q_a * q_d,
                    qui_a * qui_d,
                    sex_a * sex_d,
                )
                tot_etapa = s_t + t_t + q_t + qui_t + sex_t

                s_a_h = (
                    f'<td class="{bg_class} aula-destaque">{s_a}</td>'
                    if s_a > 0
                    else f'<td class="{bg_class}">{s_a}</td>'
                )
                t_a_h = (
                    f'<td class="{bg_class} aula-destaque">{t_a}</td>'
                    if t_a > 0
                    else f'<td class="{bg_class}">{t_a}</td>'
                )
                q_a_h = (
                    f'<td class="{bg_class} aula-destaque">{q_a}</td>'
                    if q_a > 0
                    else f'<td class="{bg_class}">{q_a}</td>'
                )
                qui_a_h = (
                    f'<td class="{bg_class} aula-destaque">{qui_a}</td>'
                    if qui_a > 0
                    else f'<td class="{bg_class}">{qui_a}</td>'
                )
                sex_a_h = (
                    f'<td class="{bg_class} aula-destaque">{sex_a}</td>'
                    if sex_a > 0
                    else f'<td class="{bg_class}">{sex_a}</td>'
                )

                html_code += f'<tr class="{bg_class}">'

                if e == 1:
                    html_code += (
                        f'<td rowspan="3" style="font-weight:bold;">{mat}</td>'
                    )

                html_code += f"<td>{e}</td>"
                html_code += (
                    f"{s_a_h}<td>{s_d}</td><td>{s_t}</td>"
                    f"{t_a_h}<td>{t_d}</td><td>{t_t}</td>"
                    f"{q_a_h}<td>{q_d}</td><td>{q_t}</td>"
                    f"{qui_a_h}<td>{qui_d}</td><td>{qui_t}</td>"
                    f"{sex_a_h}<td>{sex_d}</td><td>{sex_t}</td>"
                    f'<td style="font-weight:bold;">{tot_etapa}</td>'
                )

                if e == 1:
                    html_code += (
                        f'<td rowspan="3" style="font-weight:bold; font-size:14px;">{tot_anual}</td>'
                        f'<td rowspan="3" style="font-weight:bold; font-size:14px;">{prev}</td>'
                        f'<td rowspan="3" class="{sit_class}">{sit_txt}</td>'
                    )

                html_code += "</tr>"

        html_code += "</tbody></table>"
        st.markdown(html_code, unsafe_allow_html=True)

        st.markdown("### ⚙️ Ações para cada Disciplina")
        cols_btn = st.columns(len(lancamentos_turma))
        for pos, (orig_idx, item) in enumerate(lancamentos_turma):
            with cols_btn[pos if pos < len(cols_btn) else 0]:
                st.markdown(f"**{item['materia']}**")
                col_e, col_d = st.columns([1, 1])
                with col_e:
                    if st.button("✏️ Editar", key=f"btn_edit_{orig_idx}"):
                        st.session_state.editing_idx = orig_idx
                        st.rerun()
                with col_d:
                    if st.button("🗑️ Deletar", key=f"btn_del_{orig_idx}"):
                        st.session_state.lancamentos.pop(orig_idx)
                        st.rerun()

        # Botões para Download (Excel e PDF)
        st.markdown("---")
        c_exp1, c_exp2 = st.columns([1, 1])

        with c_exp1:
            rows_excel = [item for _, item in lancamentos_turma]
            df_exp = pd.DataFrame(rows_excel)
            buffer_excel = io.BytesIO()
            with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
                df_exp.to_excel(writer, index=False, sheet_name="Lançamentos")

            st.download_button(
                label="📥 Baixar Planilha em Excel (.xlsx)",
                data=buffer_excel.getvalue(),
                file_name=f"Conferencia_{st.session_state.turma_atual}_{st.session_state.ano_letivo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with c_exp2:
            if HAS_REPORTLAB:
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
                    "PdfTitle",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=14,
                    leading=16,
                    textColor=colors.whitesmoke,
                    alignment=1,
                )

                table_data = [[
                    Paragraph(
                        f"TURMA: {st.session_state.turma_atual} - PREVISÃO DE AULAS - {st.session_state.ano_letivo}",
                        title_style,
                    )
                ]]
                pdf_table = Table(table_data, colWidths=[780])
                pdf_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0d2b59")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                ]))

                elements.append(pdf_table)

                pdf_table_data = [[
                    "Componente Curricular",
                    "Etapa",
                    "Seg",
                    "Ter",
                    "Qua",
                    "Qui",
                    "Sex",
                    "Nº Aulas/Etapa",
                    "Total Aulas",
                    "Aulas Anual",
                    "Situação",
                ]]

                cell_style = ParagraphStyle(
                    "PdfCell",
                    parent=styles["Normal"],
                    fontName="Helvetica",
                    fontSize=8,
                    leading=10,
                    alignment=1,
                )
                cell_bold = ParagraphStyle(
                    "PdfCellBold",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=8,
                    leading=10,
                    alignment=1,
                )

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
                            Paragraph(str(tot_etapa), cell_bold),
                            Paragraph(str(tot_anual) if e == 1 else "", cell_bold),
                            Paragraph(str(prev) if e == 1 else "", cell_bold),
                            Paragraph(sit_txt if e == 1 else "", cell_style),
                        ])

                data_table = Table(
                    pdf_table_data,
                    colWidths=[150, 40, 40, 40, 40, 40, 40, 80, 70, 70, 90],
                )
                data_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b55a8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ]))

                elements.append(Spacer(1, 10))
                elements.append(data_table)

                doc.build(elements)

                st.download_button(
                    label="📄 Baixar Relatório em PDF (.pdf)",
                    data=pdf_buffer.getvalue(),
                    file_name=f"Conferencia_{st.session_state.turma_atual}_{st.session_state.ano_letivo}.pdf",
                    mime="application/pdf",
                )

    else:
        st.info(
            f"Nenhuma disciplina lançada para a Turma {st.session_state.turma_atual}."
        )
