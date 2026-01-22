import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador de Bônus | Controladoria", layout="wide")

# --- HELPER FORMATADOR (Padrão BR: 1.000,00) ---
def formatar_br(valor):
    if isinstance(valor, (int, float)):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor

# --- SISTEMA DE LOGIN ---
def check_password():
    if st.secrets.get("PASSWORD") is None: return True
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.text_input("🔒 Digite a senha de acesso:", type="password", on_change=password_entered, key="password")
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
def get_escala_padrao(): return [0.6, 0.8, 1.0, 1.2]

def interpolar_nota_kpi(atingimento_pct):
    df_faixas = st.session_state.config_faixas
    try:
        x_gatilhos = [
            df_faixas.loc[df_faixas['Nível']=='Mínimo', 'Gatilho'].values[0],
            df_faixas.loc[df_faixas['Nível']=='Parcial', 'Gatilho'].values[0],
            df_faixas.loc[df_faixas['Nível']=='Meta', 'Gatilho'].values[0],
            df_faixas.loc[df_faixas['Nível']=='Superado', 'Gatilho'].values[0]
        ]
    except: return 0.0
    y_scores = get_escala_padrao()
    if atingimento_pct < x_gatilhos[0]: return 0.0
    return np.interp(atingimento_pct, x_gatilhos, y_scores)

def buscar_valor_degrau(nota_final_score, df_origem, col_filtro=None, val_filtro=None):
    if col_filtro and val_filtro: row = df_origem[df_origem[col_filtro] == val_filtro]
    else: row = df_origem.iloc[[0]]
    if row.empty: return 0.0
    row = row.iloc[0]
    if nota_final_score >= 1.2: return row['Superado']
    elif nota_final_score >= 1.0: return row['Meta']
    elif nota_final_score >= 0.8: return row['Parcial']
    elif nota_final_score >= 0.6: return row['Mínimo']
    else: return 0.0

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

# --- ABA 0: CONFIGURAÇÕES (VERTICALIZADA) ---
if menu == "0. Configurações Gerais":
    st.header("⚙️ Parâmetros do Sistema")
    
    st.subheader("1. Múltiplos Salariais por Cargo")
    st.session_state.config_multiplos = st.data_editor(
        st.session_state.config_multiplos,
        column_config={
            "Mínimo": st.column_config.NumberColumn(format="%.1f"),
            "Parcial": st.column_config.NumberColumn(format="%.1f"),
            "Meta": st.column_config.NumberColumn(format="%.1f"),
            "Superado": st.column_config.NumberColumn(format="%.1f")
        }, use_container_width=True
    )
    
    st.divider() # Divisor
    
    st.subheader("2. Faixas de Atingimento (%)")
    st.session_state.config_faixas = st.data_editor(
        st.session_state.config_faixas,
        column_config={
            "Gatilho": st.column_config.NumberColumn(format="%.2f %%", min_value=0.0, max_value=2.0, step=0.01)
        }, use_container_width=True
    )
    
    st.divider() # Divisor
    
    st.subheader("3. Fator Global (Ajuste)")
    st.session_state.config_fator = st.data_editor(
        st.session_state.config_fator,
        column_config={
            "Mínimo": st.column_config.NumberColumn(format="%.2f"),
            "Parcial": st.column_config.NumberColumn(format="%.2f"),
            "Meta": st.column_config.NumberColumn(format="%.2f"),
            "Superado": st.column_config.NumberColumn(format="%.2f")
        }, use_container_width=True
    )

# --- ABA 1: INDICADORES (FORMATAÇÃO BR) ---
elif menu == "1. Indicadores Corporativos":
    st.header("🏢 Indicadores Corporativos")
    
    df_k = pd.DataFrame(st.session_state.kpis_corp)
    edited_k = st.data_editor(
        df_k,
        column_config={
            "Peso (%)": st.column_config.NumberColumn(format="%d %%", min_value=0, max_value=100),
            "Meta (R$)": st.column_config.NumberColumn(format="%.2f", min_value=0.0),
            "Realizado (R$)": st.column_config.NumberColumn(format="%.2f", min_value=0.0)
        }, num_rows="dynamic", use_container_width=True
    )
    st.session_state.kpis_corp = edited_k.to_dict('records')
    
    st.divider()
    st.subheader("Apuração dos Resultados")
    
    total_peso = 0
    nota_final = 0
    detalhes = []
    
    df_f = st.session_state.config_faixas
    cols_lbl = ["Mínimo", "Parcial", "Meta", "Superado"]
    g_str = [f"{df_f.loc[df_f['Nível']==c, 'Gatilho'].values[0]:.0%}" for c in cols_lbl]
    
    for item in st.session_state.kpis_corp:
        p = item.get('Peso (%)', 0)
        m = item.get('Meta (R$)', 0)
        r = item.get('Realizado (R$)', 0)
        atg = r/m if m>0 else 0
        nota = interpolar_nota_kpi(atg)
        score = nota * (p/100)
        total_peso += p
        nota_final += score
        
        # Formatação manual BR para exibição na tabela
        detalhes.append({
            "Indicador": item.get('Indicador',''), 
            "Peso": f"{p}%",
            "Mínimo": g_str[0], "Parcial": g_str[1], "Meta": g_str[2], "Superado": g_str[3],
            "Meta (R$)": formatar_br(m),
            "Realizado (R$)": formatar_br(r),
            "% Ating.": f"{atg:.2%}", 
            "Nota": f"{nota:.2f}"
        })
    
    # Exibe tabela como texto (já formatado no loop)
    st.table(pd.DataFrame(detalhes))
    
    c1, c2 = st.columns(2)
    if total_peso != 100: c1.error(f"Pesos: {total_peso}%. Ajuste para 100%.")
    else:
        c1.metric("Nota Corporativa Final (Score)", f"{nota_final:.4f}")
        st.session_state.nota_corporativa_final = nota_final

