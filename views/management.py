import streamlit as st

STATUS_COLORS = {
    "SIM": "#10B981", "ANDAMENTO": "#3B82F6", "PENDENTE": "#F59E0B",
    "ENTRADA": "#8B5CF6", "NÃO INICIADO": "#64748B", "NÃO SE APLICA": "#334155"
}

def render_management(dm, project_id, project_name):
    
    df_full = dm.get_project_data(project_id)
    
    c_filt1, c_filt2, c_filt3 = st.columns(3)
    with c_filt1:
        st.markdown(f"### Gestão Operacional: {project_name}")
    with c_filt2:
        setores = ["Todos"] + sorted(df_full['sector'].fillna("").unique().tolist())
        setor_sel = st.selectbox("Filtrar por Setor", setores)
    with c_filt3:
        status_sel = st.selectbox("Filtrar por Status", ["Todos"] + sorted(df_full['status'].unique().tolist()))

    df_view = df_full.copy()
    if setor_sel != "Todos": df_view = df_view[df_view['sector'] == setor_sel]
    if status_sel != "Todos": df_view = df_view[df_view['status'] == status_sel]

    if df_view.empty:
        st.info("Nenhuma atividade corresponde aos filtros.")
        return

    df_view['group_id'] = df_view['item_number'].astype(str).str.split('.').str[0]
    unique_groups = sorted(df_view['group_id'].unique(), key=lambda x: int(x) if x.isdigit() else 999)

    for group in unique_groups:
        group_df = df_view[df_view['group_id'] == group]
        if group_df.empty: continue
        
        st.markdown(f"<div style='margin-top:20px; margin-bottom:10px; font-weight:600; color:#94a3b8; font-size:0.9rem; letter-spacing:1px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;'>FASE {group}</div>", unsafe_allow_html=True)
        
        for _, row in group_df.iterrows():
            status_color = STATUS_COLORS.get(row['status'], "#64748B")
            
            with st.container():
                c_bar, c_content, c_action = st.columns([0.08, 3, 1.2])
                
                with c_bar:
                    st.markdown(f"""
                        <div style="
                            background-color: {status_color};
                            height: 60px;
                            width: 6px;
                            border-radius: 4px;
                            margin: auto;
                        "></div>
                    """, unsafe_allow_html=True)
                
                with c_content:
                    st.markdown(f"<div style='font-weight:600; color:#f1f5f9; font-size:1rem;'>{row['item_number']} - {row['title']}</div>", unsafe_allow_html=True)
                    
                    meta_html = ""
                    if row['sector']: meta_html += f"<span style='font-size:0.7rem; background:rgba(255,255,255,0.05); padding:2px 6px; border-radius:4px; color:#cbd5e1; margin-right:5px;'>{row['sector']}</span>"
                    if row['area']: meta_html += f"<span style='font-size:0.7rem; background:rgba(255,255,255,0.05); padding:2px 6px; border-radius:4px; color:#94a3b8;'>{row['area']}</span>"
                    
                    st.markdown(f"<div style='margin-top:4px;'>{meta_html}</div>", unsafe_allow_html=True)
                    
                    if row['description']:
                        st.markdown(f"<div style='font-size:0.8rem; color:#64748b; margin-top:2px; font-style:italic;'>{row['description']}</div>", unsafe_allow_html=True)

                with c_action:
                    opts = list(STATUS_COLORS.keys())
                    current = row['status']
                    idx = opts.index(current) if current in opts else 0
                    
                    def cb(tid=row['task_id'], pid=project_id):
                        val = st.session_state[f"gst_{tid}"]
                        dm.update_single_status(pid, tid, val)
                        st.toast(f"Status salvo: {val}", icon="✅")

                    st.selectbox(
                        "Status", 
                        options=opts, 
                        index=idx, 
                        key=f"gst_{row['task_id']}", 
                        on_change=cb, 
                        label_visibility="collapsed"
                    )