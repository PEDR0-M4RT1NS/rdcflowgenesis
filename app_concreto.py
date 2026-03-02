import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from io import BytesIO
from sidebar import mostrar_sidebar

# 1. Configuração da página (DEVE SER O PRIMEIRO COMANDO)
st.set_page_config(
    page_title="RDC Gênesis", 
    page_icon="logo_rdc.ico", 
    layout="wide"
)

# 2. Chama a proteção de tela e login
mostrar_sidebar()

# --- NOVO: LÓGICA DE NAVEGAÇÃO ENTRE ABAS ---
# Se o usuário clicar em "Relatórios" na sidebar, o código entra aqui e para o resto
if st.session_state.get('pagina_atual') == "📊 Relatórios Detalhados":
    from relatorios import renderizar_relatorios
    renderizar_relatorios()
    st.stop() # Impede que o formulário de lançamento apareça abaixo do relatório

# --- FUNÇÕES DE AUXÍLIO PARA FORMATAÇÃO RÁPIDA ---
def formatar_hora_input(texto):
    texto = "".join(filter(str.isdigit, texto))
    if len(texto) == 4:
        return f"{texto[:2]}:{texto[2:]}"
    return texto

def formatar_data_input(texto):
    texto = "".join(filter(str.isdigit, texto))
    if len(texto) == 8:
        return f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"
    return texto

def formatar_placa_input(texto):
    texto = texto.upper().replace("-", "").strip()
    if len(texto) == 7:
        return f"{texto[:3]}-{texto[3:]}"
    return texto

# --- CABEÇALHO ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    # Verifique se o arquivo logo_rdc.jpg existe na pasta
    try:
        st.image("logo_rdc.jpg", width=180)
    except:
        st.warning("Arquivo de logo não encontrado.")

with col_tit:
    st.title("RDC - Registro de Concretagem")
    st.subheader("Empreendimento FLOW")

st.divider()

def salvar_dados(dados):
    arquivo = 'historico_concretagem.csv'
    df_novo = pd.DataFrame([dados])
    if not os.path.isfile(arquivo):
        df_novo.to_csv(arquivo, index=False, sep=';', encoding='utf-8-sig')
    else:
        df_novo.to_csv(arquivo, mode='a', header=False, index=False, sep=';', encoding='utf-8-sig')

# --- 3. FORMULÁRIO DE LANÇAMENTO ---
with st.form("form_final", clear_on_submit=True):
    st.subheader("📝 Lançamento Rápido da Carga")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        data_raw = st.text_input("Data (DDMMAAAA)", max_chars=8, help="Digite apenas números")
        data_final = formatar_data_input(data_raw)
        
        numero_nf = st.text_input("Número da NF / Recibo")
        
        placa_raw = st.text_input("PLACA (Somente letras e números)", max_chars=7).upper()
        placa_final = formatar_placa_input(placa_raw)
        
        volume = st.number_input("Volume m³", min_value=0.0, step=0.5)
        fck = st.selectbox("FCK (MPa)", [15, 20, 25, 30, 35, 40, 50])

    with c2:
        valor_unit = st.number_input("VALOR m³ (R$)", min_value=0.0, value=530.0)
        
        h_saida_raw = st.text_input("H. Saída (HHMM)", max_chars=4)
        h_saida_final = formatar_hora_input(h_saida_raw)
        
        h_ini_raw = st.text_input("H. Início Descarga (HHMM)", max_chars=4)
        h_ini_final = formatar_hora_input(h_ini_raw)
        
        h_fim_raw = st.text_input("H. Fim Descarga (HHMM)", max_chars=4)
        h_fim_final = formatar_hora_input(h_fim_raw)
        
        slump_obtido = st.number_input("Slump Test (cm)", value=10.0)

    with c3:
        litros_agua = st.number_input("LITROS ÁGUA (Adição Canteiro)", min_value=0.0)
        destino = st.text_input("DESTINO").upper()
        aditivo = st.text_input("ADITIVO")
        obs = st.text_area("Observações")

    if data_final or placa_final:
        st.caption(f"👀 Prévia: Data: {data_final} | Placa: {placa_final} | Horário: {h_ini_final}")
    
    submit = st.form_submit_button("💾 REGISTRAR CARGA")

