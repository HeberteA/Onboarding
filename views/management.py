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

    st.markdown("##### Obra:")

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
        done_global = 0
        pending_global = 0
        pct_global = 0

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.markdown(f"""
        <span style="font-family: 'Inter', sans-serif; font-weight: 700; font-size: 3.75rem; color: white; letter-spacing: 2px;"> {project_name}</span>
        """, unsafe_allow_html=True)
    with c2:
        unique_sectors = sorted([s for s in df['sector'].dropna().unique() if str(s).strip() != ""])
        sel_sector = st.selectbox("Setor", ["Todos"] + unique_sectors)
    with c3:
        sel_status = st.selectbox("Status", ["Todos"] + list(STATUS_COLORS.keys()))

    st.markdown("<div style='margin-bottom: 25px'></div>", unsafe_allow_html=True)

    hero_bar_color = "#35BE53" if pct_global == 100 else "#E37026"

    st.markdown(textwrap.dedent(f"""
    <div style="background-color: transparent !important; background-image: linear-gradient(160deg, #1e1e1f 0%, #0a0a0c 100%) !important; border: 1px solid rgba(255, 255, 255, 0.9) !important; padding: 20px; border-radius: 10px;">
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

        parent_mask = (group_df['
