import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Sistema de Contagem de Aulas", layout="wide"
)

if "disciplinas" not in st.session_state:
    st.session_state.disciplinas = [
        "ARTE",
        "BIOLOGIA",
        "BIOLOGIA NA PRATICA",
        "CIENCIAS",
        "EDUCACAO FISICA",
        "HISTORIA",
        "LINGUA PORTUGUESA",
        "MATEMATICA",
        "QUIMICA",
    ]

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

st.title("📊 Gestão e Conferência de Aulas")

aba1, aba2 = st.tabs(["📝 Lançamento de Aulas", "⚙️ Configurações do Ano"])

with aba2:
    st.subheader("⚙️ Configurar Calendário e Disciplinas")
    col_config1, col_config2 = st.columns([1, 1])

    with col_config1:
        st.markdown("### 1. Dias por Etapa em cada Dia da Semana")
        df_editado = st.data_editor(
            st.session_state.dias_etapas,
            num_rows="fixed",
            use_container_width=True,
            key="editor_etapas",
        )
        st.session_state.dias_etapas = df_editado

    with col_config2:
        st.markdown("### 2. Gerenciar Matérias / Disciplinas")
        nova_materia = st.text_input("Adicionar nova disciplina:")
        if st.button("➕ Adicionar Disciplina"):
            if (
                nova_materia.strip()
                and nova_materia.upper() not in st.session_state.disciplinas
            ):
                st.session_state.disciplinas.append(nova_materia.upper())
                st.session_state.disciplinas.sort()
                st.success(f"'{nova_materia.upper()}' adicionada com sucesso!")
                st.rerun()

        materia_remover = st.selectbox(
            "Remover disciplina:",
            ["-- Selecione --"] + st.session_state.disciplinas,
        )
        if (
            st.button("🗑️ Remover Disciplina")
            and materia_remover != "-- Selecione --"
        ):
            st.session_state.disciplinas.remove(materia_remover)
            st.success(f"'{materia_remover}' removida com sucesso!")
            st.rerun()

with aba1:
    st.subheader("Selecione o Componente Curricular")
    materia_selecionada = st.selectbox(
        "Componente Curricular / Matéria:", st.session_state.disciplinas
    )

    st.markdown("---")
    st.markdown("### Informe o número de aulas por dia da semana:")

    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    col_dias = st.columns(5)
    aulas_por_dia = {}

    for idx, dia in enumerate(dias_semana):
        with col_dias[idx]:
            aulas_por_dia[dia] = st.number_input(
                f"{dia}", min_value=0, max_value=10, value=0, key=f"aula_{dia}"
            )

    df_dias = st.session_state.dias_etapas.set_index("Dia da Semana")

    dados_calculados = []
    totais_etapas = []

    for e in [1, 2, 3]:
        col_etapa = f"Etapa {e}"
        linha = {"Etapa": f"Etapa {e}"}
        total_etapa = 0

        for dia in dias_semana:
            n_aulas = aulas_por_dia[dia]
            n_dias = df_dias.loc[dia, col_etapa]
            subtotal = n_aulas * n_dias

            linha[f"{dia} (Aulas/Dias)"] = f"{n_aulas} x {n_dias}"
            linha[f"Total {dia}"] = subtotal
            total_etapa += subtotal

        linha["TOTAL DA ETAPA"] = total_etapa
        totais_etapas.append(total_etapa)
        dados_calculados.append(linha)

    df_resultado = pd.DataFrame(dados_calculados)

    st.markdown("### 📊 Detalhamento dos Cálculos")
    st.dataframe(df_resultado, use_container_width=True)

    total_anual = sum(totais_etapas)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Etapa 1", f"{totais_etapas[0]} aulas")
    c2.metric("Total Etapa 2", f"{totais_etapas[1]} aulas")
    c3.metric("Total Etapa 3", f"{totais_etapas[2]} aulas")
    c4.metric("TOTAL ANUAL", f"{total_anual} aulas")
