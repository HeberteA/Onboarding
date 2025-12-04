import streamlit as st
import pandas as pd
import textwrap

PROJECT_TYPES = ["MULTIFAMILIAR", "COMERCIAL", "USO MISTO", "UNIFAMILIAR"]

def render_projects(dm):
    st.markdown("""
    <style>
        /* Card Estilizado */
        div.project-card {
            background-color: transparent; 
            background-image: linear-gradient(160deg, #1e1e1f 0%, #0a0a0c 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s;
        }
        div.project-card:hover {
            border-color: #E37026;
            background: rgba(227, 112, 38, 0.05);
        }
        
        /* Badge de Categoria */
        .category-badge {
            background: rgba(227, 112, 38, 0.15); 
            border: 1px solid rgba(227, 112, 38, 0.5); 
            color: #E37026; 
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.65rem; 
            font-weight: 600; 
            letter-spacing: 1px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## Gerenciar Obras")

    tab_list, tab_new = st.tabs(["Lista de Obras", "Nova Obra"])

    with tab_list:
        df = dm.get_projects_summary()
        
        if df.empty:
            st.info("Nenhuma obra cadastrada. Adicione a primeira na aba ao lado.")
        else:
            cols = st.columns(3)
            
            for index, row in df.iterrows():
                total = row['total_tasks']
                done = row['done_tasks']
                pct = int((done / total) * 100) if total > 0 else 0
                
                bar_color = "#22c55e" if pct == 100 else "#3b82f6"
                
                col = cols[index % 3]
                
                with col:
                    with st.container():
                        st.markdown(textwrap.dedent(f"""
                        <div class="project-card">
                            <div>
                                <div style="display:flex; justify-content:space-between; align-items:start;">
                                    <span style="font-size:1.1rem; font-weight:700; color:#fff; line-height:1.2;">{row['name']}</span>
                                    <span style="font-weight:700; color:{bar_color};">{pct}%</span>
                                </div>
                                <div><span class="category-badge, margin-bottom:8px;">{row['category']}</span></div>
                            </div>
                            <div>
                            </div>
                                <div style="font-size:0.8rem; color:#888; margin-bottom:8px;">
                                    <span>Progresso</span>
                                    <span>{done}/{total}</span>
                                <div style="width:100%; height:8px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden; margin-bottom:15px;">
                                    <div style="width:{pct}%; height:100%; background:{bar_color};"></div>
                                </div>
                            </div>
                        </div>
                        """), unsafe_allow_html=True)
                        
                        c_edit, _, _, c_del = st.columns([1.75, 2, 2, 1.75])
                        
                        with c_edit:
                            if st.button("Editar", key=f"edit_{row['id']}", use_container_width=True):
                                edit_project_dialog(dm, row)
                        
                        with c_del:
                            if st.button("🗑️", key=f"del_{row['id']}", use_container_width=True):
                                delete_project_dialog(dm, row)

    with tab_new:
        st.markdown("#### Cadastro de Nova Obra")
        
        with st.form("new_project_form", clear_on_submit=True):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                new_name = st.text_input("Nome da Obra")
            with col_b:
                new_cat = st.selectbox("Categoria", PROJECT_TYPES)
            
            submitted = st.form_submit_button("Criar Obra", type="primary")
            
            if submitted:
                if not new_name:
                    st.warning("O nome da obra é obrigatório.")
                else:
                    if dm.save_project(new_name, new_cat):
                        st.toast(f"Obra '{new_name}' criada com sucesso!", icon="✅")
                        st.rerun()

@st.dialog("Editar Obra")
def edit_project_dialog(dm, row):
    st.markdown(f"Editando: **{row['name']}**")
    
    name = st.text_input("Nome", value=row['name'])
    
    try:
        cat_idx = PROJECT_TYPES.index(row['category'])
    except:
        cat_idx = 0
        
    category = st.selectbox("Categoria", PROJECT_TYPES, index=cat_idx)
    
    if st.button("Salvar Alterações", type="primary"):
        if dm.save_project(name, category, project_id=row['id']):
            st.toast("Atualizado!", icon="✅")
            st.rerun()

@st.dialog("Excluir Obra")
def delete_project_dialog(dm, row):
    st.warning(f"Tem certeza que deseja excluir **{row['name']}**?")
    st.markdown("Isso apagará **todos** os históricos de status desta obra. Essa ação não pode ser desfeita.")
    
    if st.button("Sim, Excluir Definitivamente", type="primary"):
        if dm.delete_project(row['id']):
            st.toast("Obra excluída.", icon="🗑️")
            st.rerun()
