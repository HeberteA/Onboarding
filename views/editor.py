import streamlit as st
from services.data_manager import data_manager

def render_view(df_ignored, category):
    
    st.markdown(f"### Lançamentos: {category}")

    projetos = data_manager.get_projects_by_category(category)
    
    if not projetos:
        st.warning(f"Nenhuma obra encontrada na categoria {category}.")
        return

    col_sel, col_blank = st.columns([1, 2])
    with col_sel:
        obra_selecionada = st.selectbox("Selecione a Obra:", projetos)

    df_obra = data_manager.get_data_single_project(obra_selecionada)
    
    if df_obra.empty:
        st.info("Carregando catálogo de atividades...")
        return

    column_cfg = {
        "id": st.column_config.Column(hidden=True),
        "ITEM": st.column_config.TextColumn("Item", width="small", disabled=True),
        "ATIVIDADE": st.column_config.TextColumn("Atividade", width="medium", disabled=True),
        "DESCRIÇÃO": st.column_config.TextColumn("Descrição", width="large", disabled=True),
        "ETAPA": st.column_config.TextColumn("Etapa", width="small", disabled=True),
        "SETOR": st.column_config.TextColumn("Setor", width="small", disabled=True),
        "RESPONSÁVEL": st.column_config.TextColumn("Responsável", width="small", disabled=True),
        "STATUS": st.column_config.SelectboxColumn(
            "Status Atual", 
            options=data_manager.LISTAS_VALIDACAO["STATUS_PROJETO"],
            width="medium",
            required=True
        )
    }

    st.markdown("---")
    edited_df = st.data_editor(
        df_obra,
        column_config=column_cfg,
        use_container_width=True,
        hide_index=True,
        height=600,
        key=f"editor_{obra_selecionada}"
    )

    # 4. SALVAR
    if st.button("Salvar Lançamentos", type="primary"):
        p_id = data_manager.current_project_id 
        success, msg = data_manager.save_single_project(edited_df, p_id)
        if success:
            st.toast(msg, icon="✅")
        else:
            st.error(msg)