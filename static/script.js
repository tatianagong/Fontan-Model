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
                const sliderValues = {
                    HR: document.getElementById("HR").value,
                    UVR: document.getElementById("UVR").value,
                    LVR: document.getElementById("LVR").value,
                    PVR: document.getElementById("PVR").value,
                    S_sa: document.getElementById("S_sa").value,
                    Hb: document.getElementById("Hb").value,
                    CVO2u: document.getElementById("CVO2u").value,
                    CVO2l: document.getElementById("CVO2l").value
                };
    
                fetch("/calculate_condition_values", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(sliderValues) // Send slider values to backend
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(result => {
                    console.log("Backend Response:", result);
    
                    // Display results dynamically
                    document.getElementById("conditionResults").innerHTML = `
                        <strong>Cardiac Output:</strong> ${result.Q_v} L/min<br>
                        <strong>Blood Flow to Upper Body:</strong> ${result.Q_u} L/min<br>
                        <strong>Blood Flow to Lower Body:</strong> ${result.Q_l} L/min<br>
                        <strong>Pulmonary Blood Flow:</strong> ${result.Q_p} L/min<br>
                        <strong>Systemic Artery Pressure:</strong> ${result.P_sa} mmHg<br>
                        <strong>Pulmonary Artery Pressure:</strong> ${result.P_pa} mmHg<br>
                        <strong>Pulmonary Vein Pressure:</strong> ${result.P_pv} mmHg<br>
                        <strong>Oxygen Saturation in Pulmonary Artery:</strong> ${result.S_pa}<br>
                        <strong>Oxygen Saturation in Pulmonary Vein:</strong> ${result.S_pv}<br>
                        <strong>Oxygen Saturation in Upper Body:</strong> ${result.S_svu}<br>
                        <strong>Oxygen Saturation in Lower Body:</strong> ${result.S_svl}<br>
                        <strong>Oxygen Extraction Ratio:</strong> ${result.OER}<br>
                        <strong>Compliance Values:</strong><br>
                        C_d: ${result.C_d}<br>
                        C_s: ${result.C_s}<br>
                        C_sa: ${result.C_sa}<br>
                        C_pv: ${result.C_pv}<br>
                        C_pa: ${result.C_pa}<br>
                    `;
                })
                .catch(error => console.error("Error fetching calculated values:", error));
            });
        } else {
            console.error("conditionSubmitBtn not found in the DOM!");
        }

//     const conditionBtn = document.getElementById("conditionSubmitBtn");

//     if (conditionBtn) {
//         conditionBtn.addEventListener("click", function () {
//             console.log("Submit button clicked! Sending request to /calculate_condition_values...");

//             fetch("/calculate_condition_values")  // Calls the new Flask route
//             .then(response => response.json())
//             .then(result => {
//                 console.log("Backend Response:", result);

//                 if (result.error) {
//                     document.getElementById("conditionResults").innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
//                     return;
//                 }

//                 // Display computed values
//                 document.getElementById("conditionResults").innerHTML = `
//                     <strong>Q_v:</strong> ${result.Q_v} L/min<br>
//                     <strong>Q_u:</strong> ${result.Q_u} L/min<br>
//                     <strong>Q_l:</strong> ${result.Q_l} L/min<br>
//                     <strong>Q_p:</strong> ${result.Q_p} L/min<br>
//                     <strong>P_sa:</strong> ${result.P_sa} mmHg<br>
//                     <strong>P_pa:</strong> ${result.P_pa} mmHg<br>
//                     <strong>P_pv:</strong> ${result.P_pv} mmHg<br>
//                     <strong>S_pa:</strong> ${result.S_pa}<br>
//                     <strong>S_pv:</strong> ${result.S_pv}<br>
//                     <strong>S_svu:</strong> ${result.S_svu}<br>
//                     <strong>S_svl:</strong> ${result.S_svl}<br>
//                     <strong>OER:</strong> ${result.OER}<br>
//                     <strong>Compliance Values:</strong><br>
//                     C_d: ${result.C_d}<br>
//                     C_s: ${result.C_s}<br>
//                     C_sa: ${result.C_sa}<br>
//                     C_pv: ${result.C_pv}<br>
//                     C_pa: ${result.C_pa}<br>
//                 `;
//             })
//             .catch(error => console.error("Error fetching calculated values:", error));
//         });
//     } else {
//         console.error("conditionSubmitBtn not found in the DOM!");
//     }
// });

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