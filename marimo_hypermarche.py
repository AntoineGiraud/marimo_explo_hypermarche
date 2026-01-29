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

    Création des tables de Staging :

    **stg_zone_has_responsable**

    **stg_retour_commande**

    **stg_commande**
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
        -- corriger l'erreur de la requête 

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


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        create or replace table stg.stg_commande as
        select
            "ID ligne" id_ligne,
            "ID commande" id_commande,
            strptime("Date de commande", '%m/%d/%Y')::date dt_commande,
            strptime("Date d'expédition", '%m/%d/%Y')::date dt_expedition,
            "Statut commande" priorite,
            "ID client" id_client,
            "Nom du client" client_nom,
            segment client_segment,
            ville ville_nom,
            région ville_region,
            pays ville_pays,
            "Zone géographique" ville_zone,
            "ID produit" id_produit,
            catégorie produit_categorie,
            "Sous-catégorie" produit_souscategorie,
            "Nom du produit" produit_nom,
            replace("Montant des ventes", ',', '.')::numeric montant_vente,
            quantité::int quantite,
            replace(remise, ',', '.')::numeric remise,
            replace(profit, ',', '.')::numeric profit
        from
            raw.raw_achats;
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    # Astuces et bonnes pratiques SQL database cloud


    ## 1. Éviter le `SELECT *`


    -- Mauvais

    ```sql
    SELECT * FROM ventes;
    ```

    -- Bon

    ```sql
    SELECT
        id_vente,
        date_vente,
        montant
    FROM ventes;
    ```

    ---
    ✅ Moins de données scannées
    ✅ Requêtes plus stables
    ✅ Meilleure lisibilité
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----------------
    ## 2. Utiliser les CTE (WITH)

    utiliser les CTE pour remplacer des sous requête ou simplement dispatcher les régles de gestion

    ### Exemple :

    ```sql
    with ventes_mois as (
        select
            client_id,
            montant
        from ventes
        where date_vente >= date_trunc(month, current_date)
    ), client_cible as (
        select
            client_id,
            nom_client,
        from dim_client
        where type_client in (2,4)
            and region_client not like 'NORD'
    )
    select vm.client_id,
            dc.nom_client,
            sum(vm.montant)
    from ventes_mois vm
            inner join client_cible dc
                using(client_id)
    group by all;
    ```

    ---
    ✅ Lisibilité
    ✅ Découpage logique
    ✅ Mutualisation de calculs
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----------------

    ## 3. Utiliser le qualify à la place de sous requête complexes

    ### Exemple :

        de :

    ``` sql
    select
        src.id_produit,
        src.id_magasin,
        src.quantite_charge,
        src.date_chargement
    from (
        select
            id_produit,
            id_magasin,
            date_chargement,
            row_number() over (partition by id_produit, id_magasin order by date_chargement desc) rn
        from stock_produit_chargement
        ) subquery
    inner join stock_produit_chargement src
        using (id_produit,id_magasin,date_chargement)
    where subquery.rn = 1;
    ```

    à :

    ``` sql
    select
        id_produit,
        id_magasin,
        quantite_chargee,
        date_chargement
    from stock_produit_chargement
    qualify row_number() over (partition by id_produit,id_magasin order by date_chargement desc) = 1;
    ```

    ---
    ✅ Lisibilité
    ✅ Simplification
    ✅ Gestion des doublons
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----
    ## Préparation des tables de **dimension**

    ### dim client
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---------------

    Création de la table dtm.dim_client

    colonne ('id_client','nom','segment')

    source : stg.stg_commande

    requête source de base
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        create or replace table dtm.dim_client as 
        select 
            id_client, 
            client_nom as nom, 
            client_segment as segment
        from stg.stg_commande
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    -----

    Requête de vérification de doublon
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- avons nous des doublons dans la dim_client ?!!
        /*
        select
        from
        group by 
        having
        */
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---------------------------------

    Création de la table dtm.dim_client **sans doublon**
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        /*
        create or replace table dtm.dim_client as 
        */
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    -------------------

    ### dim produit

    Création de la table **dtm.dim_produit**

    *colonne* ('id_produit', 'categorie', 'sous_categorie', 'nom')

    *source* : stg.stg_commande
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        create or replace table dtm.dim_produit as
        select
            id_produit,
            produit_categorie as categorie,
            produit_souscategorie as sous_categorie,
            produit_nom as nom
        from stg.stg_commande
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    -----

    Requête de vérification de doublon
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- avons nous des doublons dans la dim_produit ?!!
        /*
        select
        from
        group by 
        having
        */
        """,
        engine=conn
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---------------------------------

    Création de la table dtm.dim_produit **sans doublon**
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        /*
        create or replace table dtm.dim_produit as 
        */
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    -----

    Vérification de dim_produit

    +

    Embellisement de la données

    dispatch de la colonne nom --> nom, marque, detail, nom raw

    **Fonction utiles** :

    ```sql
    with nom_requête as ()

    split_part(string, separator, index)

    coalesce("colonne testée","colonne if null")

    position(search_string IN string)
    ```
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        from dtm.dim_produit
        """,
        engine=conn
    )
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        /*
        faire une CTE avec les données produit de stg_commande sans doublon

        reprendre cette requête en source pour l'ajouts des nouvelle colonnes

        exemple :

        with data_source as (
        select 
        	*
        from stg.stg_commande
        )select
        	*
        from data_source

        */
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    -------------------

    ### dim ville

    Création de la table **dtm.dim_ville**

    *colonne* ('id_ville', 'cd_ville', 'nom', 'region' , 'pays', 'zone', 'responsable')

    *source* : stg.stg_commande, stg.stg_zone_has_responsable

    Cette fois pas d'id fonctionnel ! Il faut créer un id_technique et un code avec les colonnes ('nom', 'region' , 'pays', 'zone')

    **Fonction utiles** :

    ```sql
    row_number() over (order by "colonnes")

    concat("nom_colonne1","nom_colonne2",...)

    md5("VARCHAR")

    sha256("VARCHAR")
    ```
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        create or replace table dtm.dim_ville as
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---------------

    Requête de vérification de doublon
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        -- avons nous des doublons dans la dim_ville ?!!
        /*
        select
        from
        group by 
        having
        */
        """,
        engine=conn
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ----------------------------

    Création de la table dtm.dim_ville **sans doublon**
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        /*
        create or replace table dtm.dim_ville
        */
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ----------------------

    ## Tables de faits

    ### fct_commande

    Création de la table **dtm.fct_commande**

    colonnes ( id_commande,
        id_client,
        id_ville,
        priorite,
        est_retourne (si null alors 0),
        dt_commande,
        dt_expedition,
        delai_expedition -- (calcule entre dt_commande dt_expedition),
        nb_produits,
        nb_articles,
        montant_vente,
        profit)

    source :

    *stg.stg_commande*

    *stg.stg_retour_commande*

    **Fonction utiles** :

    ```sql
    coalesce("colonne testée","colonne if null")

    date_diff('day', date_debut, date_fin)

    ```
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        /*
        Attention ou doublon garder l'idée de la CTE 
        */
        create or replace table dtm.fct_commande as 
        """,
        engine=conn
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ----------------------

    ### fct_commande_has_produit

    Création de la table **dtm.fct_commande_has_produit**

    colonnes (
        id_commande,
        dt_commande,
        id_ligne,
        id_produit,
        montant_vente,
        quantite,
        remise,
        profit,
        prix_unitaire (montant divisé par la quantité) ,
        prix_unitaire_avant_remise (montant divisé par la quantité, fois le taux de remise)
    )

    source :

    *stg.stg_commande*
    """)
    return


@app.cell
def _(conn, mo):
    _df = mo.sql(
        f"""
        create or replace table dtm.fct_commande as 
        """,
        engine=conn
    )
    return


if __name__ == "__main__":
    app.run()
