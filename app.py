import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador de Bônus | Controladoria", layout="wide")

# --- SISTEMA DE LOGIN ---
def check_password():
    if st.secrets.get("PASSWORD") is None: return True
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.text_input("🔒 Digite a senha de acesso:", type="password", on_change=password_entered, key="password")
    return False

if not check_password(): st.stop()

# --- INICIALIZAÇÃO DE DADOS (SESSION STATE) ---

# 1. Múltiplos
if 'config_multiplos' not in st.session_state:
    data = [
        {"Cargo": "Estagiário", "Mínimo": 0.6, "Parcial": 0.8, "Meta": 1.0, "Superado": 1.2},
        {"Cargo": "Operacional", "Mínimo": 0.6, "Parcial": 0.8, "Meta": 1.0, "Superado": 1.2},
        {"Cargo": "Tático", "Mínimo": 2.0, "Parcial": 4.0, "Meta": 8.0, "Superado": 9.0},
        {"Cargo": "Estratégico", "Mínimo": 2.0, "Parcial": 4.0, "Meta": 8.0, "Superado": 9.0}
    ]
    st.session_state.config_multiplos = pd.DataFrame(data)

# 2. Fator (Novo)
if 'config_fator' not in st.session_state:
    data_fator = [
        {"Parâmetro": "Fator Global", "Mínimo": 1.0, "Parcial": 1.0, "Meta": 1.0, "Superado": 1.0}
    ]
    st.session_state.config_fator = pd.DataFrame(data_fator)

# 3. Faixas
if 'config_faixas' not in st.session_state:
    data_faixas = [
        {"Nível": "Mínimo", "Gatilho": 0.90},
        {"Nível": "Parcial", "Gatilho": 0.95},
        {"Nível": "Meta", "Gatilho": 1.00},
        {"Nível": "Superado", "Gatilho": 1.10}
    ]
    st.session_state.config_faixas = pd.DataFrame(data_faixas)

# 4. Funcionários
if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = [
        {"ID": 1, "Nome": "João Silva", "Cargo": "Operacional", "Salario": 3500.0, "Tempo_Casa_Meses": 12},
        {"ID": 2, "Nome": "Maria Souza", "Cargo": "Tático", "Salario": 12000.0, "Tempo_Casa_Meses": 12},
        {"ID": 3, "Nome": "Carlos CEO", "Cargo": "Estratégico", "Salario": 45000.0, "Tempo_Casa_Meses": 12}
    ]

# --- FUNÇÃO DE INTERPOLAÇÃO GENÉRICA ---
def interpolar_valores(atingimento_corp, df_origem, coluna_chave=None, valor_chave=None):
    # Pega os gatilhos X
    df_faixas = st.session_state.config_faixas
    try:
        x_points = [
            df_faixas.loc[df_faixas['Nível']=='Mínimo', 'Gatilho'].values[0],
            df_faixas.loc[df_faixas['Nível']=='Parcial', 'Gatilho'].values[0],
            df_faixas.loc[df_faixas['Nível']=='Meta', 'Gatilho'].values[0],
            df_faixas.loc[df_faixas['Nível']=='Superado', 'Gatilho'].values[0]
        ]
    except: return 0.0

    # Pega os valores Y
    if coluna_chave and valor_chave:
        row = df_origem[df_origem[coluna_chave] == valor_chave]
    else:
        row = df_origem.iloc[[0]] # Pega a primeira linha (caso do Fator)

    if row.empty: return 0.0
    
    y_points = [
        row['Mínimo'].values[0], row['Parcial'].values[0], 
        row['Meta'].values[0], row['Superado'].values[0]
    ]
    
    # Se não atingiu o gatilho mínimo, é zero
    if atingimento_corp < x_points[0]: return 0.0
    
    return np.interp(atingimento_corp, x_points, y_points)

