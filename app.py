###ADDITIONS TO FILE IN THE INTEREST OF ADDING PLOTS TO THE WEBPAGE ARE ENCLOSED BY TRIPLE HASHTAGS ###

from flask import Flask, render_template, request, jsonify
from hlhs_model import fun_flows, fun_sat, C_d, C_s, C_sa, C_pv, C_pa
import scipy.optimize

###
import fontan_plots
from flask import send_from_directory
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
###

app = Flask(__name__)

###
# Ensure you have a folder to save plots
PLOTS_FOLDER = 'static/plots'
os.makedirs(PLOTS_FOLDER, exist_ok=True)
###

# Render the main page
@app.route("/")
def index():
    return render_template("index.html")

# Process the slider input
@app.route("/process", methods=["POST"])
def process():
    data = request.json
    HR = float(data.get("HR"))  # Slider value, e.g., heart rate
    UVR = float(data.get("UVR"))
    LVR = float(data.get("LVR"))
    PVR = float(data.get("PVR"))
    S_sa = float(data.get("S_sa"))
    Hb = float(data.get("Hb"))
    CVO2u = float(data.get("CVO2u"))
    CVO2l = float(data.get("CVO2l"))

    param_flows = ( UVR, LVR, PVR, HR, C_d, C_s, C_sa, C_pv, C_pa)
    z0_flows = (3.1, 1.5, 1.5, 3.2, 75, 26, 2)

    result_flows = scipy.optimize.fsolve(fun_flows, z0_flows, args=param_flows, full_output=True, xtol=1e-4, maxfev=1000, factor=0.1) 
    ( Q_v, Q_u, Q_l, Q_p, P_sa, P_pa, P_pv) = result_flows[0]

    param_sat = ( Q_p, Q_u, Q_l, S_sa, CVO2u, CVO2l, Hb)
    z0_sat = (0.55, 0.99, 0.55, 0.55)

    result_O2_sat = scipy.optimize.fsolve(fun_sat, z0_sat, args=param_sat, full_output=True, xtol=1e-4, maxfev=1000, factor=0.1) 
    ( S_pa, S_pv, S_svu, S_svl ) = result_O2_sat[0]

    OER = (Q_u * (S_sa - S_svu) + Q_l * (S_sa - S_svl))/ ((Q_u + Q_l) * S_sa)

    return jsonify({
        "Q_v": round(Q_v, 2),
        "Q_u": round(Q_u, 2),
        "Q_l": round(Q_l, 2),
        "Q_p": round(Q_p, 2),
        "P_sa": round(P_sa, 2),
        "P_pa": round(P_pa, 2),
        "P_pv": round(P_pv, 2),
        "P_sa": round(P_sa, 2),
        "S_pa": round(S_pa,2),
        "S_pv": round(S_pv,2),
        "S_svu": round(S_svu, 2),
        "S_svl": round(S_svl,2),
        "OER": round(OER, 2),
    })


