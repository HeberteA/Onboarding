import streamlit as st
import plotly.express as px
import pandas as pd
from utils.styles import card_component

def render_view(df, cat_selecionada):
    if df.empty:
        st.info("Nenhum dado encontrado para esta seleção.")
        return

    # Preparação dos Dados
    cols_meta = ["ITEM", "ATIVIDADE", "DESCRIÇÃO", "ETAPA", "SETOR", "RESPONSÁVEL"]
    cols_projetos = [c for c in df.columns if c not in cols_meta]

    if not cols_projetos:
        st.warning("Selecione uma categoria com obras ativas para ver indicadores.")
        return

    # Cálculos Reais
    all_status = []
    for col in cols_projetos:
        all_status.extend(df[col].astype(str).tolist())
    
    s = pd.Series(all_status)
    total = len(s)
    concluido = s[s == "SIM"].count()
    pendente = s[s == "PENDENTE"].count()
    andamento = s[s == "ANDAMENTO"].count()
    
    taxa = (concluido / total * 100) if total > 0 else 0

    # --- RENDERIZAÇÃO DOS CARDS (GRID) ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(card_component("Taxa de Conclusão", f"{taxa:.1f}%", "+2% vs mês ant.", "positive"), unsafe_allow_html=True)
    with c2:
        st.markdown(card_component("Pendências Críticas", f"{pendente}", "Requer Atenção", "negative"), unsafe_allow_html=True)
    with c3:
        st.markdown(card_component("Em Execução", f"{andamento}", "Fluxo Normal", "neutral"), unsafe_allow_html=True)
    with c4:
        st.markdown(card_component("Total Mapeado", f"{total}", "Itens de Controle", "neutral"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS ESTILIZADOS ---
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.markdown("<h3 style='font-size:16px; color:white; margin-bottom:15px'>Status por Obra</h3>", unsafe_allow_html=True)
        melted = df.melt(id_vars=["ATIVIDADE"], value_vars=cols_projetos, var_name="Obra", value_name="Status")
        
        fig = px.histogram(
            melted, x="Obra", color="Status", barmode="group",
            color_discrete_map={
                "SIM": "#10b981", "PENDENTE": "#ef4444", "ANDAMENTO": "#3b82f6", 
                "NÃO INICIADO": "#334155", "NÃO SE APLICA": "#1e293b"
            }
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#94a3b8", "family": "Inter"},
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", y=1.1)
        )
        fig.update_yaxes(showgrid=True, gridcolor="#334155")
        st.plotly_chart(fig, use_container_width=True)