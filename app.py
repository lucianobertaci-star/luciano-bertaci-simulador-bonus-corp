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

# --- INICIALIZAÇÃO DE DADOS ---

# 1. Múltiplos
if 'config_multiplos' not in st.session_state:
    data = [
        {"Cargo": "Estagiário", "Mínimo": 0.6, "Parcial": 0.8, "Meta": 1.0, "Superado": 1.2},
        {"Cargo": "Operacional", "Mínimo": 0.6, "Parcial": 0.8, "Meta": 1.0, "Superado": 1.2},
        {"Cargo": "Tático", "Mínimo": 2.0, "Parcial": 4.0, "Meta": 8.0, "Superado": 9.0},
        {"Cargo": "Estratégico", "Mínimo": 2.0, "Parcial": 4.0, "Meta": 8.0, "Superado": 9.0}
    ]
    st.session_state.config_multiplos = pd.DataFrame(data)

# 2. Fator Global
if 'config_fator' not in st.session_state:
    data_fator = [{"Parâmetro": "Fator Global", "Mínimo": 1.0, "Parcial": 1.0, "Meta": 1.0, "Superado": 1.0}]
    st.session_state.config_fator = pd.DataFrame(data_fator)

# 3. Faixas (Gatilhos)
if 'config_faixas' not in st.session_state:
    data_faixas = [
        {"Nível": "Mínimo", "Gatilho": 0.90},
        {"Nível": "Parcial", "Gatilho": 0.95},
        {"Nível": "Meta", "Gatilho": 1.00},
        {"Nível": "Superado", "Gatilho": 1.10}
    ]
    st.session_state.config_faixas = pd.DataFrame(data_faixas)

# 4. KPIs Corporativos
if 'kpis_corp' not in st.session_state:
    st.session_state.kpis_corp = [
        {"Indicador": "Receitas", "Peso (%)": 80, "Meta (R$)": 40735845.0, "Realizado (R$)": 38700644.0},
        {"Indicador": "Fluxo de Caixa", "Peso (%)": 20, "Meta (R$)": 16922142.0, "Realizado (R$)": 18154955.0}
    ]

# 5. Funcionários
if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = [
        {"ID": 1, "Nome": "João Silva", "Cargo": "Operacional", "Salario": 3500.0, "Tempo_Casa_Meses": 12},
        {"ID": 2, "Nome": "Maria Souza", "Cargo": "Tático", "Salario": 12000.0, "Tempo_Casa_Meses": 12},
        {"ID": 3, "Nome": "Carlos CEO", "Cargo": "Estratégico", "Salario": 45000.0, "Tempo_Casa_Meses": 12}
    ]

# --- FUNÇÃO DE INTERPOLAÇÃO ---
def interpolar_valores(atingimento_corp, df_origem, coluna_chave=None, valor_chave=None):
    try:
        df_faixas = st.session_state.config_faixas
        min_g = df_faixas.loc[df_faixas['Nível']=='Mínimo', 'Gatilho'].values[0]
        par_g = df_faixas.loc[df_faixas['Nível']=='Parcial', 'Gatilho'].values[0]
        meta_g = df_faixas.loc[df_faixas['Nível']=='Meta', 'Gatilho'].values[0]
        super_g = df_faixas.loc[df_faixas['Nível']=='Superado', 'Gatilho'].values[0]
        x_points = [min_g, par_g, meta_g, super_g]
    except: return 0.0

    if coluna_chave and valor_chave:
        row = df_origem[df_origem[coluna_chave] == valor_chave]
    else:
        row = df_origem.iloc[[0]] 
        
    if row.empty: return 0.0
    
    y_points = [
        row['Mínimo'].values[0], row['Parcial'].values[0], 
        row['Meta'].values[0], row['Superado'].values[0]
    ]
    
    if atingimento_corp < min_g: return 0.0
    return np.interp(atingimento_corp, x_points, y_points)

