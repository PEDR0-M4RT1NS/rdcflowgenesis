import streamlit as st
import pandas as pd
from calculadora import renderizar_calculadora
# Certifique-se de que o arquivo relatorios.py existe na mesma pasta
from relatorios import renderizar_relatorios 
import os

def carregar_usuarios():
    try:
        df = pd.read_csv('usuarios.csv')
        if 'nivel' not in df.columns:
            df['nivel'] = 'USER'
            df.to_csv('usuarios.csv', index=False)
        return df
    except:
        df_init = pd.DataFrame({'usuario': ['adm@genesis.com.br'], 'senha': ['genesis123'], 'nome': ['Administrador'], 'nivel': ['ADM']})
        df_init.to_csv('usuarios.csv', index=False)
        return df_init

def mostrar_sidebar():
    df_users = carregar_usuarios()

    if 'logado' not in st.session_state:
        st.session_state['logado'] = False

    # --- TELA DE LOGIN ---
    if not st.session_state['logado']:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("# 🔐 Acesso Gênesis")
            email_login = st.text_input("E-mail corporativo")
            senha_login = st.text_input("Senha", type="password")
            
            if st.button("ENTRAR NO SISTEMA"):
                user_match = df_users[(df_users['usuario'] == email_login) & (df_users['senha'] == str(senha_login))]
                if not user_match.empty:
                    st.session_state['logado'] = True
                    st.session_state['usuario_nome'] = user_match.iloc[0]['nome']
                    st.session_state['usuario_email'] = user_match.iloc[0]['usuario']
                    st.session_state['usuario_nivel'] = user_match.iloc[0]['nivel']
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        st.stop()

    # --- BARRA LATERAL (Pós-Login) ---
    with st.sidebar:
        st.image('logo_rdc.ico', width=100) 
        st.write(f"👤 Logado como: **{st.session_state['usuario_nome']}** ({st.session_state['usuario_nivel']})")
        
        if st.button("SAIR / LOGOUT"):
            st.session_state.clear()
            st.rerun()

        # --- NOVO: MENU DE NAVEGAÇÃO ---
        st.divider()
        st.subheader("📍 Navegação")
        escolha = st.radio(
            "Ir para:",
            ["📝 Lançamentos", "📊 Relatórios Detalhados"],
            key="navegacao_principal"
        )
        st.session_state['pagina_atual'] = escolha

        # --- FERRAMENTAS DE CAMPO ---
        st.divider()
        st.subheader("🛠️ Ferramentas de Campo")
        with st.expander("📐 Calculadora de Cubagem"):
            renderizar_calculadora()

        # --- GESTÃO DE ACESSOS (SÓ PARA QUEM É ADM) ---
        if st.session_state.get('usuario_nivel') == "ADM":
            st.divider()
            st.subheader("👥 Gestão de Acessos")
            with st.expander("Configurações de Usuários"):
                st.dataframe(df_users[['usuario', 'nome', 'nivel']], use_container_width=True)
                
                st.write("**Cadastrar Novo:**")
                n_email = st.text_input("E-mail", key="new_email")
                n_senha = st.text_input("Senha", type="password", key="new_pass")
                n_nome = st.text_input("Nome", key="new_name")
                n_nivel = st.selectbox("Nível", ["USER", "ADM"], key="new_level")
                
                if st.button("➕ ADICIONAR"):
                    if n_email and n_senha and n_nome:
                        nova_linha = pd.DataFrame({'usuario':[n_email], 'senha':[n_senha], 'nome':[n_nome], 'nivel':[n_nivel]})
                        df_up = pd.concat([df_users, nova_linha], ignore_index=True)
                        df_up.to_csv('usuarios.csv', index=False)
                        st.success("Usuário cadastrado!")
                        st.rerun()

                st.write("**Remover:**")
                user_del = st.selectbox("Selecione", df_users['usuario'].tolist(), key="del_select")
                if st.button("❌ REMOVER"):
                    if user_del != "adm@genesis.com.br":
                        df_up = df_users[df_users['usuario'] != user_del]
                        df_up.to_csv('usuarios.csv', index=False)
                        st.rerun()