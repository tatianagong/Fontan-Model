// Update displayed values dynamically
function updateValue(displayId, value) {
    document.getElementById(displayId).innerText = value;
}

// shows confirmation messages after preset conditions are clicked
function showConfirmationModal(condition) {
    const modal = document.getElementById("confirmation-modal");
    const modalText = document.getElementById("modal-text");

    // Custom message based on selected preset
    const messages = {
        "lowPreload": "Low Preload preset applied! Compliance values updated.",
        "lungProblem": "Lung Problem preset applied! No compliance changes were needed.",
        "heartFailure": "Heart Failure preset applied! Heart rate and compliance updated."
    };

    // Set dynamic modal text for preset conditions
    modalText.innerText = messages[condition] || "Preset applied successfully!";
    
    // Display the modal
    modal.style.display = "block";

    // Close modal when clicking '×' or outside the modal
    document.getElementById("modal-close").onclick = function () {
        modal.style.display = "none";
    };
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
}

// Handle form submission
document.getElementById('parameterForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Collect slider values
    const HR = document.getElementById('HR').value;
    const UVR = document.getElementById('UVR').value;
    const LVR = document.getElementById('LVR').value;
    const PVR = document.getElementById('PVR').value;
    const S_sa = document.getElementById('S_sa').value;
    const Hb = document.getElementById('Hb').value;
    const CVO2u = document.getElementById('CVO2u').value;
    const CVO2l = document.getElementById('CVO2l').value;

    // Send the parameters to the backend
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ HR, UVR, LVR, PVR, S_sa, Hb, CVO2u, CVO2l }) // Sending multiple parameters
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Display the results
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = `
            <p>Cardiac Output (L/min): ${data.Q_v}</p>
            <p>Blood Flow into the Upper Body (L/min): ${data.Q_u}</p>
            <p>Blood Flow into the Lower Body (L/min): ${data.Q_l}</p>
            <p>Blood Flow into the Lungs (L/min): ${data.Q_p}</p>
            <p>Pressure of the Systemic Artery (mmHg): ${data.P_sa}</p>
            <p>Oxygen Extraction Ratio: ${data.OER}</p>
        `;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

// Handle preset condition submit (NEW! Uses `/calculate_condition_values`)
document.addEventListener('DOMContentLoaded', function () {
    console.log("script.js loaded successfully.");
        // Apply preset when a preset button is clicked
        document.querySelectorAll(".preset-btn").forEach(button => {
            button.addEventListener("click", function () {
                const condition = this.dataset.condition; // Use the "data-condition" attribute
                console.log(`Applying preset: ${condition}`);
    
                fetch(`/apply_preset?condition=${condition}`)
                .then(response => response.json())
                .then(data => {
                    console.log("Preset Applied - Backend Response:", data);
    
                    // Update sliders with backend values
                    for (const key in data) {
                        if (document.getElementById(key)) {
                            document.getElementById(key).value = data[key];
                            document.getElementById(`${key}Value`).innerText = data[key];
                        }
                    }
    
                    // Show confirmation message
                    showConfirmationModal(condition);
                })
                .catch(error => console.error("Error applying preset:", error));
            });
        });
    
        // Handle condition calculation when "Submit" is clicked
        const conditionBtn = document.getElementById("conditionSubmitBtn");
    
        if (conditionBtn) {
            conditionBtn.addEventListener("click", function () {
                console.log("Submit button clicked! Sending request to /calculate_condition_values...");
    
                // Collect slider values
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

                // Copy of sliders for baseline
                const sliderValuesBaseline = { ...sliderValuesAdjusted };

                // Check if pulmonary disease is the selected condition (PVR = 27)
                const pvrValue = Number(sliderValuesAdjusted.PVR);
                let baselineLabel = "Baseline";

                if (pvrValue === 27) { 
                    // Force PVR=10 for baseline
                    sliderValuesBaseline.PVR = 10;
                    baselineLabel = "Baseline (PVR=10)";
                    console.log("Pulmonary Disease detected: Baseline PVR set to 10.");
                } else {
                    console.log("Other condition detected: Baseline will use same PVR as adjusted.");
                }

    
                // Fetch both results in parallel
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
                    console.log("With Compliance:", adjustedResult);
                    console.log("Without Compliance:", baselineResult);
                    

                    // Build table combining both
                    document.getElementById("conditionResults").innerHTML = `
                        <table class="table-results">
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
                })
                .catch(error => console.error("Error fetching data from backend:", error));
            });
            } else {
                console.error("conditionSubmitBtn not found in the DOM!");
            }

// Add click functionality to the Fontan diagram
const image = document.getElementById('clickable-image');
image.addEventListener('click', () => {});

// Modals
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('popup-modal');
    const modalText = document.getElementById('modal-text');
    const closeButton = document.getElementById('modal-close');

    // Add click listeners to each area
    document.querySelectorAll('area').forEach((area) => {
        area.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent navigation (if href is empty)
            // get custom content from data-content
            const content = area.getAttribute('data-content');
            modalText.textContent = content; // Set dynamic content
            modal.style.display = 'block'; // Show the modal
        });
    });

    // Close the modal when clicking the "X" button
    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close the modal when clicking outside the modal content
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// Dropdown and Display Plot Button Functionality
document.addEventListener('DOMContentLoaded', () => {
    const displayPlotButton = document.getElementById('displayPlotButton');
    const plotTypeSelect = document.getElementById('plotType');
    const plotContainer = document.getElementById('plotContainer');

    
    displayPlotButton.addEventListener('click', async () => {
        const selectedPlot = plotTypeSelect.value;

        try {
            const response = await fetch(`/generate_plot?plot_type=${selectedPlot}`);
            if (!response.ok) {
                throw new Error('Failed to fetch the plot');
            }

            const data = await response.json();
            plotContainer.innerHTML = `<img src="data:image/png;base64,${data.plot}" alt="Generated Plot">`;
        } catch (error) {
            console.error('Error displaying the plot:', error);
            plotContainer.innerHTML = `<p style="color: red;">Error displaying the plot. Check the console for details.</p>`;
        }
    });

    // New functionality for generating a plot based on input/output dropdowns
    const generatePlotButton = document.getElementById('generatePlotButton');
    const inputDropdown1 = document.getElementById('inputDropdown1');
    const inputDropdown2 = document.getElementById('inputDropdown2');
    const outputDropdown = document.getElementById('outputDropdown');
    const customPlotContainer = document.getElementById('customPlotContainer');  // Targeting the second plot container

    generatePlotButton.addEventListener('click', async () => {
        const input1 = inputDropdown1.value;
        const input2 = inputDropdown2.value;
        const output = outputDropdown.value;

        try {
            const response = await fetch(`/generate_custom_plot?input1=${input1}&input2=${input2}&output=${output}`);
            if (!response.ok) {
                throw new Error('Failed to fetch the plot');
            }

            const data = await response.json();
            customPlotContainer.innerHTML = `<img src="data:image/png;base64,${data.plot}" alt="Generated Custom Plot">`;
        } catch (error) {
            console.error('Error displaying the plot:', error);
            customPlotContainer.innerHTML = `<p style="color: red;">Error displaying the plot. Check the console for details.</p>`;
        }
    });
});
});