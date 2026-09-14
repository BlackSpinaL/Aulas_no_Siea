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

    # Edição das 5 etapas/dias
    df_editvel = st.data_editor(
        st.session_state.dias_etapas,
        num_rows="fixed",
        use_container_width=True,
        key="editor_etapas",
    )
    st.session_state.dias_etapas = df_editvel

    # Cálculo da coluna de TOTAL DIAS e linha de TOTAL ETAPAS para conferência
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

    st.markdown("**📋 Tabela de Conferência (com Totais de Linhas e Colunas):**")
    st.dataframe(
        df_conferencia,
        use_container_width=True,
        hide_index=True,
    )
