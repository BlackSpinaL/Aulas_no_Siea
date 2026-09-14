import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Conferência dos Diários - 2026",
    layout="wide",
)

# Estilização CSS personalizada para replicar a planilha
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
    background-color: #e8f5e9 !important; /* Verde claro */
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

st.title("📊 Conferência dos Diários - 2026")

aba1, aba2 = st.tabs(["📋 Grade de Aulas (Visualização)", "⚙️ Configurações"])

with aba2:
    st.subheader("⚙️ Configurar Calendário e Disciplinas")
    col_c1, col_c2 = st.columns([1, 1])

    with col_c1:
        st.markdown("### Dias de cada Etapa")
        df_editado = st.data_editor(
            st.session_state.dias_etapas,
            num_rows="fixed",
            use_container_width=True,
            key="editor_etapas",
        )
        st.session_state.dias_etapas = df_editado

    with col_c2:
        st.markdown("### Gerenciar Disciplinas")
        nova_mat = st.text_input("Nova disciplina:")
        if st.button("➕ Adicionar Disciplina"):
            if (
                nova_mat.strip()
                and nova_mat.upper() not in st.session_state.disciplinas
            ):
                st.session_state.disciplinas.append(nova_mat.upper())
                st.session_state.disciplinas.sort()
                st.rerun()

        mat_rem = st.selectbox(
            "Remover disciplina:",
            ["-- Selecione --"] + st.session_state.disciplinas,
        )
        if st.button("🗑️ Remover Disciplina") and mat_rem != "-- Selecione --":
            st.session_state.disciplinas.remove(mat_rem)
            st.rerun()

with aba1:
    st.markdown("### ✏️ Lançar Matéria")
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

    col_b1, col_b2 = st.columns([1, 4])
    with col_b1:
        if st.button("📥 Lançar na Grade"):
            if mat_escolhida != "-- Selecione --":
                st.session_state.lancamentos.append({
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

    with col_b2:
        if st.session_state.lancamentos and st.button("🗑️ Limpar Todos"):
            st.session_state.lancamentos = []
            st.rerun()

    st.markdown("---")

    dias_map = st.session_state.dias_etapas.set_index("Dia da Semana")

    if st.session_state.lancamentos:
        # Montagem do HTML no padrão idêntico à imagem
        html_code = """
        <table class="excel-table">
            <thead>
                <tr>
                    <th colspan="21" class="header-main">PREVISÃO DE AULAS - 2026</th>
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

        for idx, item in enumerate(st.session_state.lancamentos):
            mat = item["materia"]
            prev = item["previsto"]
            s_a, t_a, q_a, qui_a, sex_a = (
                item["Seg"],
                item["Ter"],
                item["Qua"],
                item["Qui"],
                item["Sex"],
            )

            # Classe de cor alternada (Verde claro vs Branco)
            bg_class = "row-materia-1" if idx % 2 == 0 else "row-materia-0"

            # Calcular total anual
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

                # Destacar número de aulas > 0
                s_a_html = (
                    f'<td class="{bg_class} aula-destaque">{s_a}</td>'
                    if s_a > 0
                    else f'<td class="{bg_class}">{s_a}</td>'
                )
                t_a_html = (
                    f'<td class="{bg_class} aula-destaque">{t_a}</td>'
                    if t_a > 0
                    else f'<td class="{bg_class}">{t_a}</td>'
                )
                q_a_html = (
                    f'<td class="{bg_class} aula-destaque">{q_a}</td>'
                    if q_a > 0
                    else f'<td class="{bg_class}">{q_a}</td>'
                )
                qui_a_html = (
                    f'<td class="{bg_class} aula-destaque">{qui_a}</td>'
                    if qui_a > 0
                    else f'<td class="{bg_class}">{qui_a}</td>'
                )
                sex_a_html = (
                    f'<td class="{bg_class} aula-destaque">{sex_a}</td>'
                    if sex_a > 0
                    else f'<td class="{bg_class}">{sex_a}</td>'
                )

                html_code += f'<tr class="{bg_class}">'

                # Células mescladas na 1ª Etapa do bloco
                if e == 1:
                    html_code += f'<td rowspan="3" style="font-weight:bold;">{mat}</td>'

                html_code += f"<td>{e}</td>"
                html_code += (
                    f"{s_a_html}<td>{s_d}</td><td>{s_t}</td>"
                    f"{t_a_html}<td>{t_d}</td><td>{t_t}</td>"
                    f"{q_a_html}<td>{q_d}</td><td>{q_t}</td>"
                    f"{qui_a_html}<td>{qui_d}</td><td>{qui_t}</td>"
                    f"{sex_a_html}<td>{sex_d}</td><td>{sex_t}</td>"
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

    else:
        st.info("Nenhuma disciplina lançada até o momento.")
