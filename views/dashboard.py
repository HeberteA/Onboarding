import streamlit as st
import plotly.express as px
import plotly.graph_objects as go  
import pandas as pd
import textwrap

COLOR_MAP = {
    "SIM": "#22c55e", "ANDAMENTO": "#3b82f6", "PENDENTE": "#f59e0b",
    "ENTRADA": "#8b5cf6", "NÃO INICIADO": "#64748b", "NÃO SE APLICA": "#334155"
}

def style_chart(fig):
    """Padroniza o estilo dos gráficos para Dark Mode e ajusta layout"""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#cbd5e1"),
        margin=dict(t=30, l=0, r=0, b=0),
        xaxis=dict(showgrid=False, showticklabels=True),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        coloraxis_showscale=False
    )
    return fig

def render_dashboard(dm):
    st.markdown("## Dashboard")
    
    df_all = dm.get_global_dashboard_data()
    if df_all.empty:
        st.info("Aguardando dados.")
        return

    df_all['status'] = df_all['status'].astype(str).str.strip().str.upper().replace({
        'NAO SE APLICA': 'NÃO SE APLICA', 'NAO INICIADO': 'NÃO INICIADO', 'CONCLUIDO': 'SIM', 'OK': 'SIM'
    })
    
    df_all['item_number'] = df_all['item_number'].astype(str).str.strip()
    mask_real = (df_all['item_number'].str.contains(r'\.', regex=True)) & (~df_all['item_number'].str.endswith('.0'))
    df_raw = df_all[mask_real].copy()

    df_raw['stage'] = df_raw['stage'].fillna("GERAL")
    df_raw['sector'] = df_raw['sector'].fillna("NÃO DEFINIDO")
    df_raw['responsible'] = df_raw['responsible'].fillna("NÃO ATRIBUÍDO")

    projects_list = sorted(df_raw['project_name'].unique().tolist())
    c_filter, _ = st.columns([1, 3])
    with c_filter:
        sel_project = st.selectbox("Escopo da Análise", ["Todas as Obras"] + projects_list)

    if sel_project != "Todas as Obras":
        df_calc = df_raw[df_raw['project_name'] == sel_project]
    else:
        df_calc = df_raw

    st.markdown("---")
        
    st.markdown(f"##### Visão Geral")
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    
  
    total = len(df_calc)
    if total > 0:
        done = len(df_calc[df_calc['status'].isin(['SIM', 'NÃO SE APLICA'])])
        pending = total - done
        
        progresso = int((done / total) * 100)
    else:
        done, pending, progresso = 0, 0, 0
    
    k1, k2, k3, k4 = st.columns(4)
    
    def metric_card(label, val, sub, color):
        return textwrap.dedent(f"""
        <div style="background-color: transparent; background-image: linear-gradient(160deg, #1e1e1f 0%, #0a0a0c 100%); border: 1px solid rgba(255, 255, 255, 0.1); border-radius:10px; padding:15px;">
            <div style="color:#888; font-size:0.75rem; text-transform:uppercase;">{label}</div>
            <div style="color:#fff; font-size:1.8rem; font-weight:700;">{val}</div>
            <div style="color:{color}; font-size:0.85rem;">{sub}</div>
        </div>
        """)
    
    with k1: st.markdown(metric_card("Total", total, "Atividades", "#888"), unsafe_allow_html=True)
    with k2: st.markdown(metric_card("Progresso", f"{progresso}%", f"{done} Concluídos", "#22c55e"), unsafe_allow_html=True)
    with k3: st.markdown(metric_card("Risco", pending, "Andamento / Pendentes", "#f59e0b"), unsafe_allow_html=True)
    
    df_not_done = df_calc[~df_calc['status'].isin(['SIM', 'NÃO SE APLICA'])]

    if sel_project == "Todas as Obras":
        risk_proj = df_not_done['project_name'].value_counts()
        top_risk = risk_proj.index[0] if not risk_proj.empty else "Nenhuma"
        val_risk = risk_proj.iloc[0] if not risk_proj.empty else 0
        lbl_risk = "Obra com Mais Pendências"
    else:
        risk_sec = df_not_done['sector'].value_counts()
        top_risk = risk_sec.index[0] if not risk_sec.empty else "Nenhum"
        val_risk = risk_sec.iloc[0] if not risk_sec.empty else 0
        lbl_risk = "Gargalo (Setor)"
        
    with k4: st.markdown(metric_card(lbl_risk, top_risk, f"{val_risk} Itens", "#E37026"), unsafe_allow_html=True)

    st.markdown("---")

    g1, g2 = st.columns([1.5, 1])

    with g1:
        if sel_project == "Todas as Obras":
            st.markdown("#### Comparativo de Progresso por Obra")
            
            proj_stats = []
            for p in projects_list:
                p_df = df_all[
                    (df_all['project_name'] == p) & 
                    (df_all['item_number'].astype(str).str.strip().str.contains(r'\.', regex=True)) & 
                    (~df_all['item_number'].astype(str).str.strip().str.endswith('.0'))
                ]
                
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
            fig = style_chart(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("#### Distribuição (Etapa > Setor)")
            try:
                df_sun = df_calc.copy()
                df_sun['stage'] = df_sun['stage'].fillna("N/D")
                df_sun['sector'] = df_sun['sector'].fillna("GERAL")
                df_sun['count'] = 1
                fig = px.sunburst(df_sun, path=['stage', 'sector', 'status'], values='count', color='status', color_discrete_map=COLOR_MAP)
                fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
                st.plotly_chart(fig, use_container_width=True)
            except: st.info("Dados insuficientes.")

    with g2:
        st.markdown("#### Top Pendências")
        pending_df = df_calc[df_calc['status'] == 'PENDENTE']
        if not pending_df.empty:
            gargalos = pending_df['sector'].value_counts().reset_index().head(5)
            gargalos.columns = ['Setor', 'Qtd']
            fig_bar = px.bar(gargalos, x='Qtd', y='Setor', orientation='h', color_discrete_sequence=['#E37026'], text="Qtd")
            fig_bar = style_chart(fig_bar)
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.success("Sem pendências críticas.")

    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.markdown("#### Pareto de Gargalos")
        st.caption("Foco em atividades pendentes.")
        
        df_pending = df_calc[df_calc['status'] == 'PENDENTE']
        
        if not df_not_done.empty:
            pareto_data = df_not_done['sector'].value_counts().reset_index()
            pareto_data.columns = ['Setor', 'Qtd']
            pareto_data['Setor'] = pareto_data['Setor'].astype(str)
            pareto_data['Acumulado'] = pareto_data['Qtd'].cumsum() / pareto_data['Qtd'].sum() * 100
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=pareto_data['Setor'], y=pareto_data['Qtd'], name='Pendências', text=pareto_data['Qtd'], marker_color='#ff6503', opacity=0.8))
            fig.add_trace(go.Scatter(x=pareto_data['Setor'], y=pareto_data['Acumulado'], name='Impacto %',  yaxis='y2', line=dict(color='#3b82f6', width=2), mode='lines+markers'))
            
            fig.update_layout(
                yaxis2=dict(overlaying='y', side='right', range=[0, 110], showgrid=False),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", color="#cbd5e1"),
                margin=dict(t=10, l=0, r=0, b=0), legend=dict(orientation="h", y=1.1),
                xaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("Sem gargalos pendentes.")

    with c2:
        st.markdown("#### Performance por Etapa")
        
        stage_stats = []
        for stg in df_calc['stage'].unique():
            s_df = df_calc[df_calc['stage'] == stg]
            s_total = len(s_df)
            if s_total == 0: continue
            s_done = len(s_df[s_df['status'].isin(['SIM', 'NÃO SE APLICA'])])
            s_pct = (s_done/s_total) * 100
            stage_stats.append({'Etapa': str(stg), 'Progresso': s_pct}) 
            
        df_stage = pd.DataFrame(stage_stats).sort_values('Progresso')
        
        if not df_stage.empty:
            fig_bar = px.bar(
                df_stage, x='Progresso', y='Etapa', orientation='h',
                text=df_stage['Progresso'].apply(lambda x: f"{int(x)}%"), 
                color='Progresso', color_continuous_scale=['#334155', '#22c55e']
            )
            fig_bar = style_chart(fig_bar) 
            fig_bar.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Sem dados de etapas.")
            
    st.markdown("---")

    st.markdown("#### Mapa de Calor: Responsáveis")
    
    if sel_project == "Todas as Obras":
        group_col = "project_name"
        x_label = "Obra"
    else:
        group_col = "sector"
        x_label = "Setor"

    df_not_done = df_calc[~df_calc['status'].isin(['SIM', 'NÃO SE APLICA'])]
    df_heat = df_not_done.groupby([group_col, 'responsible']).size().reset_index(name='Qtd')
    
    if not df_heat.empty:
        heatmap_data = df_heat.pivot(index='responsible', columns=group_col, values='Qtd').fillna(0)
        
        fig_heat = px.imshow(
            heatmap_data, 
            labels=dict(x=x_label, y="Responsável", color="Atividades Ativas"),
            color_continuous_scale=['#47362c', '#ff6400'], 
            aspect="auto",
            text_auto=True 
        )
        fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter", color="#cbd5e1"), margin=dict(t=10, l=0, r=0, b=0))
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Dados insuficientes para mapa de calor.")

    st.markdown("#### Radar de Atividades")
    risk_table = df_calc[df_calc['status'] == 'PENDENTE'][['project_name', 'stage', 'responsible', 'status']].head(10)
    st.dataframe(risk_table, use_container_width=True, hide_index=True)


