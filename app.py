import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador Bônus V3 | Controladoria", layout="wide")

# --- CSS PARA FORMATAÇÃO E LAYOUT ---
st.markdown("""
<style>
    .big-font {font-size: 18px !important; font-weight: bold; color: #333;}
    .stDataFrame {border: 1px solid #ddd; border-radius: 5px;}
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #1f77b4;}
</style>
""", unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
def check_password():
    if st.secrets.get("PASSWORD") is None: return True
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False):
        return True
    st.text_input("🔒 Senha:", type="password", on_change=password_entered, key="password")
    return False

if not check_password(): st.stop()

# --- INICIALIZAÇÃO DE DADOS (SESSION STATE) ---
if 'config_multiplos' not in st.session_state:
    data_mult = {
        "Cargo": ["Estagiário", "Operacional", "Tático", "Estratégico"],
        "Mínimo (x)": [0.6, 0.6, 1.0, 2.0],
        "Parcial (x)": [0.8, 0.8, 3.0, 4.0],
        "Meta (x)": [1.0, 1.0, 5.0, 8.0],
        "Superado (x)": [1.2, 1.2, 6.0, 9.0]
    }
    st.session_state.config_multiplos = pd.DataFrame(data_mult)

if 'config_fator' not in st.session_state:
    data_fator = {
        "Parâmetro": ["Fator Default"],
        "Mínimo": [1.0], "Parcial": [1.0], "Meta": [1.0], "Superado": [1.0]
    }
    st.session_state.config_fator = pd.DataFrame(data_fator)

if 'config_faixas' not in st.session_state:
    data_faixas = {
        "Nível": ["Mínimo", "Parcial", "Meta", "Superado"],
        "Gatilho (%)": [0.90, 0.95, 1.00, 1.10]
    }
    st.session_state.config_faixas = pd.DataFrame(data_faixas)

if 'metas_corp' not in st.session_state:
    st.session_state.metas_corp = [
        {"Indicador": "Receitas", "Peso": 80, "Meta ($)": 40735845.0, "Realizado ($)": 38700644.0},
        {"Indicador": "Fluxo Caixa", "Peso": 20, "Meta ($)": 16922142.0, "Realizado ($)": 18154955.0}
    ]

if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = [
        {"ID": 1, "Nome": "João Silva", "Cargo": "Tático", "Salario": 12000.0, "Tempo_Casa": 12, 
         "Metas": [{"Descricao": "Meta Geral", "Peso": 100, "Meta": 100.0, "Realizado": 95.0}]}
    ]

# --- FUNÇÃO DE INTERPOLAÇÃO UNIVERSAL ---
def calcular_interpolacao(realizado_pct, faixas_df, multiplos_row=None):
    min_g = faixas_df.loc[faixas_df['Nível']=='Mínimo', 'Gatilho (%)'].values[0]
    par_g = faixas_df.loc[faixas_df['Nível']=='Parcial', 'Gatilho (%)'].values[0]
    meta_g = faixas_df.loc[faixas_df['Nível']=='Meta', 'Gatilho (%)'].values[0]
    super_g = faixas_df.loc[faixas_df['Nível']=='Superado', 'Gatilho (%)'].values[0]
    
    x_points = [min_g, par_g, meta_g, super_g]
    
    if multiplos_row is not None:
        # Usa colunas específicas se for DataFrame de Múltiplos
        if 'Mínimo (x)' in multiplos_row:
            y_points = [multiplos_row['Mínimo (x)'], multiplos_row['Parcial (x)'], multiplos_row['Meta (x)'], multiplos_row['Superado (x)']]
        else: # Fallback para Fator
            y_points = [multiplos_row['Mínimo'], multiplos_row['Parcial'], multiplos_row['Meta'], multiplos_row['Superado']]
    else:
        y_points = [0.6, 0.8, 1.0, 1.2] # Padrão de Nota

    if realizado_pct < min_g: return 0.0
    return np.interp(realizado_pct, x_points, y_points)

# --- MENU ---
st.sidebar.title("Simulador V3")
menu = st.sidebar.radio("Navegação", ["1. Configurações Gerais", "2. Painel Corporativo", "3. Gestão Funcionários", "4. Simulação/Pagamento"])

