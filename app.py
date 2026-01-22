import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador Bônus | Controladoria", layout="wide")

# --- CSS CUSTOMIZADO ---
st.markdown("""
<style>
    .big-font {font-size: 18px !important; font-weight: bold; color: #333;}
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #1f77b4;}
    .stDataFrame {border: 1px solid #ddd; border-radius: 5px;}
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

    st.text_input("🔒 Senha de Acesso:", type="password", on_change=password_entered, key="password")
    return False

if not check_password():
    st.stop()

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
    # NOVO: Tabela de Fator
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
    # Estrutura baseada na V2 que funcionava
    st.session_state.funcionarios = [
        {
            "ID": 1, "Nome": "João Silva", "Cargo": "Tático", "Salario": 12000.0, "Tempo_Casa": 12,
            "Metas": [
                {"Descricao": "Dashboard Resultados", "Peso": 25, "Meta": 100.0, "Realizado": 50.0},
                {"Descricao": "Processos Financeiros", "Peso": 25, "Meta": 100.0, "Realizado": 95.0},
                {"Descricao": "Migração Netsuite", "Peso": 50, "Meta": 100.0, "Realizado": 95.0}
            ]
        }
    ]

# --- FUNÇÃO DE CÁLCULO (UNIVERSAL) ---
def calcular_interpolacao(realizado_pct, faixas_df, multiplos_row=None):
    # Extrair gatilhos
    min_g = faixas_df.loc[faixas_df['Nível']=='Mínimo', 'Gatilho (%)'].values[0]
    par_g = faixas_df.loc[faixas_df['Nível']=='Parcial', 'Gatilho (%)'].values[0]
    meta_g = faixas_df.loc[faixas_df['Nível']=='Meta', 'Gatilho (%)'].values[0]
    super_g = faixas_df.loc[faixas_df['Nível']=='Superado', 'Gatilho (%)'].values[0]
    
    x_points = [min_g, par_g, meta_g, super_g]
    
    # Definir Eixo Y (Múltiplos ou Fatores ou Notas Puras)
    if multiplos_row is not None:
        if 'Mínimo (x)' in multiplos_row:
            y_points = [multiplos_row['Mínimo (x)'], multiplos_row['Parcial (x)'], multiplos_row['Meta (x)'], multiplos_row['Superado (x)']]
        else:
            # Caso seja a tabela de Fator (que não tem o (x) no nome da coluna)
            y_points = [multiplos_row['Mínimo'], multiplos_row['Parcial'], multiplos_row['Meta'], multiplos_row['Superado']]
    else:
        # Padrão de Nota de Desempenho (0.6 a 1.2 conforme seu pedido anterior)
        y_points = [0.6, 0.8, 1.0, 1.2] 

    if realizado_pct < min_g:
        return 0.0
    
    return np.interp(realizado_pct, x_points, y_points)

# --- MENU LATERAL ---
st.sidebar.title("Simulador Bônus")
menu = st.sidebar.radio("Ir para:", ["1. Configurações Gerais", "2. Painel Corporativo", "3. Gestão Funcionários", "4. Simulação/Pagamento"])

# --- ABA 1: CONFIGURAÇÕES ---
if menu == "1. Configurações Gerais":
    st.header("⚙️ Configurações Gerais")
    
    st.subheader("1. Múltiplos Salariais por Cargo")
    # Formatação com 1 casa decimal conforme pedido
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

    st.subheader("2. Faixas de Atingimento (Gatilhos)")
    # Movido para baixo conforme pedido
    edited_faixas = st.data_editor(
        st.session_state.config_faixas,
        column_config={
            "Gatilho (%)": st.column_config.NumberColumn(format="%.2f", min_value=0.0, max_value=2.0)
        },
        use_container_width=True
    )
    st.session_state.config_faixas = edited_faixas
    
    st.subheader("3. Fator Default")
    # Nova tabela solicitada
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

# --- ABA 2: PAINEL CORPORATIVO ---
elif menu == "2. Painel Corporativo":
    st.header("🏢 Metas Globais")
    
    df_metas_corp = pd.DataFrame(st.session_state.metas_corp)
    
    # Grid editável com formatação R$
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
    
    st.divider()
    st.subheader("Apuração do Resultado")
    
    total_score = 0
    detalhes = []
    
    for item in st.session_state.metas_corp:
        meta = item['Meta ($)']
        real = item['Realizado ($)']
        peso = item['Peso']
        
        atingimento = real / meta if meta > 0 else 0
        
        # Interpolação para nota (0.6 a 1.2)
        nota_interpolada = calcular_interpolacao(atingimento, st.session_state.config_faixas)
        score_pond = nota_interpolada * (peso/100)
        total_score += score_pond
        
        detalhes.append({
            "Indicador": item['Indicador'],
            "Atingimento Real": atingimento,
            "Nota (0.6-1.2)": nota_interpolada,
            "Score Ponderado": score_pond
        })
        
    df_detalhe = pd.DataFrame(detalhes)
    st.dataframe(df_detalhe.style.format({
        "Atingimento Real": "{:.1%}",
        "Nota (0.6-1.2)": "{:.2f}",
        "Score Ponderado": "{:.4f}"
    }), use_container_width=True)
    
    st.metric("Nota Corporativa Final", f"{total_score:.4f}")
    st.session_state.nota_corporativa_final = total_score

# --- ABA 3: GESTÃO DE FUNCIONÁRIOS ---
elif menu == "3. Gestão Funcionários":
    st.header("👥 Gestão de Colaboradores")
    
    # 1. GRID PRINCIPAL (CADASTRO BÁSICO)
    st.info("Passo 1: Cadastre ou edite os dados básicos dos colaboradores aqui.")
    
    # Prepara DataFrame apenas com dados planos (sem a lista de metas)
    lista_plana = []
    for f in st.session_state.funcionarios:
        lista_plana.append({
            "ID": f['ID'], 
            "Nome": f['Nome'], 
            "Cargo": f['Cargo'], 
            "Salario": f['Salario'], 
            "Tempo_Casa": f['Tempo_Casa']
        })
    df_plano = pd.DataFrame(lista_plana)
    
    # Editor do Grid Principal
    edited_df_plano = st.data_editor(
        df_plano,
        num_rows="dynamic",
        column_config={
            "Salario": st.column_config.NumberColumn(format="$ %.2f"),
            "Cargo": st.column_config.SelectboxColumn(options=list(st.session_state.config_multiplos['Cargo']))
        },
        use_container_width=True,
        key="editor_funcionarios_v3"
    )
    
    # SINCRONIZAÇÃO COMPLEXA (Grid -> Session State)
    # Precisamos detectar novos, edits e deletes
    
    # Criar dicionário temporário para reconstruir o state
    novos_dados_state = []
    
    for index, row in edited_df_plano.iterrows():
        # Busca se esse ID já existia para preservar as metas
        usuario_antigo = next((u for u in st.session_state.funcionarios if u['ID'] == row['ID']), None)
        
        if usuario_antigo:
            metas_preservadas = usuario_antigo['Metas']
        else:
            # Se for novo (ID novo ou nulo), cria meta padrão
            metas_preservadas = [{"Descricao": "Nova Meta", "Peso": 100, "Meta": 100.0, "Realizado": 0.0}]
            
        novos_dados_state.append({
            "ID": row['ID'],
            "Nome": row['Nome'],
            "Cargo": row['Cargo'],
            "Salario": row['Salario'],
            "Tempo_Casa": row['Tempo_Casa'],
            "Metas": metas_preservadas
        })
    
    # Atualiza o banco de dados principal
    st.session_state.funcionarios = novos_dados_state
    
    st.divider()
    
    # 2. GESTÃO DE METAS (DETALHE)
    st.info("Passo 2: Selecione um colaborador acima para editar suas metas específicas.")
    
    if len(st.session_state.funcionarios) > 0:
        opcoes = [f"{f['ID']} - {f['Nome']}" for f in st.session_state.funcionarios]
        selection = st.selectbox("Editar Metas de:", options=opcoes)
        
        if selection:
            id_sel = int(selection.split(" - ")[0])
            # Achar indice no array
            idx = next(i for i, f in enumerate(st.session_state.funcionarios) if f['ID'] == id_sel)
            func_atual = st.session_state.funcionarios[idx]
            
            st.subheader(f"Metas de: {func_atual['Nome']}")
            
            # Editor de Metas
            df_metas = pd.DataFrame(func_atual['Metas'])
            edited_metas = st.data_editor(
                df_metas,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Peso": st.column_config.NumberColumn(format="%d %%"),
                    "Realizado": st.column_config.NumberColumn(help="Valor realizado")
                },
                key=f"metas_editor_{id_sel}"
            )
            
            # Salvar Metas
            st.session_state.funcionarios[idx]['Metas'] = edited_metas.to_dict('records')
            
            # Preview Nota
            total_n = 0
            for m in st.session_state.funcionarios[idx]['Metas']:
                 atg = m['Realizado']/m['Meta'] if m['Meta']>0 else 0
                 n = calcular_interpolacao(atg, st.session_state.config_faixas)
                 total_n += n * (m['Peso']/100)
            st.write(f"**Nota Individual Calculada:** {total_n:.2f}")

# --- ABA 4: PAGAMENTO ---
elif menu == "4. Simulação/Pagamento":
    st.header("💰 Folha de Pagamento")
    
    if 'nota_corporativa_final' not in st.session_state:
        st.error("⚠️ Necessário calcular o Painel Corporativo primeiro.")
    else:
        nota_corp = st.session_state.nota_corporativa_final
        
        if st.button("🚀 Calcular Folha de Bônus"):
            folha = []
            
            for f in st.session_state.funcionarios:
                # 1. Nota Individual
                nota_indiv = 0
                for m in f['Metas']:
                    atg = m['Realizado'] / m['Meta'] if m['Meta'] > 0 else 0
                    nt = calcular_interpolacao(atg, st.session_state.config_faixas)
                    nota_indiv += nt * (m['Peso']/100)
                
                # 2. Múltiplo Cargo
                regra_m = st.session_state.config_multiplos.loc[st.session_state.config_multiplos['Cargo'] == f['Cargo']].iloc[0]
                mult_final = calcular_interpolacao(nota_corp, st.session_state.config_faixas, multiplos_row=regra_m)
                
                # 3. Fator Default
                regra_f = st.session_state.config_fator.iloc[0]
                fator_final = calcular_interpolacao(nota_corp, st.session_state.config_faixas, multiplos_row=regra_f)
                
                # 4. Cálculo
                bonus = f['Salario'] * (f['Tempo_Casa']/12) * mult_final * nota_indiv * fator_final
                
                folha.append({
                    "Nome": f['Nome'],
                    "Cargo": f['Cargo'],
                    "Salário": f['Salario'],
                    "Nota Corp": nota_corp,
                    "Múltiplo": mult_final,
                    "Nota Indiv": nota_indiv,
                    "Fator": fator_final,
                    "Bônus Final": bonus
                })
            
            df_folha = pd.DataFrame(folha)
            
            # Formatação ajustada para não truncar e ficar legível
            st.dataframe(df_folha.style.format({
                "Salário": "R$ {:,.2f}",
                "Nota Corp": "{:.2f}",
                "Múltiplo": "{:.2f} sal.",
                "Nota Indiv": "{:.2f}",
                "Fator": "{:.2f}",
                "Bônus Final": "R$ {:,.2f}"
            }), use_container_width=True)
            
            total = df_folha['Bônus Final'].sum()
            st.metric("Total da Folha", f"R$ {total:,.2f}")
