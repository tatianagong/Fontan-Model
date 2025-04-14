// =============================================
// GENERAL UTILITY FUNCTIONS (Used across pages)
// =============================================

function updateValue(displayId, value) {
    const element = document.getElementById(displayId);
    if (element) {
        element.innerText = value;
    }
}

function showConfirmationModal(condition) {
    const modal = document.getElementById("confirmation-modal");
    const modalText = document.getElementById("modal-text");

    if (modal && modalText) {
        const messages = {
            "lowPreload": "Low Preload preset applied! Low preload refers to...",
            "lungProblem": "Lung Problem preset applied! Pulmonary diseases...",
            "heartFailure": "Heart Failure preset applied! In Fontan circulation..."
        };

        modalText.innerText = messages[condition] || "Preset applied successfully!";
        modal.style.display = "block";

        document.getElementById("modal-close").onclick = function() {
            modal.style.display = "none";
        };
        
        window.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        };
    }
}

// =============================================
// IMAGE MAP AND MODAL FUNCTIONALITY
// (For index.html with the Fontan diagram)
// =============================================

function setupImageMapModal() {
    const modal = document.getElementById('popup-modal');
    const modalText = document.getElementById('diagram-text');
    const closeButton = document.getElementById('diagram-close');
    const image = document.getElementById('clickable-image');

    if (!modal || !modalText || !closeButton || !image) return;

    // Add click listeners to each area
    document.querySelectorAll('area').forEach((area) => {
        area.addEventListener('click', (e) => {
            e.preventDefault();
            const content = area.getAttribute('data-content');
            modalText.textContent = content;
            modal.style.display = 'block';
        });
    });

    // Close handlers
    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Initialize image map resizing
    if (typeof imageMapResize === 'function') {
        imageMapResize();
    }
}

// =============================================
// SLIDER PAGE FUNCTIONALITY (/slider_page)
// =============================================

function setupSliderPage() {
    const form = document.getElementById('parameterForm');
    if (!form) return;

    // Create a container for the results table if it doesn't exist
    let resultsContainer = document.getElementById('sliderResults');
    if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.id = 'sliderResults';
        form.appendChild(resultsContainer);
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        // collect slider values
        const HR = document.getElementById('HR').value;
        const UVR = document.getElementById('UVR').value;
        const LVR = document.getElementById('LVR').value;
        const PVR = document.getElementById('PVR').value;
        const S_sa = document.getElementById('S_sa').value;
        const Hb = document.getElementById('Hb').value;
        const CVO2u = document.getElementById('CVO2u').value;
        const CVO2l = document.getElementById('CVO2l').value;

        fetch('/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ HR, UVR, LVR, PVR, S_sa, Hb, CVO2u, CVO2l })
        })
        .then(response => response.json())
        .then(data => {
           // Generate single-column results table
           resultsContainer.innerHTML = `
           <table class="results-table">
               <thead>
                   <tr>
                       <th>Output Parameter</th>
                       <th>Value</th>
                   </tr>
               </thead>
               <tbody>
                   <tr><td>Cardiac Output (L/min)</td><td>${data.Q_v}</td></tr>
                   <tr><td>Upper Body Flow (L/min)</td><td>${data.Q_u}</td></tr>
                   <tr><td>Lower Body Flow (L/min)</td><td>${data.Q_l}</td></tr>
                   <tr><td>Pulmonary Flow (L/min)</td><td>${data.Q_p}</td></tr>
                   <tr><td>Systemic Artery Pressure (mmHg)</td><td>${data.P_sa}</td></tr>
                   <tr><td>Fontan Pressure (mmHg)</td><td>${data.P_pa}</td></tr>
                   <tr><td>Common Atrium Pressure (mmHg)</td><td>${data.P_pv}</td></tr>
                   <tr><td>Oxygen Extraction Ratio</td><td>${data.OER}</td></tr>
               </tbody>
           </table>
       `;
   })
        .catch(error => console.error('Error:', error));
    });
}

// =============================================
// CONDITIONS PAGE FUNCTIONALITY (/conditions_page)
// =============================================