# --- ABA 1: CONFIGURAÇÕES ---
if menu == "1. Configurações Gerais":
    st.header("⚙️ Configurações Gerais")
    
    st.subheader("1. Múltiplos Salariais por Cargo")
    edited_mult = st.data_editor(
        st.session_state.config_multiplos,
        column_config={
            "Mínimo (x)": st.column_config.NumberColumn(format="%.1f"),
            "Parcial (x)": st.column_config.NumberColumn(format="%.1f"),
            "Meta (x)": st.column_config.NumberColumn(format="%.1f"),
            "Superado (x)": st.column_config.NumberColumn(format="%.1f"),
        },
        use_container_width=True
    )
    st.session_state.config_multiplos = edited_mult
    
    st.subheader("2. Fator de Ajuste (Default)")
    edited_fator = st.data_editor(
        st.session_state.config_fator,
        column_config={
            "Mínimo": st.column_config.NumberColumn(format="%.2f"),
            "Parcial": st.column_config.NumberColumn(format="%.2f"),
            "Meta": st.column_config.NumberColumn(format="%.2f"),
            "Superado": st.column_config.NumberColumn(format="%.2f"),
        },
        use_container_width=True
    )
    st.session_state.config_fator = edited_fator
    
    st.subheader("3. Faixas de Atingimento (Gatilhos)")
    edited_faixas = st.data_editor(
        st.session_state.config_faixas,
        column_config={
            "Gatilho (%)": st.column_config.NumberColumn(format="%.2f %%", min_value=0.0, max_value=2.0)
        },
        use_container_width=True
    )
    st.session_state.config_faixas = edited_faixas

# --- ABA 2: PAINEL CORPORATIVO ---
elif menu == "2. Painel Corporativo":
    st.header("🏢 Painel de Metas Corporativas")
    
    df_metas_corp = pd.DataFrame(st.session_state.metas_corp)
    
    edited_corp = st.data_editor(
        df_metas_corp, 
        column_config={
            "Peso": st.column_config.NumberColumn(format="%d %%"),
            "Meta ($)": st.column_config.NumberColumn(format="$ %.2f"),
            "Realizado ($)": st.column_config.NumberColumn(format="$ %.2f")
        },
        num_rows="dynamic", 
        use_container_width=True
    )
    st.session_state.metas_corp = edited_corp.to_dict('records')
    
    # Cálculo
    total_score = 0
    st.divider()
    st.subheader("Resultado Apurado")
    
    # Grid de resultados
    res_data = []
    for item in st.session_state.metas_corp:
        atg = item['Realizado ($)'] / item['Meta ($)'] if item['Meta ($)'] > 0 else 0
        nota = calcular_interpolacao(atg, st.session_state.config_faixas, multiplos_row=None)
        score = nota * (item['Peso']/100)
        total_score += score
        res_data.append([item['Indicador'], atg, nota, score])
        
    df_res = pd.DataFrame(res_data, columns=["Indicador", "% Ating.", "Nota Interp.", "Score Ponderado"])
    st.dataframe(df_res.style.format({
        "% Ating.": "{:.1%}", "Nota Interp.": "{:.2f}", "Score Ponderado": "{:.4f}"
    }), use_container_width=True)
    
    st.metric("Nota Corporativa Final", f"{total_score:.4f}")
    st.session_state.nota_corporativa_final = total_score

