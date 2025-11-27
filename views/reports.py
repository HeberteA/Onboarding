# views/reports.py
import streamlit as st
import pandas as pd
from datetime import datetime

def render_view(df, arquivo_selecionado):
    st.title(f"📑 Relatórios: {arquivo_selecionado}")
    st.markdown("Ferramenta de exportação e análise de pendências para envio rápido.")

    # 1. Filtros de Relatório
    st.sidebar.markdown("### 🔍 Filtros do Relatório")
    
    # Identificar colunas de projetos dinamicamente
    cols_meta = ["ITENS", "ATIVIDADE", "DESCRIÇÃO", "SETOR", "RESPONSÁVEL", "ETAPA"]
    cols_projetos = [c for c in df.columns if c not in cols_meta]

    status_filter = st.sidebar.multiselect(
        "Filtrar por Status", 
        ["PENDENTE", "ANDAMENTO", "NÃO INICIADO"],
        default=["PENDENTE"]
    )
    
    if "RESPONSÁVEL" in df.columns:
        resp_filter = st.sidebar.multiselect("Filtrar por Responsável", df["RESPONSÁVEL"].unique())
    else:
        resp_filter = []

    # 2. Processamento dos Dados
    # Vamos criar um dataframe focado apenas no que importa (Melting)
    if cols_projetos:
        # Transforma colunas de projetos em linhas para facilitar o filtro
        report_df = df.melt(
            id_vars=[c for c in cols_meta if c in df.columns],
            value_vars=cols_projetos,
            var_name="PROJETO/OBRA",
            value_name="STATUS"
        )
        
        # Aplicar Filtros
        if status_filter:
            report_df = report_df[report_df["STATUS"].isin(status_filter)]
        
        if resp_filter:
            report_df = report_df[report_df["RESPONSÁVEL"].isin(resp_filter)]
            
        # Limpeza para exibição
        display_cols = ["PROJETO/OBRA", "ATIVIDADE", "STATUS", "RESPONSÁVEL", "SETOR", "DESCRIÇÃO"]
        # Garante que só seleciona colunas que existem
        display_cols = [c for c in display_cols if c in report_df.columns]
        
        final_report = report_df[display_cols]
    else:
        st.warning("Não foram encontradas colunas de obras para gerar relatório detalhado.")
        final_report = df

    # 3. Exibição dos Resultados
    st.metric("Itens Encontrados", len(final_report))
    
    st.dataframe(
        final_report, 
        use_container_width=True, 
        hide_index=True,
        height=500
    )

    # 4. Botão de Download
    st.markdown("### 📤 Exportar")
    col1, col2 = st.columns(2)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    file_name = f"Relatorio_{arquivo_selecionado}_{timestamp}.csv"
    
    with col1:
        st.download_button(
            label="Baixar CSV para Excel",
            data=final_report.to_csv(index=False).encode('utf-8'),
            file_name=file_name,
            mime='text/csv',
            type="primary",
            use_container_width=True
        )
    
    with col2:
        if st.button("Copiar Tabela para Clipboard", use_container_width=True):
            final_report.to_clipboard(index=False)
            st.toast("Copiado! Cole no WhatsApp ou Email.", icon="📋")