import streamlit as st
import pandas as pd
import textwrap

STATUS_COLORS = {
    "SIM": "#35BE53",         
    "PENDENTE": "#f59e0b",      
    "ANDAMENTO": "#3b82f6",    
    "NÃO SE APLICA": "#65686b" 
}

def render_management(dm, project_id, project_name):
    st.markdown("""
<style>
/* Remove fundo das colunas */
div[data-testid="column"] { 
    background: radial-gradient(circle at 10% 20%, #3b3b3b 0%, #000000 100%);
    font-family: 'Inter', sans-serif;
    color: #ffffff;
 }

/* Expander Header Minimalista */
.streamlit-expanderHeader {
    background-color: transparent !important;
    background-image: linear-gradient(160deg, #2b2b2b 0%, #0a0a0c 100%) !important;
    
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 30px;
    border-radius: 10px !important;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.7) !important;
    margin-top: 10px;
}
.streamlit-expanderHeader:hover {
    background-color: transparent !important;
    background-image: linear-gradient(160deg, #1e1e1f 0%, #0a0a0c 100%) !important;
    text-decoration: underline;
}
.streamlit-expanderContent {
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding-left: 12px !important;
    border-left: 1px dashed rgba(255,255,255,0.1) !important;
    margin-left: 10px !important;
}
/* Selectbox Style */
.stSelectbox div[data-baseweb="select"] > div {
    border-radius: 6px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    font-size: 0.85rem !important;
    min-height: 32px !important;
}
</style>
    """, unsafe_allow_html=True)

    proj_details = dm.get_project_details(project_id)
    category = proj_details.get("category", "GERAL") if proj_details else "GERAL"
    
    df = dm.get_project_data(project_id)
    if df.empty:
        st.info("Nenhuma atividade cadastrada.")
        return

    total_global = len(df)
    if total_global > 0:
        done_global = len(df[df['status'].isin(['SIM', 'NÃO SE APLICA'])])
        pending_global = total_global - done_global
        pct_global = int((done_global / total_global) * 100)
    else:
        done_global, pending_global, pct_global = 0, 0, 0

    hero_bar_color = "#35BE53" if pct_global == 100 else "#3b82f6"
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <span style="font-family: 'Inter', sans-serif; font-size: 0.7rem; color: var(--primary); text-transform: uppercase; letter-spacing: 3px; text-transform: uppercase;">GERENCIAMENTO DE OBRA</span>
            <div style="display: flex; align-items: center; gap: 15px; margin-top: 5px;">
                <span style="font-family: 'Inter', sans-serif; font-weight: 700; font-size: 3.75rem; color: white; letter-spacing: 2px; letter-spacing: 1px;">{project_name}</span>
                <span style="background: rgba(227, 112, 38, 0.15); border: 1px solid rgba(227, 112, 38, 0.5); color: #E37026; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; letter-spacing: 1px;">{category}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        unique_sectors = sorted([s for s in df['sector'].dropna().unique() if str(s).strip() != ""])
    with c2:
        st.space("small")
        sel_sector = st.selectbox("Setor", ["Todos"] + unique_sectors)
    with c3:
        st.space("small")
        sel_status = st.selectbox("Status", ["Todos"] + list(STATUS_COLORS.keys()))

    st.markdown("<div style='margin-bottom: 25px'></div>", unsafe_allow_html=True)

    hero_bar_color = "#35BE53" if pct_global == 100 else "#3b82f6"

    st.markdown(textwrap.dedent(f"""
    <div style="background-color: transparent !important; background-image: linear-gradient(160deg, #1e1e1f 0%, #0a0a0c 100%) !important; border: 1px solid rgba(255, 255, 255, 0.9) !important;">
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 12px;">
            <div>
                <div style="font-size: 0.75rem; color: #FFFFFF; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px;">Status Geral da Obra</div>
                <div style="font-size: 2rem; font-weight: 700; color: #fff; line-height: 1;">
                    {pct_global}% 
                    <span style="font-size: 1rem; color: #888; font-weight: 400; margin-left: 5px;">Concluído</span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1rem; color: #ccc; font-weight: 600;">
                    <span style="color: #fff;">{done_global}</span> <span style="color:#666;">/ {total_global}</span> Itens
                </div>
                <div style="font-size: 0.85rem; color: #f59e0b; margin-top: 4px; font-weight: 500;">
                    {pending_global} Pendentes
                </div>
            </div>
        </div>
        <div style="width: 100%; height: 10px; background-color: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden;">
            <div style="width: {pct_global}%; height: 100%; background-color: {hero_bar_color}; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 10px {hero_bar_color}80;"></div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    df['root_id'] = df['item_number'].astype(str).apply(lambda x: x.split('.')[0])
    unique_roots = sorted(df['root_id'].unique(), key=lambda x: int(x) if x.isdigit() else 999)

    found_any = False

    for root in unique_roots:
        group_df = df[df['root_id'] == root]

        if not group_df.empty:
            phase_name_db = group_df.iloc[0]['phase_title'] 
            phase_label = f"{root} - {phase_name_db}"
        else:
            phase_label = f"FASE {root}"

        children = group_df

        filtered_children = children.copy()
        if sel_sector != "Todos": filtered_children = filtered_children[filtered_children['sector'] == sel_sector]
        if sel_status != "Todos": filtered_children = filtered_children[filtered_children['status'] == sel_status]

        if filtered_children.empty: continue
        found_any = True

        total = len(children)
        if total > 0:
            done_count = len(children[children['status'].isin(['SIM', 'NÃO SE APLICA'])])
            pending_count = total - done_count
            pct = int((done_count / total) * 100)
        else:
            done_count = 0
            pending_count = 0
            pct = 0

        if pct == 100:
            border_color = STATUS_COLORS["SIM"]
            progress_bar_color = STATUS_COLORS["SIM"]
        else:
            border_color = "#3b82f6" 
            progress_bar_color = "#3b82f6"

        html_card = textwrap.dedent(f"""
<div style="background-color: transparent; background-image: linear-gradient(160deg, #1e1e1f 0%, #0a0a0c 100%); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid {border_color}; border-radius: 8px; padding: 15px 20px; margin-top: 15px; display: flex; align-items: center; justify-content: space-between; backdrop-filter: blur(10px);">
    <div style="font-weight: 600; color: #ffffff; font-size: 1.05rem; letter-spacing: 0.5px; flex-grow: 1;">
        {phase_label}
    </div>
    <div style="display: flex; align-items: center;">
        <div style="display: flex; gap: 15px; margin-right: 20px; border-right: 1px solid rgba(255,255,255,0.1); padding-right: 20px;">
            <div style="text-align: right;">
                <div style="font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px;">Total</div>
                <div style="font-size: 0.95rem; font-weight: 700;">
                    <span style="color: #b6c0cfff;">{total}</span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px;">Pendente</div>
                <div style="font-size: 0.95rem; color: #f59e0b; font-weight: 700;">{pending_count}</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="font-size: 0.9rem; color: #ccc; font-weight: 600; min-width: 35px; text-align: right;">{pct}%</div>
            <div style="width: 100px; height: 6px; background-color: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
                <div style="width: {pct}%; height: 100%; background-color: {progress_bar_color}; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);"></div>
            </div>
        </div>
    </div>
</div>
""")
        st.markdown(html_card, unsafe_allow_html=True)

        with st.expander("Ver atividades", expanded=False):
            for _, row in filtered_children.iterrows():
                current_status = row['status']
                if current_status not in STATUS_COLORS: current_status = "PENDENTE"
                status_color = STATUS_COLORS.get(current_status, "#64748b")

                with st.container():
                    c_vis, c_info, c_act = st.columns([0.05, 3.5, 1.2])

                    with c_vis:
                        st.markdown(f"""<div style="height:100%; min-height:55px; width:4px; background:{status_color}; border-radius:4px; margin-top:4px;"></div>""", unsafe_allow_html=True)

                    with c_info:
                        st.markdown(f"<div style='font-weight:500; color:#fff; font-size:0.95rem;'>{row['item_number']} - {row['title']}</div>", unsafe_allow_html=True)
                        if row['description']:
                            st.markdown(f"<div style='color:#aaa; font-size:0.85rem; margin-top:3px; line-height:1.4;'>{row['description']}</div>", unsafe_allow_html=True)

                        tags = []
                        if row['responsible']:
                            tags.append(f"<span style='background:rgba(227, 112, 38, 0.15); padding:2px 8px; border-radius:4px; font-size:0.7rem; color:#E37026; border:1px solid rgba(227, 112, 38, 0.2);'> {row['responsible']}</span>")
                        if row['sector']: 
                            tags.append(f"<span style='background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:4px; font-size:0.7rem; color:#ccc; border:1px solid rgba(255,255,255,0.3);'> {row['sector']}</span>")
                        if row['stage']:
                            tags.append(f"<span style='background:rgba(59, 130, 246, 0.1); padding:2px 8px; border-radius:4px; font-size:0.7rem; color:#60a5fa; border:1px solid rgba(59, 130, 246, 0.2);'> {row['stage']}</span>")
                        if row['area']: 
                            tags.append(f"<span style='background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px; font-size:0.7rem; color:#ccc; border:1px solid rgba(255,255,255,0.1);'>{row['area']}</span>")

                        if tags:
                            st.markdown(f"<div style='margin-top:8px; display:flex; gap:8px; align-items:center; flex-wrap:wrap;'>{''.join(tags)}</div>", unsafe_allow_html=True)
                    
                    with c_act:
                        key_unique = f"st_{project_id}_{row['task_id']}"
                        opts = list(STATUS_COLORS.keys())

                        def on_change(tid=row['task_id'], pid=project_id, k=key_unique):
                            dm.update_single_status(pid, tid, st.session_state[k])

                        idx = opts.index(current_status) if current_status in opts else 1
                        st.selectbox("Status", opts, index=idx, key=key_unique, on_change=on_change, label_visibility="collapsed")

                st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,0.05); margin: 10px 0;'></div>", unsafe_allow_html=True)

    if not found_any:
        st.warning("Nenhuma atividade encontrada.")
