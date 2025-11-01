import folium
from folium.plugins import HeatMap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    all_cvli_df = pd.read_csv("./data/CVLI_2022.csv")
    all_censo_df = pd.read_csv("./data/censo.csv")
    all_municipios_df = pd.read_csv("./data/municipios.csv")

    # print(all_cvli_df.head())
    # print(all_censo_df.head())
    # print(all_municipios_df.head())
    # print(all_censo_df.info(), end="\n\n")
    # print(all_cvli_df.info(), end="\n\n")
    # print(all_municipios_df.info(), end="\n\n")

    censo_df = all_censo_df.drop(
        columns=[
        "Código [-]",
        "Gentílico [-]",
        "Prefeito [2025]",
        "Área Territorial - km² [2024]",
        "Densidade demográfica - hab/km² [2022]",
        "População estimada - pessoas [2025]",
        "Escolarização 6 a 14 anos % [2022]",
        "IDHM Índice de desenvolvimento humano municipal [2010]",
        "Mortalidade infantil - óbitos por mil nascidos vivos [2023]",
        "Total de receitas brutas realizadas - R$ [2024]",
        "Total de despesas brutas empenhadas - R$ [2024]",
        "PIB per capita - R$ [2021]"
    ])

    cvli_df = all_cvli_df.drop(
        columns=[
            "AIS",
            "Natureza",
            "Data",
            "Hora",
            "Dia da Semana",
            "Meio Empregado",
            "Gênero",
            "Idade da Vítima",
            "Escolaridade da Vítima",
            "Raça da Vítima"
        ]
    )
    
    municipios_df = all_municipios_df[all_municipios_df["codigo_uf"] == 23]
    # print(municipios_df.info(), end="\n\n")
    
    municipios_df = municipios_df.drop(
            columns=[
                "codigo_ibge",
                "capital",
                "codigo_uf",
                "siafi_id",
                "ddd",
                "fuso_horario",
            ]
    )

    # print(censo_df.info(), end="\n\n")
    # print(cvli_df.info(), end="\n\n")
    # print(municipios_df.info(), end="\n\n")

    censo_df = censo_df.rename(columns={"Município [-]": "municipio", "População no último censo - pessoas [2022]": "censo"})
    cvli_df = cvli_df.rename(columns={"Município": "municipio"})
    municipios_df = municipios_df.rename(columns={"nome": "municipio"})

    # print(censo_df.info(), end="\n\n")
    # print(cvli_df.info(), end="\n\n")
    # print(municipios_df.info(), end="\n\n")

    municipios_df["municipio"] = municipios_df["municipio"].replace("Ererê", "Ereré")
    # print(municipios_df.info())

    censo_municipios_df = pd.merge(municipios_df, censo_df, on="municipio", how="outer")
    # print(censo_municipios_df.info())

    # print(cvli_df.value_counts())
    quant_crimes_df = cvli_df['municipio'].value_counts().reset_index()
    # print(quant_crimes_df.info())
    
    quant_crimes_df = quant_crimes_df.rename(columns={"count": "crimes"})

    df = pd.merge(quant_crimes_df, censo_municipios_df, on="municipio", how="outer")
    # print(df.info())

    # print(df.loc[df["crimes"].isnull()])
    df["crimes"] = df["crimes"].fillna(0)
    print(df.info())

    print(df.head())

    mapa = folium.Map(location=[-5.5, -39.5], zoom_start=6)
    heat_data = [[row['latitude'], row['longitude'], row['crimes']] for index, row in df.iterrows()]
    HeatMap(heat_data, radius=15).add_to(mapa)
    mapa.save("mapas/mapa_calor_ceara.html")

    df_ranking = df.sort_values(by="crimes", ascending=False)

    top_n = 10
    df_top = df_ranking.head(top_n)

    plt.figure(figsize=(12, 8))

    sns.barplot(
        x="crimes",
        y="municipio",
        data=df_top,
        palette="Reds_r"
    )

    plt.title(f"Top {top_n} municípios com mais crimes no Ceará", fontsize=16)
    plt.xlabel("Número de Crimes")
    plt.ylabel("Município")

    for index, value in enumerate(df_top["crimes"]):
        plt.text(value + 0.5, index, str(int(value)), va='center')

    plt.tight_layout()
    plt.savefig("graficos/municipios_mais_crimes.png")


if __name__ == "__main__":
    main()