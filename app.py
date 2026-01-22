import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador de Bônus | Controladoria", layout="wide")

# --- LOGIN ---
def check_password():
    if st.secrets.get("PASSWORD") is None: return True
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.text_input("🔒 Senha:", type="password", on_change=password_entered, key="password")
    return False
if not check_password(): st.stop()

# --- DADOS INICIAIS ---
if 'config_multiplos' not in st.session_state:
    data = [
        {"Cargo": "Estagiário", "Mínimo": 0.6, "Parcial": 0.8, "Meta": 1.0, "Superado": 1.2},
        {"Cargo": "Operacional", "Mínimo": 0.6, "Parcial": 0.8, "Meta": 1.0, "Superado": 1.2},
        {"Cargo": "Tático", "Mínimo": 2.0, "Parcial": 4.0, "Meta": 8.0, "Superado": 9.0},
        {"Cargo": "Estratégico", "Mínimo": 2.0, "Parcial": 4.0, "Meta": 8.0, "Superado": 9.0}
    ]
    st.session_state.config_multiplos = pd.DataFrame(data)

if 'config_fator' not in st.session_state:
    st.session_state.config_fator = pd.DataFrame([
        {"Parâmetro": "Fator Global", "Mínimo": 1.0, "Parcial": 1.0, "Meta": 1.0, "Superado": 1.0}
    ])

if 'config_faixas' not in st.session_state:
    st.session_state.config_faixas = pd.DataFrame([
        {"Nível": "Mínimo", "Gatilho": 0.90},
        {"Nível": "Parcial", "Gatilho": 0.95},
        {"Nível": "Meta", "Gatilho": 1.00},
        {"Nível": "Superado", "Gatilho": 1.10}
    ])

if 'kpis_corp' not in st.session_state:
    st.session_state.kpis_corp = [
        {"Indicador": "Receitas", "Peso (%)": 80, "Meta (R$)": 40735845.0, "Realizado (R$)": 38700644.0},
        {"Indicador": "Fluxo de Caixa", "Peso (%)": 20, "Meta (R$)": 16922142.0, "Realizado (R$)": 18154955.0}
    ]

if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = [
        {"ID": 1, "Nome": "João Silva", "Cargo": "Operacional", "Salario": 3500.0, "Tempo_Casa_Meses": 12},
        {"ID": 2, "Nome": "Maria Souza", "Cargo": "Tático", "Salario": 12000.0, "Tempo_Casa_Meses": 12}
    ]

# --- FUNÇÕES DE CÁLCULO ---
def get_gatilhos():
    df = st.session_state.config_faixas
    return {
        'min': df.loc[df['Nível']=='Mínimo', 'Gatilho'].values[0],
        'par': df.loc[df['Nível']=='Parcial', 'Gatilho'].values[0],
        'met': df.loc[df['Nível']=='Meta', 'Gatilho'].values[0],
        'sup': df.loc[df['Nível']=='Superado', 'Gatilho'].values[0]
    }

def interpolar_score_kpi(atingimento):
    # Transforma % de atingimento (ex: 95%) em Score (0.8)
    g = get_gatilhos()
    x = [g['min'], g['par'], g['met'], g['sup']]
    y = [0.6, 0.8, 1.0, 1.2] # Score padrão para compor a nota
    if atingimento < g['min']: return 0.0
    return np.interp(atingimento, x, y)

def interpolar_multiplo_final(nota_final, df_alvo, col_filtro=None, val_filtro=None):
    # Transforma Nota Final (ex: 1.0) em Múltiplo Salarial (ex: 5.0 salários)
    # AQUI ESTAVA O ERRO: A Nota Final JÁ É o eixo X de busca, não precisamos comparar com gatilhos de % de novo.
    # Se a nota é 1.0, buscamos a coluna 'Meta'. Se é 0.8, 'Parcial'.
    
    # Mapeamento Nota -> Coluna
    x_notas = [0.6, 0.8, 1.0, 1.2] # Escala da Nota Ponderada
    
    if col_filtro: row = df_alvo[df_alvo[col_filtro] == val_filtro]
    else: row = df_alvo.iloc[[0]]
    
    if row.empty: return 0.0
    
    y_vals = [
        row['Mínimo'].values[0], row['Parcial'].values[0], 
        row['Meta'].values[0], row['Superado'].values[0]
    ]
    
    # Se a nota for menor que 0.6 (Mínimo da escala de notas), zera
    if nota_final < 0.6: return 0.0
    
    return np.interp(nota_final, x_notas, y_vals)

# --- VISUAL ---
st.title("🎯 Simulador de Bônus Corporativo")
st.markdown("<style>.metric-card {background-color:#f0f2f6;padding:15px;border-radius:10px;border-left:5px solid #1f77b4}</style>", unsafe_allow_html=True)
st.markdown("---")

