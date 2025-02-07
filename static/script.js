/////ADDITIONS TO FILE IN THE INTEREST OF ADDING PLOTS TO THE WEBPAGE ARE ENCLOSED BY FIVE DASHES /////

// Update displayed values dynamically
function updateValue(displayId, value) {
    document.getElementById(displayId).innerText = value;
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

/////
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
/////