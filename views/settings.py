import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_settings(dm):
    st.markdown("""
    <style>
        /* Tabs Modernas */
        .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; color: #94a3b8; font-weight: 500; }
        .stTabs [aria-selected="true"] { color: #E37026 !important; border-bottom-color: #E37026 !important; }
        
        /* Container dos Filtros */
        .filter-container {
            background-color: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## Configurações")
    
    tab_activities, tab_lists = st.tabs(["Gerenciar Atividades", "Listas Auxiliares"])

    with tab_activities:
        st.markdown("#### Inventário de Atividades")
        st.caption("Edite em massa setores, responsáveis e dependências. Use os filtros para encontrar itens rapidamente.")

        df_tasks = dm.get_all_tasks_admin()
        df_sectors = dm.get_aux_list('sectors')
        df_resps = dm.get_aux_list('responsibles')
        
        opt_sectors = sorted(df_sectors['name'].tolist()) if not df_sectors.empty else []
        opt_resps = sorted(df_resps['name'].tolist()) if not df_resps.empty else []

        with st.expander("Filtros Avançados", expanded=True):
            c1, c2, c3 = st.columns([1, 1, 2])
            
            with c1:
                f_sector = st.multiselect("Filtrar por Setor", opt_sectors)
            
            with c2:
                f_resp = st.multiselect("Filtrar por Responsável", opt_resps)
            
            with c3:
                f_search = st.text_input("Buscar (Nome ou Item)", placeholder="Ex: 1.1 ou Contratos...")

        df_filtered = df_tasks.copy()
        
        if f_sector:
            df_filtered = df_filtered[df_filtered['sector_name'].isin(f_sector)]
        
        if f_resp:
            df_filtered = df_filtered[df_filtered['resp_name'].isin(f_resp)]
            
        if f_search:
            mask = (
                df_filtered['title'].astype(str).str.contains(f_search, case=False) | 
                df_filtered['item_number'].astype(str).str.contains(f_search, case=False)
            )
            df_filtered = df_filtered[mask]

        edited_df = st.data_editor(
            df_filtered,
            key="tasks_editor_main",
            use_container_width=True,
            height=600,
            hide_index=True,
            column_order=("item_number", "title", "sector_name", "resp_name", "area", "stage", "description"),
            column_config={
                "id": None, 
                "item_number": st.column_config.TextColumn(
                    "Item",  
                    disabled=True, 
                    help="Identificador único"
                ),
                "title": st.column_config.TextColumn(
                    "Atividade",
                    width="large",
                    disabled=True 
                ),
                "sector_name": st.column_config.SelectboxColumn(
                    "Setor",
                    width="medium",
                    options=opt_sectors,
                    required=True
                ),
                "resp_name": st.column_config.SelectboxColumn(
                    "Responsável",
                    width="medium",
                    options=opt_resps
                ),
                "area": st.column_config.TextColumn(
                    "Área"
                ),
                "stage": st.column_config.SelectboxColumn(
                    "Etapa",
                    width="small",
                    options=["PRÉ-OBRA", "EXECUÇÃO", "PÓS-OBRA", "PROJETOS", "DOCUMENTAÇÃO"]
                ),
                "description": st.column_config.TextColumn(
                    "Descrição Técnica",
                    width="large"
                ),
            }
        )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        col_save, _ = st.columns([1, 4])
        with col_save:
            if st.button("Salvar Alterações", type="primary"):
                try:
                    dm.save_task_changes(edited_df)
                    st.toast("Banco de dados atualizado!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    with tab_lists:
        st.markdown("#### Cadastros Básicos")
        st.info("Adicione ou renomeie setores e responsáveis que aparecem nos dropdowns.")
        
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Setores**")
            df_sec = dm.get_aux_list('sectors')
            edit_sec = st.data_editor(
                df_sec, 
                key="edit_sectors", 
                num_rows="dynamic", 
                hide_index=True, 
                use_container_width=True,
                column_config={"id": None, "name": "Nome"}
            )
            if st.button("Salvar Setores"):
                dm.update_aux_list('sectors', edit_sec)
                st.success("Setores atualizados.")
                st.rerun()

        with c2:
            st.markdown("**Responsáveis**")
            df_resp = dm.get_aux_list('responsibles')
            edit_resp = st.data_editor(
                df_resp, 
                key="edit_resps", 
                num_rows="dynamic", 
                hide_index=True, 
                use_container_width=True,
                column_config={"id": None, "name": "Nome"}
            )
            if st.button("Salvar Responsáveis"):
                dm.update_aux_list('responsibles', edit_resp)
                st.success("Responsáveis atualizados.")
                st.rerun()