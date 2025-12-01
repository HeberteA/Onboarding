import streamlit as st
from services.data_manager import data_manager

def render_view(df, arquivo_selecionado):
    if df.empty:
        st.info("Nenhum dado encontrado para editar.")
        return

    with st.expander("Filtros de Tabela", expanded=False):
        c1, c2 = st.columns(2)
        setores_disponiveis = df["SETOR"].unique() if "SETOR" in df.columns else []
        resps_disponiveis = df["RESPONSÁVEL"].unique() if "RESPONSÁVEL" in df.columns else []
        
        filtro_setor = c1.multiselect("Setor", setores_disponiveis)
        filtro_resp = c2.multiselect("Responsável", resps_disponiveis)

    df_display = df.copy()
    if filtro_setor and "SETOR" in df_display.columns:
        df_display = df_display[df_display["SETOR"].isin(filtro_setor)]
    if filtro_resp and "RESPONSÁVEL" in df_display.columns:
        df_display = df_display[df_display["RESPONSÁVEL"].isin(filtro_resp)]

    cols_meta = ["ITEM", "ATIVIDADE", "DESCRIÇÃO", "ETAPA", "SETOR", "RESPONSÁVEL"]
    cols_projetos = [c for c in df.columns if c not in cols_meta]

    column_config = {
        "ITEM": st.column_config.TextColumn("Item", disabled=True, width="small"),
        "ATIVIDADE": st.column_config.TextColumn("Atividade", width="medium", disabled=True),
        "DESCRIÇÃO": st.column_config.TextColumn("Descrição", width="large", disabled=True),
        "ETAPA": st.column_config.SelectboxColumn("Etapa", options=data_manager.LISTAS_VALIDACAO["ETAPA"]),
        "SETOR": st.column_config.SelectboxColumn("Setor", options=data_manager.LISTAS_VALIDACAO["SETOR"]),
        "RESPONSÁVEL": st.column_config.SelectboxColumn("Responsável", options=data_manager.LISTAS_VALIDACAO["RESPONSÁVEL"])
    }

    for proj in cols_projetos:
        column_config[proj] = st.column_config.SelectboxColumn(
            proj, 
            options=data_manager.LISTAS_VALIDACAO["STATUS_PROJETO"],
            width="small"
        )

    # Editor
    st.markdown("### Tabela de Lançamentos")
    edited_df = st.data_editor(
        df_display,
        column_config=column_config,
        use_container_width=True,
        num_rows="fixed", 
        hide_index=True,
        height=600,
        key=f"editor_main"
    )

    # Botão de Salvar
    st.markdown("<br>", unsafe_allow_html=True)
    c_save, c_void = st.columns([1, 4])
    
    with c_save:
        if st.button("Salvar Alterações", type="primary", use_container_width=True):
            with st.spinner("Gravando no Banco de Dados..."):
                success, msg = data_manager.save_data(edited_df)
                if success:
                    st.toast(msg, icon="✅")
                else:
                    st.error(msg)