# --- ABA 2: FUNCIONÁRIOS (GRID EXCEL COM ADD/DEL) ---
elif menu == "2. Gestão de Funcionários":
    st.header("👥 Cadastro de Colaboradores")
    st.info("💡 Use o botão '+' para adicionar. Selecione a linha e aperte 'Del' para excluir. Edite clicando nas células.")
    
    df_func = pd.DataFrame(st.session_state.funcionarios)
    
    # Grid Dinâmico (num_rows="dynamic")
    edited_func = st.data_editor(
        df_func,
        column_config={
            "ID": st.column_config.NumberColumn(disabled=True), # ID automático não mexe
            "Cargo": st.column_config.SelectboxColumn(options=list(st.session_state.config_multiplos['Cargo'].unique()), required=True),
            "Salario": st.column_config.NumberColumn(label="Salário", format="%.2f", min_value=0.0, step=100.0, required=True),
            "Tempo_Casa_Meses": st.column_config.NumberColumn(label="Meses", min_value=1, max_value=12, step=1, required=True),
            "Nome": st.column_config.TextColumn(required=True)
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )
    
    # Atualiza Session State
    # Tratamento para gerar IDs automáticos nos novos registros
    if len(edited_func) > 0:
        lista_final = edited_func.to_dict('records')
        for i, f in enumerate(lista_final):
            if pd.isna(f['ID']): # Se ID for nulo (novo registro)
                f['ID'] = i + 1  # Dá um ID sequencial
        st.session_state.funcionarios = lista_final
    else:
        st.session_state.funcionarios = []

# --- ABA 3: SIMULAÇÃO ---
elif menu == "3. Simulação e Pagamento":
    st.header("💰 Simulação de Pagamento")
    
    if 'nota_corporativa_final' not in st.session_state:
        st.warning("Calcule os Indicadores primeiro.")
    else:
        nota = st.session_state.nota_corporativa_final
        st.markdown(f"""
        <div class='formula-box'>
        <b>Bônus</b> = Salário x (Meses/12) x Múltiplo(Degrau) x Nota Indiv. x Fator Global
        <br>Score Corporativo Atual: {nota:.4f}
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        
        df = pd.DataFrame(st.session_state.funcionarios)
        if not df.empty:
            if "Performance_Individual" not in df.columns: df["Performance_Individual"] = 1.0
            
            edited_df = st.data_editor(
                df,
                column_config={
                    "ID": st.column_config.NumberColumn(disabled=True),
                    "Nome": st.column_config.TextColumn(disabled=True),
                    "Cargo": st.column_config.TextColumn(disabled=True),
                    "Performance_Individual": st.column_config.NumberColumn("Nota Indiv.", format="%.2f", step=0.05),
                    "Salario": st.column_config.NumberColumn(format="R$ %.2f", disabled=True)
                }, hide_index=True, use_container_width=True
            )
            
            if st.button("🚀 Calcular Bônus"):
                res = []
                tot = 0
                fat = buscar_valor_degrau(nota, st.session_state.config_fator)
                
                for i, row in edited_df.iterrows():
                    mult = buscar_valor_degrau(nota, st.session_state.config_multiplos, "Cargo", row['Cargo'])
                    t = row['Tempo_Casa_Meses']/12
                    ind = row['Performance_Individual']
                    bonus = row['Salario'] * t * mult * ind * fat
                    
                    res.append({
                        "Nome": row['Nome'], "Cargo": row['Cargo'], 
                        "Salário": formatar_br(row['Salario']),
                        "Múltiplo": mult, "Nota Indiv.": ind, "Fator": fat, 
                        "Bônus": formatar_br(bonus)
                    })
                    tot += bonus
                
                st.metric("Total Folha", f"R$ {formatar_br(tot)}")
                
                # Tabela Final formatada
                st.dataframe(pd.DataFrame(res).style.format({
                    "Múltiplo": "{:.2f}x", "Nota Indiv.": "{:.0%}", "Fator": "{:.2f}"
                }), use_container_width=True)
        else: st.warning("Sem funcionários cadastrados.")
