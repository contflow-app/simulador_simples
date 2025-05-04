
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
    receitas = [receita_acumulada + receita_mes_atual]
    projecao = []

    for i in range(12):
        novo_total = receitas[-1] + faturamento_medio
        faixa_proj = tabela_simples[tabela_simples["Limite"] >= novo_total].iloc[0]
        aliq_efetiva_proj = ((novo_total * faixa_proj["Aliquota"]) - faixa_proj["Deducao"]) / novo_total
        projecao.append((f"Mês {i+1}", novo_total, aliq_efetiva_proj * 100))
        receitas.append(novo_total)

    df_proj = pd.DataFrame(projecao, columns=["Mês", "Receita Bruta Acumulada", "Alíquota Efetiva (%)"])
    df_proj["Receita Bruta Acumulada"] = df_proj["Receita Bruta Acumulada"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown("## 📈 Projeção dos Próximos 12 Meses")
    st.dataframe(df_proj)

    fig, ax = plt.subplots()
    ax.plot(range(1, 13), [p[2] for p in projecao], marker='o')
    ax.set_xlabel("Mês")
    ax.set_ylabel("Alíquota Efetiva (%)")
    ax.set_title("Projeção da Alíquota Efetiva - 12 Meses")
    st.pyplot(fig)
