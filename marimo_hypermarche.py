import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb

    # Create a DuckDB connection
    conn = duckdb.connect("explo_hypermarche.db")
    return conn, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # TD — explo hypermarché

    Ce TD vous guide dans l’exploration des données d'un magasin hypermarché fictif à l'aide de DuckDB 🦆

    avec **en entrée** un **excel de commandes** qq peu fouilli comme on les aime

    👉 Certaines cellules contiennent des `TODO` à compléter.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----
    ## Préparation des couches de rafinement
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- on prépare tout de suite les couches de rafinement de nos données
        create schema if not exists raw; --> données brutes (tel quel)
        create schema if not exists stg; --> tables & colonnes renommées & typées (base de données & compréhension friendly)
        create schema if not exists dtm; --> tables de dimension & faits préparées, prêtes pour analyse
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----
    ## Chargons les données brutes depuis l'excel
    """)
    return


@app.cell
def _():
    url_hypermarche = 'https://github.com/AntoineGiraud/dbt_hypermarche/raw/refs/heads/main/input/Hypermarche.xlsx'
    url_hypermarche = 'data/Hypermarche.xlsx'
    # url distante ou locale qu'importe DuckDB s'en arrangera :)
    return (url_hypermarche,)


@app.cell
def _(conn, mo, url_hypermarche):
    _df = mo.sql(
        f"""
        -- si on veut lire depuis un excel
        -- > doc: https://duckdb.org/docs/stable/guides/file_formats/excel_import.html
        create or replace table raw.raw_achats as
          from read_xlsx("{url_hypermarche}", sheet = 'Achats', all_varchar = true);
        create or replace table raw.raw_retours as
          from read_xlsx("{url_hypermarche}", sheet = 'Retours');
        create or replace table raw.raw_personnes as
          from read_xlsx("{url_hypermarche}", sheet = 'Personnes');

        --> puissance de marimo en action : f string python {url_hypermarche}
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---------

    ## Regardons les données brutes

    Oula, les colonnes ne sont pas "base de données friendly"

    On va ajuster ça dans la couche staging
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- retourne QUE infos du "schéma" de la base de données
        describe raw.raw_achats;
        """,
        engine=conn
    )
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- summarize fait en plus un p'tit récap min/max/moy/count/count distinct
        summarize raw.raw_achats;
        """,
        engine=conn
    )
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- huum, l'onglet personne a l'être d'être lié à la zone géo de la ville de la commande
        summarize raw.raw_personnes
        """,
        engine=conn
    )
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- ok, telle commande a été retournée, mais le 'Oui' c'est pas très BDD friendly !
        summarize raw.raw_retours
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ____
    ## Staging - renommage des colonnes DB friendly
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- responsables des zones géographiques
        create or replace table stg.stg_zone_has_responsable as
        select
        	"Zone géographique" "zone",
        	"Responsable régional" responsable
        from raw.raw_personnes
        ;
        -- affichons les données
        from stg.stg_zone_has_responsable
        """,
        engine=conn
    )
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- table des retours 🧪
        create or replace table stg.stg_retour_commande as
        select
        	"ID commande" id_commande,
        	replace("Retourné", 'Oui', 1)::int est_retourne
        from raw.raw_retours
        ;
        -- affichons les données
        from stg.stg_retour_commande
        """,
        engine=conn
    )
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- table des commandes 
        select
            -- petite démo de fonctions DuckDB sympas
            * replace (
                strptime("Date de commande", '%m/%d/%Y')::date as "Date de commande",
                replace(profit, ',', '.')::numeric as profit
            )
            -- MAIS 🧪 ... on ne va pas aller loin ainsi pour tout bien renommer & typer
        from raw.raw_achats
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----
    ## Préparation des tables de **dimension**

    ### dim client
    """)
    return


app._unparsable_cell(
    r"""
    select distinct id_client, client_nom as nom, client_segment as segment
    from stg.stg_commande
    """,
    name="_"
)


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- avons nous des doublons dans la dim client ?!!

        select
        	ma_cle_primaire,
            count(1) nb
        from dtm.dim_client
        group by 1
        having count(1) > 1
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### dim ville
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Continuez :) 🧪
    """)
    return


if __name__ == "__main__":
    app.run()
