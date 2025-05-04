
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd

# ---------- AUTENTICAÇÃO ----------
users = {
    "raulmarsantos": {
        "name": "Raul Martins",
        "password": "123456"
    }
}

hashed_passwords = stauth.Hasher([u["password"] for u in users.values()]).generate()

credentials = {
    u: {"name": users[u]["name"], "password": hashed_passwords[i]}
    for i, u in enumerate(users)
}

authenticator = stauth.Authenticate(
    credentials,
    "simulador_app",
    "abcdef1234567890",
    cookie_expiry_days=1
)

nome_usuario, autenticado, nome = authenticator.login("Login", "main")

if autenticado:
    authenticator.logout("Sair", "sidebar")
    st.sidebar.success(f"Bem-vindo, {nome}!")

    st.title("📊 Simulador de Alíquota Efetiva - Simples Nacional (Anexo III)")

    st.markdown("Preencha a receita bruta acumulada e o faturamento mensal atual. Você pode usar um valor único de projeção ou informar mês a mês.")

    receita_bruta_inicial = st.number_input("Receita bruta acumulada dos últimos 12 meses (até o mês atual)", value=0.0, step=100.0, format="%.2f")
    faturamento_mes_atual = st.number_input("Faturamento do mês atual", value=0.0, step=100.0, format="%.2f")

    modo_real = st.checkbox("Quero inserir o faturamento real de cada mês")

    if modo_real:
        faturamentos = []
        col1, col2, col3 = st.columns(3)
        with col1:
            faturamentos.append(faturamento_mes_atual)
        for i in range(1, 13):
            with [col1, col2, col3][i % 3]:
                val = st.number_input(f"Faturamento Mês {i}", min_value=0.0, step=100.0, format="%.2f")
                faturamentos.append(val)
    else:
        faturamento_projetado = st.number_input("Faturamento projetado para os próximos meses", value=0.0, step=100.0, format="%.2f")
        faturamentos = [faturamento_mes_atual] + [faturamento_projetado] * 12

    if receita_bruta_inicial > 0 and all(f > 0 for f in faturamentos):
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
        acumulado = receita_bruta_inicial

        for i in range(13):
            receita_mes = faturamentos[i]
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

else:
    st.warning("Por favor, faça login para acessar o simulador.")
