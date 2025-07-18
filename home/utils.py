import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def get_drug_info_from_fda(drug_name):
    """
    Récupère les informations d'un médicament depuis l'API OpenFDA avec mise en cache.
    
    Args:
        drug_name (str): Nom du médicament à rechercher
        
    Returns:
        dict: Informations sur le médicament ou None en cas d'erreur
    """
    if not drug_name:
        logger.warning("Nom de médicament non fourni")
        return None
    
    # Vérifier si l'information est en cache
    cache_key = f'fda_drug_info_{drug_name.lower()}'
    cached_info = cache.get(cache_key)
    if cached_info is not None:
        logger.info(f"Données FDA trouvées en cache pour {drug_name}")
        return cached_info
        
    base_url = "https://api.fda.gov/drug/label.json"
    
    try:
        # Première tentative avec le nom exact
        params = {
            'search': f'openfda.brand_name:"{drug_name}"',
            'limit': 1
        }
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Si pas de résultats, essayer une recherche plus large
        if not data.get('results'):
            params['search'] = f'openfda.brand_name:{drug_name}'
            response = requests.get(base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
        
        if data.get('results'):
            result = data['results'][0]
            info = {
                'brand_name': result.get('openfda', {}).get('brand_name', [None])[0],
                'generic_name': result.get('openfda', {}).get('generic_name', [None])[0],
                'indications': result.get('indications_and_usage', [None])[0],
                'warnings': result.get('warnings', [None])[0],
                'side_effects': result.get('adverse_reactions', [None])[0],
                'dosage': result.get('dosage_and_administration', [None])[0],
                'manufacturer': result.get('openfda', {}).get('manufacturer_name', [None])[0],
                'route': result.get('openfda', {}).get('route', [None])[0],
            }
            # Mettre en cache pour 24 heures
            cache.set(cache_key, info, timeout=60*60*24)
            return info
            
    except requests.Timeout:
        logger.error(f"Timeout lors de la requête FDA pour {drug_name}")
        return None
    except requests.RequestException as e:
        logger.error(f"Erreur lors de la requête FDA pour {drug_name}: {str(e)}")
        return None
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Erreur lors du traitement des données FDA pour {drug_name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la récupération des données FDA pour {drug_name}: {str(e)}")
        return None
        
    logger.info(f"Aucune information FDA trouvée pour {drug_name}")
    return None
