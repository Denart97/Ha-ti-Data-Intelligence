from typing import List, Dict, Any
from sqlalchemy import text
from openai import OpenAI
from backend.core.config import settings
from backend.db.pg_session import SessionLocal
from data_ingestion.utils.logger import logger

class SQLAgent:
    """Agent capable de traduire le langage naturel en SQL et d'exécuter la requête."""

    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
            logger.warning("OPENAI_API_KEY missing. SQLAgent running in Mock mode.")
        self.db = SessionLocal()

    def _get_sql_prompt(self, query: str) -> str:
        return f"""
        Tu es un expert en données macroéconomiques de la Caraïbe.
        Ta mission : traduire la question en une requête SQL valide pour SQLite.
        
        SCHÉMA EXACT DE LA BASE DE DONNÉES SQLITE :
        - pays (id, iso_alpha3, nom_fr, nom_en, created_at)
        - indicateurs (id, code_indicateur, nom, unite_mesure, grand_domaine, created_at)
        - valeurs_indicateurs (id, indicateur_id, pays_id, dataset_id, date_valeur, valeur_numerique, statut, created_at)
        
        CODES INDICATEURS DISPONIBLES :
        - GDP : PIB (Croissance annuelle %)
        - INFLATION : Inflation (Prix à la consommation %)
        - USD_HTG_REF : Taux de change (USD/HTG)
        - UNEMPLOYMENT : Taux de chômage (%)
        - FDI : Investissements Directs Étrangers (% PIB)
        - EDUCATION_EXP : Dépenses en éducation (% PIB)
        - HEALTH_EXP : Dépenses publiques de santé (% PIB)
        - POPULATION : Population totale
        - EXTERNAL_DEBT : Stock de la dette extérieure (USD)
        
        PAYS DISPONIBLES (iso_alpha3) :
        - HTI : Haïti
        - DOM : République Dominicaine
        - CUB : Cuba
        - JAM : Jamaïque
        
        EXEMPLE DE REQUÊTE CORRECTE :
        SELECT v.date_valeur, v.valeur_numerique
        FROM valeurs_indicateurs v
        JOIN indicateurs i ON v.indicateur_id = i.id
        JOIN pays p ON v.pays_id = p.id
        WHERE i.code_indicateur = 'GDP'
          AND p.iso_alpha3 = 'HTI'
        ORDER BY v.date_valeur DESC
        LIMIT 5;
        
        RÈGLES IMPORTANTES :
        - Utilise TOUJOURS les JOINs corrects avec les tables `indicateurs` et `pays`
        - La colonne de valeur s'appelle `valeur_numerique`
        - La colonne de date s'appelle `date_valeur`
        - Retourne UNIQUEMENT la requête SQL, sans commentaire ni blocs Markdown.
        
        QUESTION : {query}
        """

    def execute_query(self, natural_query: str) -> str:
        """Traduit et exécute la requête via LLM."""
        logger.info(f"SQL Agent translating: {natural_query}")
        
        if not self.openai_client:
            return "Erreur : Client IA non configuré. Veuillez vérifier votre clé API."

        try:
            # 1. Traduction via LLM
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": self._get_sql_prompt(natural_query)}],
                temperature=0
            )
            sql_query = response.choices[0].message.content.strip()
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            logger.info(f"Generated SQL: {sql_query}")

            # 2. Exécution
            result = self.db.execute(text(sql_query))
            rows = result.fetchall()
            
            if not rows:
                return "Aucune donnée statistique pertinente trouvée en base pour cette question."

            # 3. Formatage simple du résultat
            formatted_data = "\n".join([str(dict(row._mapping)) for row in rows])
            return f"Résultats Statistique :\n{formatted_data}"

        except Exception as e:
            logger.error(f"SQL Agent failed: {e}")
            return f"Erreur lors de l'analyse statistique : {e}"
        finally:
            self.db.close()
