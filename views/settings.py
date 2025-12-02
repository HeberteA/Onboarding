import streamlit as st
import pandas as pd

def render_settings(dm):
    st.markdown("## Configurações e Cadastro")
    st.markdown("Gerencie as informações mestre do sistema. As alterações aqui refletem em **todas** as obras.")

    tab_tasks, tab_lists = st.tabs(["Gerenciar Atividades", "Listas Auxiliares"])

    with tab_tasks:
        st.info("Edite as células abaixo e clique em 'Salvar Alterações'. Você pode alterar descrições, áreas, etapas e realocar responsáveis.")
        
        df_tasks = dm.get_all_tasks_raw()
        
        df_sectors = dm.get_aux_list('sectors')
        df_resps = dm.get_aux_list('responsibles')
        
        options_sectors = df_sectors['name'].tolist() if not df_sectors.empty else []
        options_resps = df_resps['name'].tolist() if not df_resps.empty else []

        edited_df = st.data_editor(
            df_tasks,
            key="task_editor",
            use_container_width=True,
            height=600,
            hide_index=True,
            column_order=["item_number", "title", "area", "stage", "sector_name", "resp_name", "description"],
            column_config={
                "id": None, 
                "item_number": st.column_config.TextColumn("Item", disabled=True, width="small"),
                "title": st.column_config.TextColumn("Atividade", disabled=True, width="medium"),
                "area": st.column_config.TextColumn("Área (Atividade 1)", width="small"),
                "stage": st.column_config.SelectboxColumn(
                    "Etapa",
                    width="small",
                    options=["PRÉ-OBRA", "EXECUÇÃO", "PÓS-OBRA", "DOCUMENTAÇÃO", "PROJETOS"],
                    required=False
                ),
                "sector_name": st.column_config.SelectboxColumn(
                    "Setor",
                    width="medium",
                    options=options_sectors,
                    required=True
                ),
                "resp_name": st.column_config.SelectboxColumn(
                    "Responsável",
                    width="medium",
                    options=options_resps,
                    required=False
                ),
                "description": st.column_config.TextColumn("Descrição Detalhada", width="large"),
            }
        )

        col_btn, _ = st.columns([1, 4])
        with col_btn:
            if st.button("Salvar Alterações nas Atividades", type="primary"):
                try:
                    dm.save_bulk_tasks(edited_df)
                    st.toast("Banco de dados atualizado com sucesso!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    with tab_lists:
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### Setores")
            df_sec = dm.get_aux_list('sectors')
            edited_sec = st.data_editor(
                df_sec, 
                key="sec_editor", 
                num_rows="dynamic", 
                hide_index=True,
                use_container_width=True
            )
            if st.button("Salvar Setores"):
                dm.update_aux_list('sectors', edited_sec)
                st.toast("Setores atualizados!", icon="✅")
                st.rerun()

        with c2:
            st.markdown("#### Responsáveis")
            df_resp = dm.get_aux_list('responsibles')
            edited_resp = st.data_editor(
                df_resp, 
                key="resp_editor", 
                num_rows="dynamic",
                hide_index=True,
                use_container_width=True
            )
            if st.button("Salvar Responsáveis"):
                dm.update_aux_list('responsibles', edited_resp)
                st.toast("Responsáveis atualizados!", icon="✅")
                st.rerun()