// Variables globales
let yearlyChart = null;

// Fonction principale d'initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log("Document chargé, initialisation...");
    
    // Analyser les données JSON
    let carDataParsed;
    let carGifsParsed;
    
    try {
        // Récupérer et parser les données des voitures
        const carDataRaw = document.getElementById('car-data').textContent;
        carDataParsed = JSON.parse(carDataRaw);
        console.log("Données des voitures chargées:", carDataParsed);
        
        // Récupérer et parser les GIFs des voitures
        const carGifsRaw = document.getElementById('car-gifs').textContent;
        carGifsParsed = JSON.parse(carGifsRaw);
        console.log("GIFs des voitures chargés:", carGifsParsed);
    } catch (e) {
        console.error("Erreur lors du parsing des données:", e);
        alert("Erreur lors du chargement des données. Veuillez rafraîchir la page.");
        return;
    }
    
    // Éléments DOM
    const yearFilter = document.getElementById('year-filter');
    const brandFilter = document.getElementById('brand-filter');
    const applyButton = document.getElementById('apply-filters');
    const carTitle = document.getElementById('car-title');
    const salesVolume = document.getElementById('sales-volume');
    const carGif = document.getElementById('car-gif');
    const topBrandsContainer = document.getElementById('top-brands');
    const yearlyChartCanvas = document.getElementById('yearly-chart');
    
    // Initialiser l'affichage si les données sont disponibles
    if (carDataParsed && carDataParsed.length > 0) {
        updateCharts(carDataParsed);
        populateTopBrands(carDataParsed);
        
        // Écouteur d'événement pour le bouton d'application des filtres
        applyButton.addEventListener('click', function() {
            const selectedYear = parseInt(yearFilter.value);
            const selectedBrand = brandFilter.value;
            console.log(`Filtrage - Année: ${selectedYear}, Marque: ${selectedBrand}`);
            updateDisplay(selectedYear, selectedBrand, carDataParsed, carGifsParsed);
        });
        
        // Initialiser avec les valeurs par défaut si disponibles
        if (yearFilter.options.length > 0 && brandFilter.options.length > 0) {
            const defaultYear = parseInt(yearFilter.value);
            const defaultBrand = brandFilter.value;
            updateDisplay(defaultYear, defaultBrand, carDataParsed, carGifsParsed);
        }
    } else {
        console.error("Aucune donnée de voiture disponible");
        carTitle.textContent = "Erreur: Aucune donnée disponible";
    }
    
    // Fonction pour mettre à jour l'affichage
    function updateDisplay(year, brand, carData, carGifs) {
        console.log(`Mise à jour de l'affichage - Année: ${year}, Marque: ${brand}`);
        
        // Filtrer les données
        const filteredData = carData.filter(car => 
            car.year === year && car.marque === brand
        );
        
        console.log("Données filtrées:", filteredData);
        
        if (filteredData.length > 0) {
            const volume = filteredData[0].volume;
            
            // Mettre à jour les informations textuelles
            carTitle.textContent = `${brand} (${year})`;
            salesVolume.textContent = volume;
            
            // Afficher le GIF de la voiture avec animation
            carGif.style.opacity = '0';
            setTimeout(() => {
                const gifPath = carGifs[brand];
                if (gifPath) {
                    carGif.src = `/static/logs/${gifPath}`;
                    carGif.alt = `${brand} logo animé`;
                    
                    // Animation de l'image
                    carGif.style.opacity = '1';
                    carGif.classList.add('fade-in');
                } else {
                    console.warn(`Aucun GIF trouvé pour la marque: ${brand}`);
                    carGif.src = "";
                    carGif.alt = "Logo non disponible";
                }
            }, 300);
        } else {
            console.warn(`Aucune donnée pour - Année: ${year}, Marque: ${brand}`);
            carTitle.textContent = "Données non disponibles";
            salesVolume.textContent = "-";
            carGif.src = "";
            carGif.alt = "";
        }
    }
    
    // Fonction pour mettre à jour les graphiques
    function updateCharts(carData) {
        if (!yearlyChartCanvas) {
            console.error("Élément du graphique non trouvé");
            return;
        }
        
        try {
            // Préparer les données pour le graphique annuel
            const years = [...new Set(carData.map(item => item.year))].sort();
            const yearlyTotals = years.map(year => {
                return {
                    year: year,
                    total: carData.filter(item => item.year === year)
                        .reduce((sum, item) => sum + item.volume, 0)
                };
            });
            
            console.log("Données pour le graphique annuel:", yearlyTotals);
            
            // Créer le graphique annuel
            const yearlyChartCtx = yearlyChartCanvas.getContext('2d');
            
            if (yearlyChart) {
                yearlyChart.destroy();
            }
            
            yearlyChart = new Chart(yearlyChartCtx, {
                type: 'bar',
                data: {
                    labels: yearlyTotals.map(item => item.year),
                    datasets: [{
                        label: 'Ventes totales',
                        data: yearlyTotals.map(item => item.total),
                        backgroundColor: '#3498db',
                        borderColor: '#2980b9',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (e) {
            console.error("Erreur lors de la création du graphique:", e);
        }
    }
    
    // Fonction pour afficher le top 5 des marques
    function populateTopBrands(carData) {
        if (!topBrandsContainer) {
            console.error("Conteneur du top des marques non trouvé");
            return;
        }
        
        try {
            // Regrouper par marque et calculer le total des ventes
            const brandTotals = {};
            
            carData.forEach(item => {
                if (!brandTotals[item.marque]) {
                    brandTotals[item.marque] = 0;
                }
                brandTotals[item.marque] += item.volume;
            });
            
            // Convertir en tableau et trier
            const sortedBrands = Object.entries(brandTotals)
                .map(([brand, sales]) => ({ brand, sales }))
                .sort((a, b) => b.sales - a.sales)
                .slice(0, 5);
            
            console.log("Top 5 des marques:", sortedBrands);
            
            // Afficher dans le DOM
            topBrandsContainer.innerHTML = '';
            sortedBrands.forEach((item, index) => {
                const brandItem = document.createElement('div');
                brandItem.className = 'brand-item';
                
                // Créer un conteneur pour afficher le logo GIF à côté du texte
                const brandLogo = document.createElement('img');
                if (carGifsParsed[item.brand]) {
                    brandLogo.src = `/static/logs/${carGifsParsed[item.brand]}`;
                    brandLogo.alt = `Logo ${item.brand}`;
                    brandLogo.className = 'brand-logo-small';
                }
                
                brandItem.innerHTML = `
                    <div class="brand-info">
                        <span class="brand-name">${index + 1}. ${item.brand}</span>
                        <span class="brand-sales">${item.sales} ventes</span>
                    </div>
                `;
                
                // Ajouter le logo au début de l'élément
                brandItem.prepend(brandLogo);
                
                topBrandsContainer.appendChild(brandItem);
            });
        } catch (e) {
            console.error("Erreur lors de la création du top des marques:", e);
        }
    }
});