function setupConditionsPage() {
    // Apply preset when a preset button is clicked
    document.querySelectorAll(".preset-btn").forEach(button => {
        button.addEventListener("click", function() {
            const condition = this.dataset.condition;
            fetch(`/apply_preset?condition=${condition}`)
            .then(response => response.json())
            .then(data => {
                for (const key in data) {
                    if (document.getElementById(key)) {
                        document.getElementById(key).value = data[key];
                        document.getElementById(`${key}Value`).innerText = data[key];
                    }
                }
                showConfirmationModal(condition);
            })
            .catch(error => console.error("Error applying preset:", error));
        });
    });

    // Handle condition calculation
    const conditionBtn = document.getElementById("conditionSubmitBtn");
    if (!conditionBtn) return;

    conditionBtn.addEventListener("click", function() {
        const sliderValuesAdjusted = {
            HR: document.getElementById("HR").value,
            UVR: document.getElementById("UVR").value,
            LVR: document.getElementById("LVR").value,
            PVR: document.getElementById("PVR").value,
            S_sa: document.getElementById("S_sa").value,
            Hb: document.getElementById("Hb").value,
            CVO2u: document.getElementById("CVO2u").value,
            CVO2l: document.getElementById("CVO2l").value
        };

        const sliderValuesBaseline = { ...sliderValuesAdjusted };
        let baselineLabel = "Baseline";

        if (Number(sliderValuesAdjusted.PVR) === 27) { 
            sliderValuesBaseline.PVR = 10;
            baselineLabel = "Baseline (PVR=10)";
        }

        Promise.all([
            fetch("/calculate_condition_values", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(sliderValuesAdjusted)
            }).then(res => res.json()),
            fetch("/process", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(sliderValuesBaseline)
            }).then(res => res.json())
        ])
        .then(([adjustedResult, baselineResult]) => {
            const resultsDiv = document.getElementById("conditionResults");
            if (resultsDiv) {
                resultsDiv.innerHTML = `
                    <table class="results-table">
                        <thead>
                            <tr>
                                <th>Parameter</th>
                                <th>With Condition</th>
                                <th>${baselineLabel}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>Cardiac Output (L/min)</td><td>${adjustedResult.Q_v}</td><td>${baselineResult.Q_v}</td></tr>
                            <tr><td>Blood Flow to Upper Body (L/min)</td><td>${adjustedResult.Q_u}</td><td>${baselineResult.Q_u}</td></tr>
                            <tr><td>Blood Flow to Lower Body (L/min)</td><td>${adjustedResult.Q_l}</td><td>${baselineResult.Q_l}</td></tr>
                            <tr><td>Pulmonary Blood Flow (L/min)</td><td>${adjustedResult.Q_p}</td><td>${baselineResult.Q_p}</td></tr>
                            <tr><td>Systemic Artery Pressure (mmHg)</td><td>${adjustedResult.P_sa}</td><td>${baselineResult.P_sa}</td></tr>
                            <tr><td>Fontan Pressure (mmHg)</td><td>${adjustedResult.P_pa}</td><td>${baselineResult.P_pa}</td></tr>
                            <tr><td>Common Atrium Pressure (mmHg)</td><td>${adjustedResult.P_pv}</td><td>${baselineResult.P_pv}</td></tr>
                            <tr><td>Oxygen Extraction Ratio</td><td>${adjustedResult.OER}</td><td>${baselineResult.OER}</td></tr>
                        </tbody>
                    </table>
                `;
            }
        })
        .catch(error => console.error("Error fetching data:", error));
    });
}

// =============================================
// PLOT PAGE FUNCTIONALITY (/plot_page)
// =============================================

function setupPlotPage() {
    const displayPlotButton = document.getElementById('displayPlotButton');
    const plotTypeSelect = document.getElementById('plotType');
    const plotContainer = document.getElementById('plotContainer');

    if (displayPlotButton && plotTypeSelect && plotContainer) {
        displayPlotButton.addEventListener('click', async () => {
            const selectedPlot = plotTypeSelect.value;
            try {
                const response = await fetch(`/generate_plot?plot_type=${selectedPlot}`);
                const data = await response.json();
                plotContainer.innerHTML = `<img src="data:image/png;base64,${data.plot}" alt="Generated Plot">`;
            } catch (error) {
                plotContainer.innerHTML = `<p style="color: red;">Error displaying plot.</p>`;
            }
        });
    }

    // Custom plot functionality
    const generatePlotButton = document.getElementById('generatePlotButton');
    const customPlotContainer = document.getElementById('customPlotContainer');

    if (generatePlotButton && customPlotContainer) {
        generatePlotButton.addEventListener('click', async () => {
            const input1 = document.getElementById('inputDropdown1').value;
            const input2 = document.getElementById('inputDropdown2').value;
            const output = document.getElementById('outputDropdown').value;

            try {
                const response = await fetch(
                    `/generate_custom_plot?input1=${input1}&input2=${input2}&output=${output}`
                );
                const data = await response.json();
                customPlotContainer.innerHTML = `<img src="data:image/png;base64,${data.plot}" alt="Generated Custom Plot">`;
            } catch (error) {
                customPlotContainer.innerHTML = `<p style="color: red;">Error displaying custom plot.</p>`;
            }
        });
    }
}

// =============================================
// MAIN INITIALIZATION (Runs when page loads)
// =============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log("Initializing page scripts...");
    
    // Setup functionality based on what exists on the page
    setupImageMapModal();  // For index.html
    setupSliderPage();     // For /slider_page
    setupConditionsPage(); // For /conditions_page
    setupPlotPage();       // For /plot_page

    // Initialize image map if it exists
    if (document.getElementById('clickable-image') && typeof imageMapResize === 'function') {
        imageMapResize();
    }
});