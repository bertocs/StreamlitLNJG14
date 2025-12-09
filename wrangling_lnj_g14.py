import pandas as pd

# Ruta EXACTA de tu archivo (la que me has dado)
EXCEL_PATH = r"C:\Users\josea\Desktop\ANALISIS\proyectos_ds\lnj_g4_2024_25\datalapreferente\matriz_lnj_g14.xlsx"

# Nombre de la hoja donde está la matriz
# Si tu hoja se llama distinto, cámbialo aquí (por ejemplo "matriz")
SHEET_NAME_MATRIZ = "Sheet1"
SHEET_NAME_STATS = "estadisticas"


def cargar_matriz():
    """
    Carga la matriz desde el Excel.
    Se asume:
      - La primera columna del Excel es el índice (nombres de equipos).
      - Las columnas tienen los mismos nombres de equipos.
    """
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME_MATRIZ, index_col=0)
    return df


def extraer_goles(resultado):
    """Devuelve (g_local, g_visitante) a partir de un string '2-1'."""
    return map(int, resultado.split("-"))


def contar_partidos(df):
    equipos = df.index.tolist()

    partidos_local = []
    partidos_visitante = []

    for equipo in equipos:
        # Partidos como LOCAL: fila del equipo
        resultados_local = df.loc[equipo]
        partidos_local.append(resultados_local.notna().sum())

        # Partidos como VISITANTE: columna del equipo
        resultados_visitante = df[equipo]
        partidos_visitante.append(resultados_visitante.notna().sum())

    df_stats = pd.DataFrame({
        "equipo": equipos,
        "partidos_local": partidos_local,
        "partidos_visitante": partidos_visitante
    })

    df_stats["partidos_totales"] = df_stats["partidos_local"] + df_stats["partidos_visitante"]
    return df_stats


def contar_resultados(df, df_stats):
    equipos = df.index.tolist()

    victorias_local = []
    empates_local = []
    derrotas_local = []
    victorias_visitante = []
    empates_visitante = []
    derrotas_visitante = []

    for equipo in equipos:
        v_local = e_local = d_local = 0
        v_vis = e_vis = d_vis = 0

        # Como LOCAL (fila)
        for resultado in df.loc[equipo]:
            if isinstance(resultado, str) and "-" in resultado:
                g_local, g_visit = extraer_goles(resultado)
                if g_local > g_visit:
                    v_local += 1
                elif g_local == g_visit:
                    e_local += 1
                else:
                    d_local += 1

        # Como VISITANTE (columna)
        for resultado in df[equipo]:
            if isinstance(resultado, str) and "-" in resultado:
                g_local, g_visit = extraer_goles(resultado)
                if g_visit > g_local:
                    v_vis += 1
                elif g_visit == g_local:
                    e_vis += 1
                else:
                    d_vis += 1

        victorias_local.append(v_local)
        empates_local.append(e_local)
        derrotas_local.append(d_local)

        victorias_visitante.append(v_vis)
        empates_visitante.append(e_vis)
        derrotas_visitante.append(d_vis)

    df_stats["victorias_local"] = victorias_local
    df_stats["victorias_visitante"] = victorias_visitante
    df_stats["empates_local"] = empates_local
    df_stats["empates_visitante"] = empates_visitante
    df_stats["derrotas_local"] = derrotas_local
    df_stats["derrotas_visitante"] = derrotas_visitante

    return df_stats


def calcular_puntos(df_stats):
    df_stats["puntos_local"] = df_stats["victorias_local"] * 3 + df_stats["empates_local"]
    df_stats["puntos_visitante"] = df_stats["victorias_visitante"] * 3 + df_stats["empates_visitante"]
    df_stats["puntos_totales"] = df_stats["puntos_local"] + df_stats["puntos_visitante"]
    return df_stats


def calcular_goles(df, df_stats):
    equipos = df.index.tolist()

    goles_local = []
    goles_recibidos_local = []
    goles_visitante = []
    goles_recibidos_visitante = []

    # Goles como LOCAL (filas)
    for equipo in equipos:
        gf = gc = 0
        for resultado in df.loc[equipo]:
            if isinstance(resultado, str) and "-" in resultado:
                g_local, g_visitante = map(int, resultado.split("-"))
                gf += g_local
                gc += g_visitante
        goles_local.append(gf)
        goles_recibidos_local.append(gc)

    # Goles como VISITANTE (columnas)
    for equipo in equipos:
        gf = gc = 0
        for resultado in df[equipo]:
            if isinstance(resultado, str) and "-" in resultado:
                g_local, g_visitante = map(int, resultado.split("-"))
                gf += g_visitante
                gc += g_local
        goles_visitante.append(gf)
        goles_recibidos_visitante.append(gc)

    df_stats["goles_local"] = goles_local
    df_stats["goles_visitante"] = goles_visitante
    df_stats["goles_total"] = df_stats["goles_local"] + df_stats["goles_visitante"]

    df_stats["goles_recibidos_local"] = goles_recibidos_local
    df_stats["goles_recibidos_visitante"] = goles_recibidos_visitante
    df_stats["goles_recibidos_total"] = (
        df_stats["goles_recibidos_local"] + df_stats["goles_recibidos_visitante"]
    )

    df_stats["goles_por_partido_local"] = (
        df_stats["goles_local"] / df_stats["partidos_local"]
    ).round(2)

    df_stats["goles_por_partido_visitante"] = (
        df_stats["goles_visitante"] / df_stats["partidos_visitante"]
    ).round(2)

    df_stats["goles_por_partido_total"] = (
        df_stats["goles_total"] / df_stats["partidos_totales"]
    ).round(2)

    df_stats["goles_recibidos_por_partido_local"] = (
        df_stats["goles_recibidos_local"] / df_stats["partidos_local"]
    ).round(2)

    df_stats["goles_recibidos_por_partido_visitante"] = (
        df_stats["goles_recibidos_visitante"] / df_stats["partidos_visitante"]
    ).round(2)

    df_stats["goles_recibidos_por_partido_total"] = (
        df_stats["goles_recibidos_total"] / df_stats["partidos_totales"]
    ).round(2)

    df_stats["diferencia_goles"] = df_stats["goles_total"] - df_stats["goles_recibidos_total"]

    return df_stats


def escribir_hoja_estadisticas():
    df_matriz = cargar_matriz()

    df_stats = contar_partidos(df_matriz)
    df_stats = contar_resultados(df_matriz, df_stats)
    df_stats = calcular_puntos(df_stats)
    df_stats = calcular_goles(df_matriz, df_stats)

    # Añadir/actualizar hoja "estadisticas" en el MISMO Excel
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        # No tocamos la hoja de la matriz; solo escribimos/actualizamos "estadisticas"
        df_stats.to_excel(writer, sheet_name=SHEET_NAME_STATS, index=False)

    print("Hoja 'estadisticas' creada/actualizada en el archivo:")
    print(EXCEL_PATH)


def main():
    escribir_hoja_estadisticas()


if __name__ == "__main__":
    main()