# --- VISUAL ---
st.title("🎯 Simulador de Bônus Corporativo")
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;}
    .formula-box {background-color: #e8f4f8; padding: 15px; border-radius: 5px; font-family: monospace; color: #0e1117;}
</style>
""", unsafe_allow_html=True)
st.markdown("---")

menu = st.sidebar.radio("Navegação", ["0. Configurações Gerais", "1. Painel Corporativo", "2. Gestão de Funcionários", "3. Simulação e Pagamento"])

# --- ABA 0: CONFIGURAÇÕES ---
if menu == "0. Configurações Gerais":
    st.header("⚙️ Parâmetros do Sistema")
    
    st.subheader("1. Múltiplos Salariais por Cargo")
    st.session_state.config_multiplos = st.data_editor(
        st.session_state.config_multiplos,
        column_config={
            "Mínimo": st.column_config.NumberColumn(format="%.1f"),
            "Parcial": st.column_config.NumberColumn(format="%.1f"),
            "Meta": st.column_config.NumberColumn(format="%.1f"),
            "Superado": st.column_config.NumberColumn(format="%.1f"),
        },
        use_container_width=True,
        key="cfg_mult"
    )
    
    st.subheader("2. Fator Global (Ajuste)")
    st.session_state.config_fator = st.data_editor(
        st.session_state.config_fator,
        column_config={
            "Mínimo": st.column_config.NumberColumn(format="%.2f"),
            "Parcial": st.column_config.NumberColumn(format="%.2f"),
            "Meta": st.column_config.NumberColumn(format="%.2f"),
            "Superado": st.column_config.NumberColumn(format="%.2f"),
        },
        use_container_width=True,
        key="cfg_fat"
    )
    
    st.subheader("3. Faixas de Atingimento (Gatilhos)")
    st.session_state.config_faixas = st.data_editor(
        st.session_state.config_faixas,
        column_config={
            "Gatilho": st.column_config.NumberColumn(format="%.2f %%", min_value=0.0, max_value=2.0, step=0.01)
        },
        use_container_width=True,
        key="cfg_faixa"
    )

# --- ABA 1: CORPORATIVO ---
elif menu == "1. Painel Corporativo":
    st.header("🏢 Desempenho Corporativo")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Indicador: EBITDA/Resultado")
        meta = st.number_input("Meta (R$)", value=10000000.0, step=100000.0, format="%.2f")
        real = st.number_input("Realizado (R$)", value=9800000.0, step=100000.0, format="%.2f")
        atg = real / meta if meta > 0 else 0
    with c2:
        st.subheader("Status")
        st.metric("% Atingimento", f"{atg:.2%}")
        try:
            min_t = st.session_state.config_faixas.loc[st.session_state.config_faixas['Nível']=='Mínimo', 'Gatilho'].values[0]
            if atg < min_t: st.error("❌ Abaixo do Gatilho")
            else: st.success("✅ Elegível")
        except: pass
    st.session_state.atingimento_global = atg

# --- ABA 2: FUNCIONÁRIOS ---
elif menu == "2. Gestão de Funcionários":
    st.header("👥 Cadastro")
    with st.expander("➕ Adicionar Novo", expanded=False):
        with st.form("add"):
            c1, c2, c3 = st.columns(3)
            nome = c1.text_input("Nome")
            cargos = list(st.session_state.config_multiplos['Cargo'].unique())
            cargo = c2.selectbox("Cargo", cargos)
            sal = c3.number_input("Salário", step=100.0)
            tempo = st.number_input("Meses", 1, 12, 12)
            if st.form_submit_button("Salvar"):
                nid = len(st.session_state.funcionarios)+1
                st.session_state.funcionarios.append({"ID": nid, "Nome": nome, "Cargo": cargo, "Salario": sal, "Tempo_Casa_Meses": tempo})
                st.rerun()
    
    if st.session_state.funcionarios:
        st.dataframe(pd.DataFrame(st.session_state.funcionarios).style.format({"Salario": "R$ {:,.2f}"}), use_container_width=True)
        if st.button("Limpar Lista"):
            st.session_state.funcionarios = []
            st.rerun()

# --- ABA 3: SIMULAÇÃO ---
elif menu == "3. Simulação e Pagamento":
    st.header("💰 Simulação de Pagamento (Payroll)")
    
    if 'atingimento_global' not in st.session_state:
        st.warning("Defina o Painel Corporativo primeiro.")
    else:
        atg_global = st.session_state.atingimento_global
        
        # --- EXIBIÇÃO DA FÓRMULA ---
        st.markdown("### 📐 Fórmula de Cálculo")
        st.markdown("""
        <div class='formula-box'>
        <b>Bônus Final</b> = (Salário Base) x (Fator Tempo) x (Múltiplo Cargo) x (Nota Individual) x (Fator Global)
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Atingimento Corporativo Atual: {atg_global:.2%}")
        
        st.divider()
        st.subheader("Avaliação e Cálculo")
        
        df = pd.DataFrame(st.session_state.funcionarios)
        if not df.empty:
            if "Performance_Individual" not in df.columns: df["Performance_Individual"] = 1.0
            
            edited_df = st.data_editor(
                df,
                column_config={
                    "Performance_Individual": st.column_config.NumberColumn("Nota Indiv. (0-1.2)", format="%.2f", step=0.05),
                    "Salario": st.column_config.NumberColumn(format="R$ %.2f")
                },
                hide_index=True, use_container_width=True
            )
            
            if st.button("🚀 Calcular Bônus"):
                res = []
                total = 0
                
                # Interpola o FATOR GLOBAL uma vez só (pois é igual para todos)
                fator_global_calc = interpolar_valores(atg_global, st.session_state.config_fator)
                
                for i, row in edited_df.iterrows():
                    # Interpola o Múltiplo do Cargo
                    mult = interpolar_valores(atg_global, st.session_state.config_multiplos, "Cargo", row['Cargo'])
                    
                    tempo = row['Tempo_Casa_Meses'] / 12
                    indiv = row['Performance_Individual']
                    
                    # FÓRMULA FINAL APLICADA
                    bonus = row['Salario'] * tempo * mult * indiv * fator_global_calc
                    
                    res.append({
                        "Nome": row['Nome'], "Cargo": row['Cargo'], "Salário": row['Salario'],
                        "Múltiplo": mult, "Nota Indiv.": indiv, "Fator Global": fator_global_calc,
                        "Bônus": bonus
                    })
                    total += bonus
                
                df_res = pd.DataFrame(res)
                c1, c2 = st.columns(2)
                c1.metric("Total Folha", f"R$ {total:,.2f}")
                c2.metric("Fator Global Aplicado", f"{fator_global_calc:.2f}")
                
                st.dataframe(df_res.style.format({
                    "Salário": "R$ {:,.2f}", "Bônus": "R$ {:,.2f}", 
                    "Múltiplo": "{:.2f}x", "Nota Indiv.": "{:.0%}", "Fator Global": "{:.2f}"
                }), use_container_width=True)
                
                st.bar_chart(df_res, x="Nome", y="Bônus")
        else:
            st.warning("Sem funcionários.")
