
import streamlit as st
import pandas as pd

st.title("📊 Simulador de Alíquota Efetiva - Simples Nacional (Anexo III)")

st.markdown("Preencha os dados para simular a alíquota efetiva do Simples Nacional.")

# Opção para marcar se a empresa está iniciando as atividades
empresa_iniciando = st.checkbox("Empresa está iniciando as atividades")

# Entradas principais
if empresa_iniciando:
    receita_bruta_inicial = 0.0
    st.write("Receita Bruta Inicial: R$ 0,00 (empresa em início de atividades)")
else:
    receita_bruta_inicial = st.number_input("Receita bruta acumulada dos últimos 12 meses (até o mês atual)", value=0.0, step=100.0, format="%.2f")

faturamento_mes_atual = st.number_input("Faturamento do mês atual", value=0.0, step=100.0, format="%.2f")

# Verificação de limite do Simples Nacional
if faturamento_mes_atual * 12 > 3600000:
    st.error("⚠️ O faturamento anual projetado excede o limite do Simples Nacional (R$ 3.600.000,00).")
else:
    if empresa_iniciando:
        # Anualizar o faturamento para cálculo da faixa
        receita_anualizada = faturamento_mes_atual * 12
        receita_bruta_inicial = receita_anualizada
    else:
        receita_anualizada = receita_bruta_inicial

    def faixa_simples(rbt12):
        if rbt12 <= 180_000:
            return 0.06, 0
        elif rbt12 <= 360_000:
            return 0.112, 9360
        elif rbt12 <= 720_000:
            return 0.135, 17640
        elif rbt12 <= 1_800_000:
            return 0.16, 35640
        elif rbt12 <= 3_600_000:
            return 0.21, 125640
        else:
            return 0.33, 648000

    projecao = []

    # Mês 0
    aliq_nom, ded = faixa_simples(receita_anualizada)
    aliq_eff = ((receita_anualizada * aliq_nom) - ded) / receita_anualizada
    imposto = faturamento_mes_atual * aliq_eff
    projecao.append({
        "Mês": "Mês 0 (Atual)",
        "Receita Bruta Base": receita_bruta_inicial,
        "Receita do Mês": faturamento_mes_atual,
        "Alíquota Efetiva (%)": aliq_eff * 100,
        "Imposto Estimado": imposto
    })

    # Próximos 12 meses
    acumulado = receita_bruta_inicial + faturamento_mes_atual
    for i in range(1, 13):
        receita_mes = faturamento_mes_atual
        aliq_nom, ded = faixa_simples(acumulado)
        aliq_eff = ((acumulado * aliq_nom) - ded) / acumulado
        imposto = receita_mes * aliq_eff
        projecao.append({
            "Mês": f"Mês {i}",
            "Receita Bruta Base": acumulado,
            "Receita do Mês": receita_mes,
            "Alíquota Efetiva (%)": aliq_eff * 100,
            "Imposto Estimado": imposto
        })
        acumulado += receita_mes

    df = pd.DataFrame(projecao)

    def moeda(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def pct(v): return f"{v:.4f}"

    df["Receita Bruta Base"] = df["Receita Bruta Base"].apply(moeda)
    df["Receita do Mês"] = df["Receita do Mês"].apply(moeda)
    df["Alíquota Efetiva (%)"] = df["Alíquota Efetiva (%)"].apply(pct)
    df["Imposto Estimado"] = df["Imposto Estimado"].apply(moeda)

    df.set_index("Mês", inplace=True)
    st.markdown("## 📈 Projeção Mês a Mês")
    st.table(df)
