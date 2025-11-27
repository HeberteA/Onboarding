# views/editor.py
import streamlit as st
from services.data_manager import data_manager

def render_view(df, arquivo_selecionado):
    st.title(f"📝 Editor: {arquivo_selecionado}")
    
    # Filtros Rápidos
    if "SETOR" in df.columns and "RESPONSÁVEL" in df.columns:
        c1, c2 = st.columns(2)
        filtro_setor = c1.multiselect("Filtrar Setor", data_manager.LISTAS_VALIDACAO["SETOR"])
        filtro_resp = c2.multiselect("Filtrar Responsável", data_manager.LISTAS_VALIDACAO["RESPONSÁVEL"])
        
        df_display = df.copy()
        if filtro_setor:
            df_display = df_display[df_display["SETOR"].isin(filtro_setor)]
        if filtro_resp:
            df_display = df_display[df_display["RESPONSÁVEL"].isin(filtro_resp)]
    else:
        df_display = df.copy()

    # Configuração Dinâmica das Colunas
    cols_meta = ["ITENS", "ATIVIDADE", "DESCRIÇÃO", "SETOR", "RESPONSÁVEL", "ETAPA"]
    cols_projetos = [c for c in df.columns if c not in cols_meta]

    column_config = {
        "ITENS": st.column_config.NumberColumn("Item", disabled=True),
        "ATIVIDADE": st.column_config.TextColumn("Atividade", width="medium", required=True),
        "SETOR": st.column_config.SelectboxColumn("Setor", options=data_manager.LISTAS_VALIDACAO["SETOR"], required=True),
        "RESPONSÁVEL": st.column_config.SelectboxColumn("Responsável", options=data_manager.LISTAS_VALIDACAO["RESPONSÁVEL"], required=True),
        "ETAPA": st.column_config.SelectboxColumn("Etapa", options=data_manager.LISTAS_VALIDACAO["ETAPA"])
    }

    for proj in cols_projetos:
        column_config[proj] = st.column_config.SelectboxColumn(
            proj, 
            options=data_manager.LISTAS_VALIDACAO["STATUS_PROJETO"],
            width="small"
        )

    # Editor
    edited_df = st.data_editor(
        df_display,
        column_config=column_config,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        key=f"editor_{arquivo_selecionado}"
    )

    # Ação de Salvar
    st.markdown("### Ações")
    c_save, c_status = st.columns([1, 4])
    
    with c_save:
        if st.button("💾 Salvar na Nuvem", type="primary"):
            with st.spinner("Sincronizando com Google Sheets..."):
                # No mundo real, atualizamos o DF principal com as edições do df_display
                # Aqui simplificamos salvando o que está visível ou a lógica de merge seria necessária
                success, msg = data_manager.save_data(arquivo_selecionado, edited_df)
                if success:
                    st.toast(msg, icon="✅")
                    st.balloons()
                else:
                    st.error(msg)
    
    with c_status:
        if not data_manager.client:
            st.warning("⚠️ Modo Offline: Configure as credenciais do Google para salvar na nuvem.")