# --- FUNÇÃO AUXILIAR PARA NOTA PADRÃO ---
def interpolar_nota_padrao(atingimento):
    df_faixas = st.session_state.config_faixas
    min_g = df_faixas.loc[df_faixas['Nível']=='Mínimo', 'Gatilho'].values[0]
    par_g = df_faixas.loc[df_faixas['Nível']=='Parcial', 'Gatilho'].values[0]
    meta_g = df_faixas.loc[df_faixas['Nível']=='Meta', 'Gatilho'].values[0]
    super_g = df_faixas.loc[df_faixas['Nível']=='Superado', 'Gatilho'].values[0]
    x = [min_g, par_g, meta_g, super_g]
    y = [0.6, 0.8, 1.0, 1.2]
    
    if atingimento < min_g: return 0.0
    return np.interp(atingimento, x, y)

# --- VISUAL ---
st.title("🎯 Simulador de Bônus Corporativo")
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #1f77b4;}
    .formula-box {background-color: #e8f4f8; padding: 10px; border-radius: 5px; font-family: monospace; color: #0e1117;}
</style>
""", unsafe_allow_html=True)
st.markdown("---")

menu = st.sidebar.radio("Navegação", ["0. Configurações Gerais", "1. Indicadores Corporativos", "2. Gestão de Funcionários", "3. Simulação e Pagamento"])

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
        use_container_width=True
    )
    
    st.subheader("2. Faixas de Atingimento (Gatilhos)")
    st.session_state.config_faixas = st.data_editor(
        st.session_state.config_faixas,
        column_config={
            "Gatilho": st.column_config.NumberColumn(format="%.2f %%", min_value=0.0, max_value=2.0, step=0.01)
        },
        use_container_width=True
    )
    
    st.subheader("3. Fator Global")
    st.session_state.config_fator = st.data_editor(
        st.session_state.config_fator,
        column_config={
            "Mínimo": st.column_config.NumberColumn(format="%.2f"),
            "Parcial": st.column_config.NumberColumn(format="%.2f"),
            "Meta": st.column_config.NumberColumn(format="%.2f"),
            "Superado": st.column_config.NumberColumn(format="%.2f"),
        },
        use_container_width=True
    )

# --- ABA 1: INDICADORES CORPORATIVOS ---
elif menu == "1. Indicadores Corporativos":
    st.header("🏢 Indicadores Corporativos")
    
    st.info("Cadastre os indicadores e seus respectivos pesos e resultados.")
    
    df_kpis = pd.DataFrame(st.session_state.kpis_corp)
    # ALTERAÇÃO: Removido "R$" do formato, mantendo apenas %.2f
    edited_kpis = st.data_editor(
        df_kpis,
        column_config={
            "Peso (%)": st.column_config.NumberColumn(format="%d %%", min_value=0, max_value=100),
            "Meta (R$)": st.column_config.NumberColumn(format="%.2f"),
            "Realizado (R$)": st.column_config.NumberColumn(format="%.2f"),
        },
        num_rows="dynamic",
        use_container_width=True
    )
    st.session_state.kpis_corp = edited_kpis.to_dict('records')
    
    st.divider()
    st.subheader("Apuração dos Resultados")
    
    total_peso = 0
    nota_final_ponderada = 0
    tabela_detalhada = []
    
    df_f = st.session_state.config_faixas
    min_txt = f"{df_f.loc[df_f['Nível']=='Mínimo', 'Gatilho'].values[0]:.0%}"
    par_txt = f"{df_f.loc[df_f['Nível']=='Parcial', 'Gatilho'].values[0]:.0%}"
    met_txt = f"{df_f.loc[df_f['Nível']=='Meta', 'Gatilho'].values[0]:.0%}"
    sup_txt = f"{df_f.loc[df_f['Nível']=='Superado', 'Gatilho'].values[0]:.0%}"
    
    for item in st.session_state.kpis_corp:
        peso = item.get('Peso (%)', 0)
        meta = item.get('Meta (R$)', 0)
        real = item.get('Realizado (R$)', 0)
        
        atingimento = real / meta if meta > 0 else 0
        nota_item = interpolar_nota_padrao(atingimento)
        contrib = nota_item * (peso / 100)
        
        total_peso += peso
        nota_final_ponderada += contrib
        
        tabela_detalhada.append({
            "Indicadores": item['Indicador'],
            "Peso": f"{peso}%",
            "Mínimo": min_txt, "Parcial": par_txt, "Meta": met_txt, "Superado": sup_txt,
            "Meta (R$)": meta,
            "Realizado (R$)": real,
            "% Atingimento": atingimento,
            "Nota Interpolada": nota_item
        })
        
    df_display = pd.DataFrame(tabela_detalhada)
    # ALTERAÇÃO: Formatação visual sem R$
    st.dataframe(
        df_display.style.format({
            "Meta (R$)": "{:,.2f}", 
            "Realizado (R$)": "{:,.2f}",
            "% Atingimento": "{:.2%}",
            "Nota Interpolada": "{:.2f}"
        }),
        use_container_width=True
    )
    
    c1, c2 = st.columns(2)
    if total_peso != 100:
        c1.error(f"⚠️ Soma dos pesos: {total_peso}%. Ajuste para 100%.")
    else:
        c1.metric("Nota Corporativa Final", f"{nota_final_ponderada:.4f}")
        
    st.session_state.nota_corporativa_final = nota_final_ponderada

# --- ABA 2: FUNCIONÁRIOS ---
elif menu == "2. Gestão de Funcionários":
    st.header("👥 Cadastro de Colaboradores")
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
        # ALTERAÇÃO: Salário formatado apenas com números
        st.dataframe(pd.DataFrame(st.session_state.funcionarios).style.format({"Salario": "{:,.2f}"}), use_container_width=True)
        if st.button("Limpar Lista"):
            st.session_state.funcionarios = []
            st.rerun()

# --- ABA 3: SIMULAÇÃO ---
elif menu == "3. Simulação e Pagamento":
    st.header("💰 Simulação de Pagamento")
    
    if 'nota_corporativa_final' not in st.session_state:
        st.warning("⚠️ Calcule os Indicadores Corporativos na Aba 1 primeiro.")
    else:
        nota_corp = st.session_state.nota_corporativa_final
        
        st.markdown("### 📐 Fórmula de Cálculo")
        st.markdown(f"""
        <div class='formula-box'>
        <b>Bônus</b> = (Salário) x (Fator Tempo) x (Múltiplo Cargo [Ref: {nota_corp:.4f}]) x (Nota Individual) x (Fator Global)
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Simulação")
        
        df = pd.DataFrame(st.session_state.funcionarios)
        if not df.empty:
            if "Performance_Individual" not in df.columns: df["Performance_Individual"] = 1.0
            
            edited_df = st.data_editor(
                df,
                column_config={
                    "Performance_Individual": st.column_config.NumberColumn("Nota Indiv.", format="%.2f", step=0.05),
                    "Salario": st.column_config.NumberColumn(format="R$ %.2f")
                },
                hide_index=True, use_container_width=True
            )
            
            if st.button("🚀 Calcular"):
                res = []
                total = 0
                
                fator_glob = interpolar_valores(nota_corp, st.session_state.config_fator)
                
                for i, row in edited_df.iterrows():
                    mult = interpolar_valores(nota_corp, st.session_state.config_multiplos, "Cargo", row['Cargo'])
                    tempo = row['Tempo_Casa_Meses'] / 12
                    indiv = row['Performance_Individual']
                    bonus = row['Salario'] * tempo * mult * indiv * fator_glob
                    
                    res.append({
                        "Nome": row['Nome'], "Cargo": row['Cargo'], "Salário": row['Salario'],
                        "Múltiplo": mult, "Nota Indiv.": indiv, "Fator Global": fator_glob, "Bônus": bonus
                    })
                    total += bonus
                
                df_r = pd.DataFrame(res)
                st.metric("Total Folha", f"R$ {total:,.2f}")
                st.dataframe(df_r.style.format({
                    "Salário": "R$ {:,.2f}", "Bônus": "R$ {:,.2f}", 
                    "Múltiplo": "{:.2f}x", "Nota Indiv.": "{:.0%}", "Fator Global": "{:.2f}"
                }), use_container_width=True)
        else:
            st.warning("Sem funcionários.")
