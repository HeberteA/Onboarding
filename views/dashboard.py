import streamlit as st
import plotly.express as px
import pandas as pd

COLOR_MAP = {
    "SIM": "#22c55e", "ANDAMENTO": "#3b82f6", "PENDENTE": "#f59e0b",
    "ENTRADA": "#8b5cf6", "NÃO INICIADO": "#64748b", "NÃO SE APLICA": "#334155"
}

def update_fig_layout(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#cbd5e1"),
        margin=dict(t=30, l=0, r=0, b=0),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
    )
    return fig

def render_dashboard(dm):
    st.markdown("## Dashboard")
    
    df_all = dm.get_global_dashboard_data()
    if df_all.empty:
        st.info("Nenhum dado encontrado.")
        return

    df_all['status'] = df_all['status'].astype(str).str.strip().str.upper()
    df_all['status'] = df_all['status'].replace({
        'NAO SE APLICA': 'NÃO SE APLICA',
        'NAO INICIADO': 'NÃO INICIADO',
        'CONCLUIDO': 'SIM',
        'OK': 'SIM'
    })
    projects_list = sorted(df_all['project_name'].unique().tolist())
    
    c_filter, _ = st.columns([1, 3])
    with c_filter:
        sel_project = st.selectbox("Filtrar Obra", ["Todas as Obras"] + projects_list)

    if sel_project != "Todas as Obras":
        df = df_all[df_all['project_name'] == sel_project].copy()
        title_suffix = f": {sel_project}"
    else:
        df = df_all.copy()
        title_suffix = " (Consolidado)"

    df['item_number'] = df['item_number'].astype(str).str.strip()
    
    mask_activities = (
        (df['item_number'].str.contains(r'\.', regex=True)) & 
        (~df['item_number'].str.endswith('.0'))
    )
    
    df_calc = df[mask_activities]
    
    k1, k2, k3, k4 = st.columns(4)
    
    st.markdown(f"##### Visão Geral{title_suffix}")
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    total = len(df_calc)
    
    if total > 0:
        done = len(df_calc[df_calc['status'].isin(['SIM', 'NÃO SE APLICA'])])
        pending = len(df_calc[df_calc['status'] == 'PENDENTE'])
        progresso = int((done / total) * 100)
    else:
        done = 0
        pending = 0
        progresso = 0
        
    def metric_card(label, val, sub, color):
        return f"""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:15px;">
            <div style="color:#888; font-size:0.75rem; text-transform:uppercase;">{label}</div>
            <div style="color:#fff; font-size:1.8rem; font-weight:700;">{val}</div>
            <div style="color:{color}; font-size:0.85rem;">{sub}</div>
        </div>
        """
    
    with k1: st.markdown(metric_card("Total", total, "Atividades", "#888"), unsafe_allow_html=True)
    with k2: st.markdown(metric_card("Progresso", f"{progresso}%", f"{done} Concluídos", "#22c55e"), unsafe_allow_html=True)
    with k3: st.markdown(metric_card("Risco", pending, "Pendentes", "#f59e0b"), unsafe_allow_html=True)
    
    if sel_project == "Todas as Obras":
        risk_proj = df[df['status'] == 'PENDENTE']['project_name'].value_counts()
        top_risk = risk_proj.index[0] if not risk_proj.empty else "Nenhuma"
        val_risk = risk_proj.iloc[0] if not risk_proj.empty else 0
        lbl_risk = "Obra com Mais Pendências"
    else:
        risk_sec = df[df['status'] == 'PENDENTE']['sector'].value_counts()
        top_risk = risk_sec.index[0] if not risk_sec.empty else "Nenhum"
        val_risk = risk_sec.iloc[0] if not risk_sec.empty else 0
        lbl_risk = "Gargalo no Setor"
        
    with k4: st.markdown(metric_card(lbl_risk, top_risk, f"{val_risk} Itens", "#E37026"), unsafe_allow_html=True)

    st.markdown("---")

    g1, g2 = st.columns([1.5, 1])

    with g1:
        if sel_project == "Todas as Obras":
            st.markdown("#### Comparativo de Progresso por Obra")
            
            proj_stats = []
            for p in projects_list:
                p_df = df[df['project_name'] == p]
                p_tot = len(p_df)
                p_done = len(p_df[p_df['status'].isin(['SIM', 'NÃO SE APLICA'])])
                p_pct = (p_done / p_tot) * 100 if p_tot > 0 else 0
                proj_stats.append({'Obra': p, 'Progresso': p_pct})
            
            df_proj = pd.DataFrame(proj_stats).sort_values('Progresso', ascending=True)
            
            fig = px.bar(
                df_proj, x='Progresso', y='Obra', orientation='h',
                text=df_proj['Progresso'].apply(lambda x: f"{int(x)}%"),
                color='Progresso', color_continuous_scale=['#333', '#E37026']
            )
            fig = update_fig_layout(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("#### Distribuição (Etapa > Setor)")
            try:
                df['stage'] = df['stage'].fillna("N/D")
                df['sector'] = df['sector'].fillna("GERAL")
                df['count'] = 1
                fig = px.sunburst(df, path=['stage', 'sector', 'status'], values='count', color='status', color_discrete_map=COLOR_MAP)
                fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
                st.plotly_chart(fig, use_container_width=True)
            except: st.info("Dados insuficientes.")

    with g2:
        st.markdown("#### Top Pendências")
        pending_df = df[df['status'] == 'PENDENTE']
        if not pending_df.empty:
            gargalos = pending_df['sector'].value_counts().reset_index().head(5)
            gargalos.columns = ['Setor', 'Qtd']
            fig_bar = px.bar(gargalos, x='Qtd', y='Setor', orientation='h', color_discrete_sequence=['#f59e0b'])
            fig_bar = update_fig_layout(fig_bar)
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.success("Sem pendências críticas.")

    st.markdown("#### Radar de Atividades")
    risk_table = df[df['status'] == 'PENDENTE'][['project_name', 'stage', 'responsible', 'status']].head(10)
    st.dataframe(risk_table, use_container_width=True, hide_index=True)
