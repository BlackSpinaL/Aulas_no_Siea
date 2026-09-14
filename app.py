import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Conferência dos Diários - Visualização em Planilha",
    layout="wide",
)

# Lista completa com as 30 disciplinas
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
    st.session_state.dias_etapas = pd.DataFrame(
        {
            "Dia da Semana": [
                "Segunda",
                "Terça",
                "Quarta",
                "Quinta",
                "Sexta",
            ],
            "Etapa 1": [13, 12, 14, 14, 13],
            "Etapa 2": [15, 16, 13, 13, 14],
            "Etapa 3": [12, 12, 13, 13, 13],
        }
    )

if "lancamentos" not in st.session_state:
    st.session_state.lancamentos = []

st.title("📊 Conferência dos Diários - Grade Geral")

aba1, aba2 = st.tabs(
    ["📋 Grade Geral (Estilo Planilha)", "⚙️ Configurações do Ano"]
)

# -------------------------------------------------------------
# ABA 2: CONFIGURAÇÕES
# -------------------------------------------------------------
with aba2:
    st.subheader("⚙️ Configurar Calendário e Disciplinas")
    col_c1, col_c2 = st.columns([1, 1])

    with col_c1:
        st.markdown("### 1. Dias de cada Etapa (Calendário)")
        df_editado = st.data_editor(
            st.session_state.dias_etapas,
            num_rows="fixed",
            use_container_width=True,
            key="editor_etapas",
        )
        st.session_state.dias_etapas = df_editado

    with col_c2:
        st.markdown("### 2. Gerenciar Matérias")
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

# -------------------------------------------------------------
# ABA 1: VISUALIZAÇÃO ESTILO PLANILHA
# -------------------------------------------------------------
with aba1:
    st.markdown("### ✏️ Lançar Nova Matéria na Grade")

    c_m, c_seg, c_ter, c_qua, c_qui, c_sex = st.columns([3, 1, 1, 1, 1, 1])
    with c_m:
        mat_escolhida = st.selectbox(
            "Selecione o Componente Curricular:",
            ["-- Selecione --"] + st.session_state.disciplinas,
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

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("📥 Adicionar Lançamento"):
            if mat_escolhida != "-- Selecione --":
                st.session_state.lancamentos.append({
                    "materia": mat_escolhida,
                    "Seg": seg,
                    "Ter": ter,
                    "Qua": qua,
                    "Qui": qui,
                    "Sex": sex,
                })
                st.success(f"Matéria '{mat_escolhida}' lançada com sucesso!")
                st.rerun()

    with col_btn2:
        if st.session_state.lancamentos and st.button("🗑️ Limpar Todos os Lançamentos"):
            st.session_state.lancamentos = []
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Grade Visual em Tempo Real (Idêntica à Planilha)")

    dias_map = st.session_state.dias_etapas.set_index("Dia da Semana")
    tabela_consolidada = []

    for item in st.session_state.lancamentos:
        mat = item["materia"]
        seg_a, ter_a, qua_a, qui_a, sex_a = (
            item["Seg"],
            item["Ter"],
            item["Qua"],
            item["Qui"],
            item["Sex"],
        )

        tot_anual = 0
        linhas_materia = []

        for e in [1, 2, 3]:
            s_d = dias_map.loc["Segunda", f"Etapa {e}"]
            t_d = dias_map.loc["Terça", f"Etapa {e}"]
            q_d = dias_map.loc["Quarta", f"Etapa {e}"]
            qui_d = dias_map.loc["Quinta", f"Etapa {e}"]
            sex_d = dias_map.loc["Sexta", f"Etapa {e}"]

            s_tot, t_tot, q_tot, qui_tot, sex_tot = (
                seg_a * s_d,
                ter_a * t_d,
                qua_a * q_d,
                qui_a * qui_d,
                sex_a * sex_d,
            )
            tot_etapa = s_tot + t_tot + q_tot + qui_tot + sex_tot
            tot_anual += tot_etapa

            linhas_materia.append({
                "Componente Curricular": mat if e == 1 else "",
                "Etapa": e,
                "Seg (Aulas)": seg_a,
                "Seg (Etapa)": s_d,
                "Seg (Total)": s_tot,
                "Ter (Aulas)": ter_a,
                "Ter (Etapa)": t_d,
                "Ter (Total)": t_tot,
                "Qua (Aulas)": qua_a,
                "Qua (Etapa)": q_d,
                "Qua (Total)": q_tot,
                "Qui (Aulas)": qui_a,
                "Qui (Etapa)": qui_d,
                "Qui (Total)": qui_tot,
                "Sex (Aulas)": sex_a,
                "Sex (Etapa)": sex_d,
                "Sex (Total)": sex_tot,
                "Nº AULAS POR ETAPA": tot_etapa,
                "TOTAL AULAS ANUAL": "",
            })

        if linhas_materia:
            linhas_materia[0]["TOTAL AULAS ANUAL"] = tot_anual
            tabela_consolidada.extend(linhas_materia)

    df_view = pd.DataFrame(tabela_consolidada)

    if not df_view.empty:
        st.dataframe(df_view, use_container_width=True, height=500)

        # Gerar arquivo Excel para download
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_view.to_excel(writer, index=False, sheet_name="Grade_Contagem")

        st.download_button(
            label="📥 Baixar Planilha em Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="Conferência_de_Diarios.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.info("Nenhuma matéria lançada. Adicione uma matéria acima para visualizar a grade.")
