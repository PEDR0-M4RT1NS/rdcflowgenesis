import streamlit as st

def renderizar_calculadora():
    st.write("### 🧮 Calculadora de Volume")
    st.caption("Calcule a cubagem para o pedido:")
    
    # Inputs do usuário
    c = st.number_input("Comprimento (m)", min_value=0.0, step=0.1, key="calc_c")
    l = st.number_input("Largura (m)", min_value=0.0, step=0.1, key="calc_l")
    h = st.number_input("Altura/Espessura (m)", min_value=0.0, step=0.05, key="calc_h")
    
    # Cálculo
    volume_puro = c * l * h
    
    if volume_puro > 0:
        # Adicionando margem de perda (opcional)
        margem = st.slider("Margem de Perda (%)", 0, 15, 5)
        volume_final = volume_puro * (1 + (margem / 100))
        
        st.divider()
        st.metric("Volume Teórico", f"{volume_puro:.2f} m³")
        st.subheader(f"Solicitar: {volume_final:.2f} m³")
        st.caption(f"Incluindo {margem}% de margem de segurança.")
    else:
        st.info("Insira as dimensões para calcular.")