if submit:
    try:
        fmt = "%H:%M"
        t_saida = datetime.strptime(h_saida_final, fmt)
        t_inicio = datetime.strptime(h_ini_final, fmt)
        tempo_transporte = t_inicio - t_saida
        valor_total = volume * valor_unit
        status_tempo = "OK" if tempo_transporte <= timedelta(hours=2) and tempo_transporte >= timedelta(0) else "ALERTA (+2h)"

        dados_carga = {
            "DATA": data_final,
            "RECIBO/NF": numero_nf,
            "PLACA": placa_final,
            "FCK": fck,
            "m3": float(volume),
            "DESTINO": destino,
            "SAIDA_USINA": h_saida_final,
            "INICIO_DESC": h_ini_final,
            "FIM_DESC": h_fim_final,
            "TEMPO_TOTAL": str(tempo_transporte),
            "SLUMP": slump_obtido,
            "AGUA_ADD": litros_agua,
            "ADITIVO": aditivo,
            "VALOR_M3": valor_unit,
            "VALOR_TOTAL": float(valor_total),
            "STATUS": status_tempo,
            "OBS": obs
        }
        salvar_dados(dados_carga)
        st.success(f"Registo efetuado! Status: {status_tempo} ({tempo_transporte})")
        st.rerun()
    except Exception as e:
        st.error("Erro nos dados! Verifique se a Data (8 dígitos) e Horários (4 dígitos) estão completos.")

# --- 4. RESUMO RÁPIDO (Visível abaixo do formulário) ---
st.divider()
if os.path.isfile('historico_concretagem.csv'):
    df = pd.read_csv('historico_concretagem.csv', sep=';')
    
    st.subheader("📊 Conferência Rápida (Diária)")
    data_para_filtrar = st.date_input("Filtrar visualização por data:", datetime.now())
    data_formatada = data_para_filtrar.strftime("%d/%m/%Y")
    df_dia = df[df['DATA'] == data_formatada]
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Volume do Dia", f"{df_dia['m3'].sum():.2f} m³")
    k2.metric("Gasto do Dia", f"R$ {df_dia['VALOR_TOTAL'].sum():,.2f}")
    k3.metric("Nº Cargas", len(df_dia))

    # --- ÁREA ADMINISTRATIVA ---
    if st.session_state.get('usuario_nivel') == "ADM":
        st.divider()
        st.subheader("⚙️ Painel de Controle Administrativo")
        st.dataframe(df, use_container_width=True)
        
        tab1, tab2 = st.tabs(["📝 Editar", "❌ Excluir"])
        with tab1:
            id_editar = st.number_input("ID para editar:", min_value=0, max_value=len(df)-1, step=1)
            linha = df.iloc[id_editar]
            with st.form("edicao_rapida"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_vol = st.number_input("Volume", value=float(linha['m3']))
                    e_v_u = st.number_input("Valor Unit", value=float(linha['VALOR_M3']))
                    e_saida = st.text_input("H. Saída (HHMM)", value=str(linha['SAIDA_USINA']).replace(":",""))
                with col_e2:
                    e_ini = st.text_input("H. Início (HHMM)", value=str(linha['INICIO_DESC']).replace(":",""))
                    e_dest = st.text_input("Destino", value=linha['DESTINO'])
                
                if st.form_submit_button("SALVAR EDIÇÃO"):
                    h_s = formatar_hora_input(e_saida)
                    h_i = formatar_hora_input(e_ini)
                    df.at[id_editar, 'm3'] = e_vol
                    df.at[id_editar, 'VALOR_M3'] = e_v_u
                    df.at[id_editar, 'SAIDA_USINA'] = h_s
                    df.at[id_editar, 'INICIO_DESC'] = h_i
                    df.at[id_editar, 'DESTINO'] = e_dest
                    df.to_csv('historico_concretagem.csv', index=False, sep=';', encoding='utf-8-sig')
                    st.rerun()
        with tab2:
            id_del = st.number_input("ID para excluir:", min_value=0, max_value=len(df)-1, step=1, key="del_final")
            if st.button("CONFIRMAR EXCLUSÃO"):
                df = df.drop(df.index[id_del])
                df.to_csv('historico_concretagem.csv', index=False, sep=';', encoding='utf-8-sig')
                st.rerun()