###
from fontan_plots import plotCO, plotQU, plotQL, plotQP,plotPSA,plotOER
COs=plotCO()
QUs=plotQU()
QLs=plotQL()
QPs=plotQP()
PSAs=plotPSA()
OERs=plotOER()
# Route to generate a plot based on user selection
@app.route('/generate_plot')
def generate_plot():

    plot_type = request.args.get('plot_type')
    
    # Generate the selected plot
    if plot_type == 'CO':
        fig, ax = plt.subplots(figsize=(10, 8))
        normalized_range = np.linspace(0.5, 1.5, 50)  # X-axis values from 0.5 to 1.5

        excluded_params = {
            "Compliance at Dia",
            "Compliance at Sys",
            "Compliance of Systemic Artery",
            "Compliance of Pulmonary Vein",
            "Compliance of Pulmonary Artery",
            "Hemoglobin Concentration"
        }

        # Iterate over each parameter's CO values and plot them
        for param_name, cardiac_outputs in COs.items():
            if param_name not in excluded_params:
                #####
                baseline_value = {"Heart Rate": (100, "beats/min"),
                                  "Upper Body Resistance": (45, "Wood Units"),
                                  "Lower Body Resistance": (35, "Wood Units"),
                                  "Pulmonary Resistance": (10, "Wood Units"),
                                  "Systemic Arterial Oxygen Saturation": (0.99, "%"),
                                  "Hemoglobin Concentration": (15, "g/dL"),
                                  "Oxygen Consumption of Upper Body": (70, "mL O2/min"),
                                  "Oxygen Consumption of Lower Body": (50, "mL O2/min")}[param_name]
            
                
                baseline_value, unit = baseline_value

                # Format the legend label with the baseline value and unit
                label = f"{param_name} (Baseline: {baseline_value} {unit})"
                ######
                ax.plot(normalized_range, cardiac_outputs, label=label)

        ax.set_title('Cardiac Output vs. Parameter Variation')
        ax.set_xlabel("Normalized Parameter Value (0.5x to 1.5x)")
        ax.set_ylabel("Cardiac Output (CO) [L/min]")
        ax.legend(title="Parameters", loc='upper right')
        ax.grid(True)

    elif plot_type == 'Q_u':
        fig, ax = plt.subplots(figsize=(10, 8))
        normalized_range = np.linspace(0.5, 1.5, 50)  # X-axis values from 0.5 to 1.5

        excluded_params = {
            #"Hemoglobin Concentration"
        }

        # Iterate over each parameter's CO values and plot them
        for param_name, QU_outputs in QUs.items():
            if param_name not in excluded_params:

                baseline_value = {
                                    "Heart Rate": (100, "beats/min"),
                                    "Upper Body Resistance": (45, "Wood Units"),
                                    "Lower Body Resistance": (35, "Wood Units"),
                                    "Pulmonary Resistance": (10, "Wood Units"),
                                    "Systemic Arterial Oxygen Saturation": (0.99, "%"),
                                    "Hemoglobin Concentration": (15, "g/dL"),
                                    "Oxygen Consumption of Upper Body": (70, "mL O2/min"),
                                    "Oxygen Consumption of Lower Body": (50, "mL O2/min"),
                                    # Added missing compliance parameters
                                    "Compliance at Dia": (2 / 100, "mL/mmHg"),  
                                    "Compliance at Sys": (0.01 / 100, "mL/mmHg"),
                                    "Compliance of Systemic Artery": (1 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Vein": (30 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Artery": (2 / 135, "mL/mmHg")
                                }[param_name]
                baseline_value, unit = baseline_value
                # Format the legend label with the baseline value and unit
                label = f"{param_name} (Baseline: {baseline_value} {unit})"

                ######
                ax.plot(normalized_range, QU_outputs, label=label)

        ax.set_title('Upper Body Blood Flow (Q_u) vs. Parameter Variation')
        ax.set_xlabel("Normalized Parameter Value (0.5x to 1.5x)")
        ax.set_ylabel("Upper Body Flow (Q_u) [L/min]")
        ax.legend(title="Parameters", loc='upper right')
        ax.grid(True)

    elif plot_type == 'Q_l':
        fig, ax = plt.subplots(figsize=(10, 8))
        normalized_range = np.linspace(0.5, 1.5, 50)  # X-axis values from 0.5 to 1.5

        excluded_params = {
            #"Hemoglobin Concentration"
        }

        # Iterate over each parameter's CO values and plot them
        for param_name, QL_outputs in QLs.items():
            if param_name not in excluded_params:

                baseline_value = {
                                    "Heart Rate": (100, "beats/min"),
                                    "Upper Body Resistance": (45, "Wood Units"),
                                    "Lower Body Resistance": (35, "Wood Units"),
                                    "Pulmonary Resistance": (10, "Wood Units"),
                                    "Systemic Arterial Oxygen Saturation": (0.99, "%"),
                                    "Hemoglobin Concentration": (15, "g/dL"),
                                    "Oxygen Consumption of Upper Body": (70, "mL O2/min"),
                                    "Oxygen Consumption of Lower Body": (50, "mL O2/min"),
                                    # Added missing compliance parameters
                                    "Compliance at Dia": (2 / 100, "mL/mmHg"),  
                                    "Compliance at Sys": (0.01 / 100, "mL/mmHg"),
                                    "Compliance of Systemic Artery": (1 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Vein": (30 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Artery": (2 / 135, "mL/mmHg")
                                }[param_name]
                baseline_value, unit = baseline_value
                # Format the legend label with the baseline value and unit
                label = f"{param_name} (Baseline: {baseline_value} {unit})"

                ######
                ax.plot(normalized_range, QL_outputs, label=label)

        ax.set_title('Lower Body Blood Flow (Q_l) vs. Parameter Variation')
        ax.set_xlabel("Normalized Parameter Value (0.5x to 1.5x)")
        ax.set_ylabel("Lower Body Flow (Q_l) [L/min]")
        ax.legend(title="Parameters", loc='upper right')
        ax.grid(True)
    
    elif plot_type == 'Q_p':
        fig, ax = plt.subplots(figsize=(10, 8))
        normalized_range = np.linspace(0.5, 1.5, 50)  # X-axis values from 0.5 to 1.5

        excluded_params = {
            #"Hemoglobin Concentration"
        }

        # Iterate over each parameter's CO values and plot them
        for param_name, QP_outputs in QPs.items():
            if param_name not in excluded_params:

                baseline_value = {
                                    "Heart Rate": (100, "beats/min"),
                                    "Upper Body Resistance": (45, "Wood Units"),
                                    "Lower Body Resistance": (35, "Wood Units"),
                                    "Pulmonary Resistance": (10, "Wood Units"),
                                    "Systemic Arterial Oxygen Saturation": (0.99, "%"),
                                    "Hemoglobin Concentration": (15, "g/dL"),
                                    "Oxygen Consumption of Upper Body": (70, "mL O2/min"),
                                    "Oxygen Consumption of Lower Body": (50, "mL O2/min"),
                                    # Added missing compliance parameters
                                    "Compliance at Dia": (2 / 100, "mL/mmHg"),  
                                    "Compliance at Sys": (0.01 / 100, "mL/mmHg"),
                                    "Compliance of Systemic Artery": (1 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Vein": (30 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Artery": (2 / 135, "mL/mmHg")
                                }[param_name]
                baseline_value, unit = baseline_value
                # Format the legend label with the baseline value and unit
                label = f"{param_name} (Baseline: {baseline_value} {unit})"

                ######
                ax.plot(normalized_range, QP_outputs, label=label)

        ax.set_title('Pulmonary Blood Flow (Q_p) vs. Parameter Variation')
        ax.set_xlabel("Normalized Parameter Value (0.5x to 1.5x)")
        ax.set_ylabel("Pulmonary Flow (Q_p) [L/min]")
        ax.legend(title="Parameters", loc='upper right')
        ax.grid(True)
    
    elif plot_type == 'P_sa':
        fig, ax = plt.subplots(figsize=(10, 8))
        normalized_range = np.linspace(0.5, 1.5, 50)  # X-axis values from 0.5 to 1.5

        excluded_params = {
            #"Hemoglobin Concentration"
        }

        # Iterate over each parameter's CO values and plot them
        for param_name, PSA_outputs in PSAs.items():
            if param_name not in excluded_params:

                baseline_value = {
                                    "Heart Rate": (100, "beats/min"),
                                    "Upper Body Resistance": (45, "Wood Units"),
                                    "Lower Body Resistance": (35, "Wood Units"),
                                    "Pulmonary Resistance": (10, "Wood Units"),
                                    "Systemic Arterial Oxygen Saturation": (0.99, "%"),
                                    "Hemoglobin Concentration": (15, "g/dL"),
                                    "Oxygen Consumption of Upper Body": (70, "mL O2/min"),
                                    "Oxygen Consumption of Lower Body": (50, "mL O2/min"),
                                    # Added missing compliance parameters
                                    "Compliance at Dia": (2 / 100, "mL/mmHg"),  
                                    "Compliance at Sys": (0.01 / 100, "mL/mmHg"),
                                    "Compliance of Systemic Artery": (1 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Vein": (30 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Artery": (2 / 135, "mL/mmHg")
                                }[param_name]
                baseline_value, unit = baseline_value
                # Format the legend label with the baseline value and unit
                label = f"{param_name} (Baseline: {baseline_value} {unit})"

                ######
                ax.plot(normalized_range, PSA_outputs, label=label)

        ax.set_title('Systemic Arterial Pressure (P_sa) vs. Parameter Variation')
        ax.set_xlabel("Normalized Parameter Value (0.5x to 1.5x)")
        ax.set_ylabel("Systemic Arterial Pressure (P_sa) [mmHg]")
        ax.legend(title="Parameters", loc='upper right')
        ax.grid(True)
    
    elif plot_type == 'OER':
        fig, ax = plt.subplots(figsize=(10, 8))
        normalized_range = np.linspace(0.5, 1.5, 50)  # X-axis values from 0.5 to 1.5

        excluded_params = {
            #"Hemoglobin Concentration"
        }

        # Iterate over each parameter's OER values and plot them
        for param_name, OER_outputs in OERs.items():
            if param_name not in excluded_params:

                baseline_value = {
                                    "Heart Rate": (100, "beats/min"),
                                    "Upper Body Resistance": (45, "Wood Units"),
                                    "Lower Body Resistance": (35, "Wood Units"),
                                    "Pulmonary Resistance": (10, "Wood Units"),
                                    "Systemic Arterial Oxygen Saturation": (0.99, "%"),
                                    "Hemoglobin Concentration": (15, "g/dL"),
                                    "Oxygen Consumption of Upper Body": (70, "mL O2/min"),
                                    "Oxygen Consumption of Lower Body": (50, "mL O2/min"),
                                    # Added missing compliance parameters
                                    "Compliance at Dia": (2 / 100, "mL/mmHg"),  
                                    "Compliance at Sys": (0.01 / 100, "mL/mmHg"),
                                    "Compliance of Systemic Artery": (1 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Vein": (30 / 135, "mL/mmHg"),
                                    "Compliance of Pulmonary Artery": (2 / 135, "mL/mmHg")
                                }[param_name]
                baseline_value, unit = baseline_value
                # Format the legend label with the baseline value and unit
                label = f"{param_name} (Baseline: {baseline_value} {unit})"

                ######
                ax.plot(normalized_range, OER_outputs, label=label)

        ax.set_title('Oxygen Extraction Ratio (OER) vs. Parameter Variation')
        ax.set_xlabel("Normalized Parameter Value (0.5x to 1.5x)")
        ax.set_ylabel("Oxygen Extraction Ratio (OER)")
        ax.legend(title="Parameters", loc='upper right')
        ax.grid(True)


    else:
        return jsonify({'error': 'Invalid plot type'}), 400

    # Convert the plot to a PNG image
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    
    # Encode the image as base64
    plot_data = base64.b64encode(img.getvalue()).decode('utf-8')

    return jsonify({'plot': plot_data})

###

######
@app.route('/generate_custom_plot')
def generate_custom_plot():
    # Capture the query parameters from the frontend
    input1 = request.args.get('input1')
    input2 = request.args.get('input2')
    output = request.args.get('output')

    # Generate a sample plot based on the selected parameters
    # For demonstration, let's create a simple line plot based on the dropdowns
    fig, ax = plt.subplots()

    # Example plot logic: using inputs to vary the plot, replace with your actual logic
    x = [1, 2, 3, 4, 5]
    if input1 == "HR":
        y = [i * 2 for i in x]  # Sample logic based on input1 (Heart Rate)
    elif input1 == "UVR":
        y = [i * 3 for i in x]  # Sample logic based on input1 (Upper Vascular Resistance)
    else:
        y = [i * 4 for i in x]  # Default example for other inputs

    ax.plot(x, y, label=f'{input1} vs {input2}')

    # Customize the plot with labels
    ax.set_title(f"Plot: {input1} vs {input2}")
    ax.set_xlabel(input1)
    ax.set_ylabel(output)

    # Convert the plot to PNG and encode it as Base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Return the plot as a JSON response
    return jsonify({'plot': plot_base64})
######

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