menu = st.sidebar.radio("Navegação", ["0. Configurações", "1. Indicadores Corporativos", "2. Funcionários", "3. Simulação"])

# --- ABA 0 ---
if menu == "0. Configurações":
    st.header("⚙️ Configurações")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1. Múltiplos (Salários)")
        st.session_state.config_multiplos = st.data_editor(st.session_state.config_multiplos, key="m")
        st.subheader("3. Fator Global")
        st.session_state.config_fator = st.data_editor(st.session_state.config_fator, key="f")
    with c2:
        st.subheader("2. Faixas (%)")
        st.session_state.config_faixas = st.data_editor(st.session_state.config_faixas, key="fx")

# --- ABA 1 ---
elif menu == "1. Indicadores Corporativos":
    st.header("🏢 Indicadores Corporativos")
    
    df_k = pd.DataFrame(st.session_state.kpis_corp)
    edited_k = st.data_editor(df_k, num_rows="dynamic", use_container_width=True,
        column_config={
            "Meta (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
            "Realizado (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
            "Peso (%)": st.column_config.NumberColumn(format="%d %%")
        })
    st.session_state.kpis_corp = edited_k.to_dict('records')
    
    st.divider()
    st.subheader("Apuração")
    
    total_peso = 0
    nota_final = 0
    detalhes = []
    
    g = get_gatilhos()
    
    for item in st.session_state.kpis_corp:
        p = item['Peso (%)']
        m = item['Meta (R$)']
        r = item['Realizado (R$)']
        atg = r/m if m>0 else 0
        
        # Calcula nota deste item (0.6 a 1.2)
        nota = interpolar_score_kpi(atg)
        score = nota * (p/100)
        
        total_peso += p
        nota_final += score
        
        detalhes.append({
            "Indicador": item['Indicador'], "Peso": f"{p}%",
            "Meta (R$)": m, "Realizado (R$)": r,
            "% Ating.": atg, "Nota Item": nota, "Score": score
        })
        
    st.dataframe(pd.DataFrame(detalhes).style.format({
        "Meta (R$)": "R$ {:,.2f}", "Realizado (R$)": "R$ {:,.2f}", 
        "% Ating.": "{:.2%}", "Nota Item": "{:.2f}", "Score": "{:.4f}"
    }), use_container_width=True)
    
    c1, c2 = st.columns(2)
    if total_peso != 100: c1.error(f"Pesos somam {total_peso}%. Ajuste para 100%.")
    else: 
        c1.metric("Nota Final (Score)", f"{nota_final:.4f}")
        st.session_state.nota_final = nota_final

# --- ABA 2 ---
elif menu == "2. Funcionários":
    st.header("👥 Cadastro")
    with st.expander("Novo Funcionário"):
        with st.form("f"):
            nome = st.text_input("Nome")
            cargo = st.selectbox("Cargo", st.session_state.config_multiplos['Cargo'].unique())
            sal = st.number_input("Salário", step=100.0)
            tempo = st.number_input("Meses", 1, 12, 12)
            if st.form_submit_button("Salvar"):
                st.session_state.funcionarios.append({"ID": len(st.session_state.funcionarios)+1, "Nome": nome, "Cargo": cargo, "Salario": sal, "Tempo_Casa_Meses": tempo})
                st.rerun()
    st.data_editor(st.session_state.funcionarios, use_container_width=True)

# --- ABA 3 ---
elif menu == "3. Simulação":
    st.header("💰 Simulação de Pagamento")
    
    if 'nota_final' not in st.session_state:
        st.error("Calcule os Indicadores primeiro.")
    else:
        nota = st.session_state.nota_final
        st.metric("Nota Corporativa Aplicada", f"{nota:.4f}")
        
        if st.button("🚀 Calcular"):
            res = []
            tot = 0
            
            # Fator Global baseado na nota (ex: nota 1.0 -> Fator 1.0)
            fat = interpolar_multiplo_final(nota, st.session_state.config_fator)
            
            for f in st.session_state.funcionarios:
                # Múltiplo baseado na nota (ex: nota 1.0 -> Tático ganha 5.0 salários)
                mult = interpolar_multiplo_final(nota, st.session_state.config_multiplos, "Cargo", f['Cargo'])
                
                # Bônus
                val = f['Salario'] * (f['Tempo_Casa_Meses']/12) * mult * fat * 1.0 # (1.0 = nota indiv default)
                res.append({
                    "Nome": f['Nome'], "Cargo": f['Cargo'], "Salário": f['Salario'],
                    "Múltiplo": mult, "Fator": fat, "Bônus": val
                })
                tot += val
            
            st.metric("Total Folha", f"R$ {tot:,.2f}")
            st.dataframe(pd.DataFrame(res).style.format({
                "Salário": "R$ {:,.2f}", "Bônus": "R$ {:,.2f}", 
                "Múltiplo": "{:.2f}x", "Fator": "{:.2f}"
            }), use_container_width=True)
