$(document).ready(function() {
    // Éléments du DOM
    const drugNameInput = $('#id_nom_medicament');
    const drugInfo = $('#drugInfo');
    const drugInfoContent = $('#drugInfoContent');
    const drugSearchSpinner = $('#drugSearchSpinner');
    const suggestDosageBtn = $('#suggestDosage');
    const dosageInput = $('#id_posologie');
    const dosageRecommendations = $('#dosageRecommendations');
    
    // Cache pour les résultats de recherche
    const drugCache = {};
    const MAX_RETRIES = 3;
    let retryCount = 0;
    let offlineMode = false;

    // Configuration de l'autocomplétion
    drugNameInput.autocomplete({
        minLength: 3,
        delay: 500,
        source: function(request, response) {
            const term = request.term.trim();
            
            if (drugCache[term]) {
                response(drugCache[term]);
                return;
            }

            if (offlineMode) {
                showOfflineWarning();
                response([]);
                return;
            }

            drugSearchSpinner.removeClass('d-none');
            
            $.ajax({
                url: '/search-drug/' + encodeURIComponent(term) + '/',
                method: 'GET',
                success: function(data) {
                    if (Array.isArray(data) && data.length > 0) {
                        const suggestions = data.map(item => ({
                            label: `${item.brand_name} (${item.generic_name || 'Nom générique non disponible'})`,
                            value: item.brand_name,
                            info: item
                        }));
                        drugCache[term] = suggestions;
                        response(suggestions);
                    } else {
                        response([]);
                        showNoResultsMessage();
                    }
                },
                error: handleApiError,
                complete: () => drugSearchSpinner.addClass('d-none')
            });
        },
        select: function(event, ui) {
            if (ui.item.info) {
                displayDrugInfo(ui.item.info);
                suggestDosageBtn.prop('disabled', !ui.item.info.dosage);
            }
        }
    });

    // Personnalisation du rendu des suggestions
    drugNameInput.autocomplete('instance')._renderItem = function(ul, item) {
        return $('<li>')
            .append(`<div class="ui-menu-item-wrapper">
                <strong>${item.info.brand_name}</strong>
                ${item.info.generic_name ? `<br><small>${item.info.generic_name}</small>` : ''}
                ${item.info.manufacturer ? `<br><small>Fabricant: ${item.info.manufacturer}</small>` : ''}
            </div>`)
            .appendTo(ul);
    };

    // Gestion de la saisie manuelle
    let searchTimeout;
    drugNameInput.on('input', function() {
        clearTimeout(searchTimeout);
        const drugName = $(this).val().trim();
        
        if (drugName.length < 3) {
            drugInfo.addClass('d-none');
            return;
        }

        if (offlineMode) {
            showOfflineWarning();
            return;
        }

        searchTimeout = setTimeout(() => {
            drugSearchSpinner.removeClass('d-none');
            retryCount = 0;
            searchDrug(drugName);
        }, 500);
    });

    // Fonction de recherche de médicament
    function searchDrug(drugName) {
        $.ajax({
            url: '/get-drug-info/' + encodeURIComponent(drugName) + '/',
            method: 'GET',
            timeout: 5000,
            success: function(data) {
                displayDrugInfo(data);
                retryCount = 0;
            },
            error: function(xhr, status, error) {
                if ((status === 'timeout' || error === 'timeout') && retryCount < MAX_RETRIES) {
                    retryCount++;
                    console.log(`Nouvelle tentative (${retryCount}/${MAX_RETRIES})...`);
                    setTimeout(() => searchDrug(drugName), 1000 * retryCount);
                    return;
                }
                handleApiError(xhr);
            },
            complete: () => drugSearchSpinner.addClass('d-none')
        });
    }

    // Affichage des informations sur le médicament
    function displayDrugInfo(info) {
        if (!info) {
            drugInfo.addClass('d-none');
            return;
        }

        const content = `
            <div class="drug-info-section">
                <p><strong>Nom générique:</strong> ${info.generic_name || 'Non disponible'}</p>
                <p><strong>Fabricant:</strong> ${info.manufacturer || 'Non disponible'}</p>
                <p><strong>Voie d'administration:</strong> ${info.route || 'Non disponible'}</p>
            </div>
            
            <div class="drug-info-section mt-3">
                <p><strong>Indications:</strong></p>
                <div class="alert alert-info small">
                    ${info.indications ? formatText(info.indications) : 'Non disponible'}
                </div>
            </div>

            ${info.warnings ? `
            <div class="drug-info-section mt-3">
                <p><strong>Avertissements importants:</strong></p>
                <div class="alert alert-warning small">
                    ${formatText(info.warnings)}
                </div>
            </div>` : ''}

            ${info.side_effects ? `
            <div class="drug-info-section mt-3">
                <p><strong>Effets secondaires:</strong></p>
                <div class="alert alert-secondary small">
                    ${formatText(info.side_effects)}
                </div>
            </div>` : ''}

            ${info.dosage ? `
            <div class="drug-info-section mt-3">
                <p><strong>Posologie recommandée:</strong></p>
                <div class="alert alert-info small">
                    ${formatText(info.dosage)}
                </div>
            </div>` : ''}
        `;

        drugInfoContent.html(content);
        drugInfo.removeClass('d-none alert-warning').addClass('alert-info');
        
        if (info.dosage) {
            dosageRecommendations.html(formatText(info.dosage));
            suggestDosageBtn.prop('disabled', false);
        } else {
            dosageRecommendations.html('<em>Aucune recommandation disponible</em>');
            suggestDosageBtn.prop('disabled', true);
        }
    }

    // Gestion des suggestions de posologie
    suggestDosageBtn.click(function() {
        const recommendation = dosageRecommendations.text();
        if (recommendation && recommendation !== 'Aucune recommandation disponible') {
            dosageInput.val(recommendation);
        }
    });

    // Gestion du mode hors ligne
    window.addEventListener('online', () => {
        offlineMode = false;
        drugInfo.removeClass('alert-warning');
    });

    window.addEventListener('offline', () => {
        offlineMode = true;
        showOfflineWarning();
    });

    // Fonctions utilitaires
    function formatText(text) {
        if (!text) return '';
        return text
            .replace(/\n/g, '<br>')
            .replace(/•/g, '<br>•')
            .split('<br>')
            .filter(line => line.trim())
            .join('<br>');
    }

    function showOfflineWarning() {
        drugInfo.removeClass('d-none alert-info')
            .addClass('alert-warning')
            .find('#drugInfoContent')
            .html(`
                <p><i class="fas fa-exclamation-triangle"></i> Mode hors ligne</p>
                <p>La recherche de médicaments nécessite une connexion Internet.</p>
            `);
    }

    function showNoResultsMessage() {
        drugInfo.removeClass('d-none alert-info')
            .addClass('alert-warning')
            .find('#drugInfoContent')
            .html(`
                <p><i class="fas fa-info-circle"></i> Aucun résultat</p>
                <p>Aucun médicament trouvé pour cette recherche.</p>
            `);
    }

    function handleApiError(xhr) {
        console.error('Erreur API:', xhr.responseText);
        drugInfo.removeClass('d-none alert-info')
            .addClass('alert-warning')
            .find('#drugInfoContent')
            .html(`
                <p><i class="fas fa-exclamation-triangle"></i> Erreur</p>
                <p>${xhr.status === 429 ? 
                    'Limite de requêtes API atteinte. Veuillez réessayer dans quelques instants.' : 
                    'Une erreur est survenue lors de la recherche. Veuillez réessayer.'}</p>
            `);
    }
});
