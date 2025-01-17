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