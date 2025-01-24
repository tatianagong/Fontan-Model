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