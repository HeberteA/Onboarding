import streamlit as st
import plotly.express as px
import pandas as pd

STATUS_COLORS = {
    "SIM": "#10B981",         
    "ANDAMENTO": "#3B82F6",    
    "PENDENTE": "#F59E0B",     
    "ENTRADA": "#8B5CF6",      
    "NÃO INICIADO": "#475569",
    "NÃO SE APLICA": "#1e293b" 
}

def render_dashboard(dm, project_id, project_name):
    st.markdown("""
    <style>
        .metric-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }
        .metric-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
        .metric-value { font-size: 1.8rem; font-weight: 700; color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"## Command Center: <span style='color:var(--primary-color)'>{project_name}</span>", unsafe_allow_html=True)
    
    df = dm.get_project_data(project_id)
    if df.empty:
        st.info("Aguardando dados para gerar inteligência.")
        return

    total = len(df)
    concluidos = len(df[df['status'] == 'SIM'])
    atencao = len(df[df['status'].isin(['PENDENTE', 'ENTRADA'])])
    progresso = (concluidos / total) * 100 if total > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Items</div><div class="metric-value">{total}</div></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="metric-card"><div class="metric-label">Concluídos</div><div class="metric-value" style="color:#10B981">{concluidos}</div></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="metric-card"><div class="metric-label">Atenção</div><div class="metric-value" style="color:#F59E0B">{atencao}</div></div>""", unsafe_allow_html=True)
    with c4: st.markdown(f"""<div class="metric-card"><div class="metric-label">Progresso</div><div class="metric-value">{int(progresso)}%</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns([1.5, 1])

    with col_chart1:
        st.markdown("##### Distribuição Hierárquica")
        
        df_sun = df.copy()
        df_sun['sector'] = df_sun['sector'].fillna("SEM SETOR") 
        df_sun['status'] = df_sun['status'].fillna("NÃO INICIADO")
        df_sun['count'] = 1
        
        try:
            fig_sun = px.sunburst(
                df_sun, 
                path=['sector', 'status'], 
                values='count',
                color='status',
                color_discrete_map=STATUS_COLORS
            )
            fig_sun.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=14)
            )
            st.plotly_chart(fig_sun, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {e}")

    with col_chart2:
        st.markdown("##### Gargalos Operacionais")
        pending_df = df[~df['status'].isin(['SIM', 'NÃO SE APLICA', 'NÃO INICIADO'])]
        
        if not pending_df.empty:
            gargalos = pending_df['sector'].value_counts().reset_index().head(5)
            gargalos.columns = ['Setor', 'Pendências']
            
            fig_bar = px.bar(
                gargalos, x='Pendências', y='Setor', orientation='h',
                color='Pendências', color_continuous_scale=['#3B82F6', '#F59E0B', '#EF4444']
            )
            fig_bar.update_layout(
                yaxis=dict(autorange="reversed"), xaxis=dict(showgrid=False),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#cbd5e1", family="Inter"),
                margin=dict(t=0, l=0, r=0, b=0), coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.success("Fluxo operacional fluindo.")