# --- ABA 3: GESTÃO FUNCIONÁRIOS ---
elif menu == "3. Gestão Funcionários":
    st.header("👥 Cadastro e Metas Individuais")
    
    # GRID PRINCIPAL DE CADASTRO
    st.markdown("### 1. Base de Colaboradores")
    df_funcs = pd.DataFrame(st.session_state.funcionarios)
    
    # Vamos usar um editor mas precisamos tomar cuidado com a coluna 'Metas' que é complexa (lista)
    # Então editamos apenas as colunas básicas aqui
    cols_basicas = ["ID", "Nome", "Cargo", "Salario", "Tempo_Casa"]
    
    edited_base = st.data_editor(
        df_funcs[cols_basicas],
        column_config={
            "Salario": st.column_config.NumberColumn(format="$ %.2f"),
            "Cargo": st.column_config.SelectboxColumn(options=list(st.session_state.config_multiplos['Cargo']))
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_funcionarios"
    )
    
    # Sincronizar edições básicas (preservando as Metas antigas)
    if len(edited_base) != len(st.session_state.funcionarios):
        # Se adicionou linha nova
        novos_funcs = []
        for index, row in edited_base.iterrows():
            # Tenta achar o registro antigo para manter as metas
            old_record = next((f for f in st.session_state.funcionarios if f['ID'] == row['ID']), None)
            if old_record:
                metas = old_record['Metas']
            else:
                metas = [{"Descricao": "Meta Padrão", "Peso": 100, "Meta": 100.0, "Realizado": 0.0}] # Default para novos
            
            novos_funcs.append({
                "ID": row['ID'], "Nome": row['Nome'], "Cargo": row['Cargo'], 
                "Salario": row['Salario'], "Tempo_Casa": row['Tempo_Casa'], "Metas": metas
            })
        st.session_state.funcionarios = novos_funcs

    st.divider()
    
    # GESTÃO DE METAS INDIVIDUAIS
    st.markdown("### 2. Detalhar Metas do Colaborador")
    
    # Selectbox para escolher quem editar as metas
    opcoes = [f"{f['ID']} - {f['Nome']}" for f in st.session_state.funcionarios]
    escolha = st.selectbox("Selecione o Colaborador para editar metas:", options=opcoes)
    
    if escolha:
        id_sel = int(escolha.split(" - ")[0])
        # Encontrar índice
        idx = next(i for i, f in enumerate(st.session_state.funcionarios) if f['ID'] == id_sel)
        
        # Editor de Metas
        df_m = pd.DataFrame(st.session_state.funcionarios[idx]['Metas'])
        edited_metas = st.data_editor(
            df_m,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Peso": st.column_config.NumberColumn(format="%d %%", max_value=100),
                "Realizado": st.column_config.NumberColumn(help="Valor Absoluto ou % (ex: 95 para 95%)")
            },
            key=f"metas_{id_sel}"
        )
        # Salvar metas
        st.session_state.funcionarios[idx]['Metas'] = edited_metas.to_dict('records')

# --- ABA 4: PAGAMENTO ---
elif menu == "4. Simulação/Pagamento":
    st.header("💰 Folha de Pagamento")
    
    if 'nota_corporativa_final' not in st.session_state:
        st.error("⚠️ Calcule o Resultado Corporativo primeiro.")
        st.stop()
        
    nota_corp = st.session_state.nota_corporativa_final
    
    st.markdown(f"""
    <div class='metric-card'>
        <span class='big-font'>Nota Corporativa Atual: {nota_corp:.4f}</span>
    </div>
    <br>
    """, unsafe_allow_html=True)

    if st.button("Calcular Folha"):
        dados_pagamento = []
        
        for f in st.session_state.funcionarios:
            # 1. Nota Individual
            nota_ind = 0
            for m in f['Metas']:
                atg = m['Realizado'] / m['Meta'] if m['Meta'] > 0 else 0
                nota_item = calcular_interpolacao(atg, st.session_state.config_faixas)
                nota_ind += nota_item * (m['Peso']/100)
                
            # 2. Múltiplo Salarial (Do Cargo + Nota Corp)
            regra_mult = st.session_state.config_multiplos.loc[st.session_state.config_multiplos['Cargo'] == f['Cargo']].iloc[0]
            mult_final = calcular_interpolacao(nota_corp, st.session_state.config_faixas, multiplos_row=regra_mult)
            
            # 3. Fator Default (Opcional - usando linha 0 da config)
            regra_fator = st.session_state.config_fator.iloc[0]
            fator_extra = calcular_interpolacao(nota_corp, st.session_state.config_faixas, multiplos_row=regra_fator)
            
            # 4. Cálculo
            bonus = f['Salario'] * (f['Tempo_Casa']/12) * mult_final * nota_ind * fator_extra
            
            dados_pagamento.append({
                "Colaborador": f['Nome'],
                "Cargo": f['Cargo'],
                "Salário Base": f['Salario'],
                "Múltiplo (Corp)": mult_final,
                "Nota Indiv.": nota_ind,
                "Fator Ajuste": fator_extra,
                "Bônus Final": bonus
            })
            
        df_pag = pd.DataFrame(dados_pagamento)
        st.dataframe(df_pag.style.format({
            "Salário Base": "R$ {:,.2f}",
            "Múltiplo (Corp)": "{:.2f} sal.",
            "Nota Indiv.": "{:.2%}",
            "Fator Ajuste": "{:.2f}",
            "Bônus Final": "R$ {:,.2f}"
        }), use_container_width=True)
        
        total = df_pag['Bônus Final'].sum()
        st.metric("💰 Total da Folha", f"R$ {total:,.2f}")
