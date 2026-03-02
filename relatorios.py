import streamlit as st
import pandas as pd
import os

def renderizar_relatorios():
    st.title("📊 Relatórios Detalhados")
    st.subheader("Filtro por Período e Local")
    
    if not os.path.exists('historico_concretagem.csv'):
        st.error("Ainda não existem dados de concretagem lançados.")
        return

    # Lemos o banco de dados
    df = pd.read_csv('historico_concretagem.csv', sep=';')
    
    # Garantimos que a coluna DATA seja entendida como data real pelo Python
    df['DATA_DT'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')

    # --- FILTROS NO TOPO ---
    with st.container():
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            d_ini = st.date_input("Data Inicial", df['DATA_DT'].min())
        with c2:
            d_fim = st.date_input("Data Final", df['DATA_DT'].max())
        with c3:
            locais = ["TODOS"] + sorted(df['DESTINO'].unique().tolist())
            local_sel = st.selectbox("Filtrar por Local", locais)

    # APLICANDO OS FILTROS
    mask = (df['DATA_DT'] >= pd.to_datetime(d_ini)) & (df['DATA_DT'] <= pd.to_datetime(d_fim))
    if local_sel != "TODOS":
        mask = mask & (df['DESTINO'] == local_sel)
    
    df_filtrado = df.loc[mask].copy()

    # --- RESULTADOS ---
    st.divider()
    if df_filtrado.empty:
        st.warning("Nenhum registro encontrado para esse filtro.")
    else:
        # KPIs do Período
        m1, m2, m3 = st.columns(3)
        m1.metric("Volume Total", f"{df_filtrado['m3'].sum():.2f} m³")
        m2.metric("Investimento", f"R$ {df_filtrado['VALOR_TOTAL'].sum():,.2f}")
        m3.metric("Caminhões", len(df_filtrado))

        # Tabela de resultados
        st.dataframe(df_filtrado.drop(columns=['DATA_DT']), use_container_width=True)
        
        # Resumo por Destino (Gráfico)
        st.write("### Consumo por Destino")
        resumo = df_filtrado.groupby('DESTINO')['m3'].sum().reset_index()
        st.bar_chart(data=resumo, x='DESTINO', y='m3')