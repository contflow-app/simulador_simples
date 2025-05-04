
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Tabela oficial Anexo III - Simples Nacional
tabela_simples = pd.DataFrame({
    "Faixa": [1, 2, 3, 4, 5, 6],
    "Limite": [180000, 360000, 720000, 1800000, 3600000, 4800000],
    "Aliquota": [0.06, 0.112, 0.135, 0.16, 0.21, 0.33],
    "Deducao": [0, 9360, 17640, 35640, 125640, 648000]
})

st.title("📊 Simulador de Alíquota Efetiva - Simples Nacional (Anexo III)")

st.markdown("### 1️⃣ Receita Bruta Acumulada Inicial (últimos 12 meses)")
receita_acumulada = st.number_input("Informe a Receita Bruta dos últimos 12 meses (R$):", min_value=0.0, step=100.0)

st.markdown("### 2️⃣ Receita do Mês Atual")
receita_mes_atual = st.number_input("Informe o faturamento do mês atual (R$):", min_value=0.0, step=100.0)

# Cálculo da alíquota efetiva com base apenas na receita acumulada
if receita_acumulada > 0:
    faixa = tabela_simples[tabela_simples["Limite"] >= receita_acumulada].iloc[0]
    aliquota_efetiva = ((receita_acumulada * faixa["Aliquota"]) - faixa["Deducao"]) / receita_acumulada
    imposto_aproximado = receita_mes_atual * aliquota_efetiva
else:
    faixa = {"Faixa": "-", "Aliquota": 0, "Deducao": 0}
    aliquota_efetiva = 0
    imposto_aproximado = 0

st.markdown("## 📌 Resultado do Mês Atual")
st.write(f"Receita Bruta Acumulada (sem incluir o mês atual): **R$ {receita_acumulada:,.2f}**")
st.write(f"Faixa: **{faixa['Faixa']}** | Alíquota Nominal: **{faixa['Aliquota'] * 100:.2f}%**")
st.write(f"Parcela a Deduzir: **R$ {faixa['Deducao']:,.2f}**")
st.success(f"Alíquota Efetiva Aplicável: **{aliquota_efetiva * 100:.2f}%**")
st.info(f"Imposto aproximado sobre R$ {receita_mes_atual:,.2f}: **R$ {imposto_aproximado:,.2f}**")

# Projeção opcional
st.markdown("### 3️⃣ Projeção dos Próximos 12 Meses (Opcional)")
faturamento_medio = st.number_input("Informe o faturamento médio mensal projetado (R$):", min_value=0.0, step=100.0)

if st.button("Gerar Projeção"):
    receitas = []
    projecao = []

    receita_base = receita_acumulada + receita_mes_atual
    receitas.append(receita_base)

    faixa_base = tabela_simples[tabela_simples["Limite"] >= receita_base].iloc[0]
    aliq_base = ((receita_base * faixa_base["Aliquota"]) - faixa_base["Deducao"]) / receita_base
    imposto_base = faturamento_medio * aliq_base
    projecao.append(("Mês 0", receita_acumulada, receita_mes_atual, aliq_base * 100, imposto_base))

    acumulado = receita_base
    for i in range(1, 13):
        acumulado += faturamento_medio
        faixa_proj = tabela_simples[tabela_simples["Limite"] >= acumulado].iloc[0]
        aliq_efetiva_proj = ((acumulado * faixa_proj["Aliquota"]) - faixa_proj["Deducao"]) / acumulado
        imposto_proj = faturamento_medio * aliq_efetiva_proj
        projecao.append((f"Mês {i}", acumulado - faturamento_medio, faturamento_medio, aliq_efetiva_proj * 100, imposto_proj))

    df_proj = pd.DataFrame(projecao, columns=[
        "Mês", 
        "Faturamento 12 Meses Anteriores", 
        "Faturamento do Mês", 
        "Alíquota Efetiva (%)", 
        "Imposto Estimado (R$)"
    ])

    df_proj["Faturamento 12 Meses Anteriores"] = df_proj["Faturamento 12 Meses Anteriores"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_proj["Faturamento do Mês"] = df_proj["Faturamento do Mês"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_proj["Imposto Estimado (R$)"] = df_proj["Imposto Estimado (R$)"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("## 📈 Projeção dos Próximos 12 Meses")
    st.dataframe(df_proj)

    fig, ax = plt.subplots()
    ax.plot(range(13), [float(row[3]) for row in projecao], marker='o')
    ax.set_xlabel("Mês")
    ax.set_ylabel("Alíquota Efetiva (%)")
    ax.set_title("Projeção da Alíquota Efetiva - 12 Meses")
    st.pyplot(fig)
