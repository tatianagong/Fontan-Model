from flask import Flask, render_template, request, jsonify, send_from_directory
from hlhs_model import fun_flows, fun_sat, update_compliance, C_d, C_s, C_sa, C_pv, C_pa
import scipy.optimize
import fontan_plots
import os
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# Ensure you have a folder to save plots
#PLOTS_FOLDER = 'static/plots'
#os.makedirs(PLOTS_FOLDER, exist_ok=True)

# Render the pages
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/slider_page')
def slider():
    return render_template('slider_page.html')

@app.route('/plot_page')
def display_plot():
    return render_template('plot_page.html')

@app.route('/heatmap_page')
def heatmap():
    return render_template('heatmap_page.html')

@app.route('/conditions_page')
def conditions_page():
    return render_template('conditions_page.html')

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
            "Oxygen Consumption of Upper Body",
            "Oxygen Consumption of Lower Body",
            "Hemoglobin Concentration",
            "Systemic Arterial Oxygen Saturation"
        }

        # Iterate over each parameter's CO values and plot them
        for param_name, cardiac_outputs in COs.items():
            if param_name not in excluded_params:
                #####
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
                                    "Compliance at Dia": (np.round(2 / 100,2), "mL/mmHg"),  
                                    "Compliance at Sys": (np.round(0.01 / 100,4), "mL/mmHg"),
                                    "Compliance of Sys Artery Over Vol": (np.round(1 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Vein Over Vol": (np.round(30 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Artery Over Vol": (np.round(2 / 135,3), "mL/mmHg")
                                }[param_name]
                
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
            "Oxygen Consumption of Upper Body",
            "Oxygen Consumption of Lower Body",
            "Hemoglobin Concentration",
            "Systemic Arterial Oxygen Saturation"
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
                                    "Compliance at Dia": (np.round(2 / 100,2), "mL/mmHg"),  
                                    "Compliance at Sys": (np.round(0.01 / 100,4), "mL/mmHg"),
                                    "Compliance of Sys Artery Over Vol": (np.round(1 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Vein Over Vol": (np.round(30 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Artery Over Vol": (np.round(2 / 135,3), "mL/mmHg")
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
            "Oxygen Consumption of Upper Body",
            "Oxygen Consumption of Lower Body",
            "Hemoglobin Concentration",
            "Systemic Arterial Oxygen Saturation"
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
                                    "Compliance at Dia": (np.round(2 / 100,2), "mL/mmHg"),  
                                    "Compliance at Sys": (np.round(0.01 / 100,4), "mL/mmHg"),
                                    "Compliance of Sys Artery Over Vol": (np.round(1 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Vein Over Vol": (np.round(30 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Artery Over Vol": (np.round(2 / 135,3), "mL/mmHg")
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
            "Oxygen Consumption of Upper Body",
            "Oxygen Consumption of Lower Body",
            "Hemoglobin Concentration",
            "Systemic Arterial Oxygen Saturation"
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
                                    "Compliance at Dia": (np.round(2 / 100,2), "mL/mmHg"),  
                                    "Compliance at Sys": (np.round(0.01 / 100,4), "mL/mmHg"),
                                    "Compliance of Sys Artery Over Vol": (np.round(1 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Vein Over Vol": (np.round(30 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Artery Over Vol": (np.round(2 / 135,3), "mL/mmHg")
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
            "Oxygen Consumption of Upper Body",
            "Oxygen Consumption of Lower Body",
            "Hemoglobin Concentration",
            "Systemic Arterial Oxygen Saturation"
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
                                    "Compliance at Dia": (np.round(2 / 100,2), "mL/mmHg"),  
                                    "Compliance at Sys": (np.round(0.01 / 100,4), "mL/mmHg"),
                                    "Compliance of Sys Artery Over Vol": (np.round(1 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Vein Over Vol": (np.round(30 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Artery Over Vol": (np.round(2 / 135,3), "mL/mmHg")
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
                                    "Compliance at Dia": (np.round(2 / 100,2), "mL/mmHg"),  
                                    "Compliance at Sys": (np.round(0.01 / 100,4), "mL/mmHg"),
                                    "Compliance of Sys Artery Over Vol": (np.round(1 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Vein Over Vol": (np.round(30 / 135,3), "mL/mmHg"),
                                    "Compliance of Plm Artery Over Vol": (np.round(2 / 135,3), "mL/mmHg")
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


from fontan_plots import complete_results
import seaborn as sns
from io import BytesIO
@app.route('/generate_custom_plot')
def generate_custom_plot():
    # Capture the query parameters from the frontend
    input1 = request.args.get('input1')
    input2 = request.args.get('input2')
    output = request.args.get('output')

    baseline_values = {
        "HR": 100,    # Heart Rate (beats/min)
        "UVR": 45,    # Upper Vascular Resistance (Wood Units)
        "LVR": 35,    # Lower Vascular Resistance (Wood Units)
        "PVR": 10,    # Pulmonary Vascular Resistance (Wood Units)
        "S_sa": 0.99, # Systemic Artery Saturation (%)
        "Hb": 15,     # Hemoglobin (g/dL)
        "CVO2u": 70,  # Upper Body Oxygen Consumption (mL O2/min)
        "CVO2l": 50,  # Lower Body Oxygen Consumption (mL O2/min)
        "C_d": 2 / 100,  # Compliance at Diastole
        "C_s": 0.01 / 100,  # Compliance at Systole
        "C_sa": 1 / 135,  # Compliance of Systemic Artery/Total Blood Volume
        "C_pv": 30 / 135, # Compliance of Pulmonary Vein/Total Blood Volume
        "C_pa": 2 / 135   # Compliance of Pulmonary Artery/Total Blood Volume
    }

    # Initial guesses for solvers
    z0_flows = [3.0, 1.5, 1.5, 3.0, 90, 5, 10]  # Initial guesses for fun_flows
    z0_sat = [0.8, 0.7, 0.7, 0.7]  # Initial guesses for fun_sat

    # Define value ranges for the two input parameters (±50% of baseline)
    input1_values = np.linspace(baseline_values[input1] * 0.5, baseline_values[input1] * 1.5, 50)
    input2_values = np.linspace(baseline_values[input2] * 0.5, baseline_values[input2] * 1.5, 50)

    # Create a grid for the heatmap
    Z = np.zeros((len(input2_values), len(input1_values)))

    for i, val1 in enumerate(input1_values):
        for j, val2 in enumerate(input2_values):
            # Set parameter values for this iteration, keeping others at baseline
            params = baseline_values.copy()
            params[input1] = val1
            params[input2] = val2

            # Solve for flows and oxygen saturation
            try:
                results = complete_results(
                    params["UVR"], params["LVR"], params["PVR"], params["HR"],
                    params["C_d"], params["C_s"], params["C_sa"], params["C_pv"], params["C_pa"],
                    z0_flows, params["S_sa"], params["CVO2u"], params["CVO2l"], params["Hb"], z0_sat
                )
                
                # Store the result in the grid
                Z[j, i] = results[output]

            except Exception as e:
                Z[j, i] = np.nan  # If the solver fails, store NaN

    # Plot the heatmap
    plt.figure(figsize=(10, 7.5))
    heatmap = sns.heatmap(Z, xticklabels=np.round(input1_values, 1), yticklabels=np.round(input2_values, 1),
                cmap="coolwarm", cbar_kws={'label': output}, linewidths=0.5)
    plt.xlabel(input1, fontsize=14)
    plt.ylabel(input2, fontsize=14)
    plt.title(f"Heatmap of {output}", fontsize = 18)

    # Invert the direction of the y-axis
    plt.gca().invert_yaxis()
    #make ticks readably small
    plt.tick_params(axis='both', which='major', labelsize=7)
    # Customize the color bar labels font size
    cbar = heatmap.collections[0].colorbar
    cbar.ax.tick_params(labelsize=12)  # Adjust the size of the color bar labels
    cbar.set_label(output, fontsize=14)  # Adjust font size of the color bar label

    # Convert plot to PNG and encode as Base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    return jsonify({"plot": plot_base64})

@app.route('/apply_preset')
def apply_preset():
    condition = request.args.get("condition")

    presets = {
        "lowPreload": {
            "HR": 110, "UVR": 45, "LVR": 35, "PVR": 10, "S_sa": 0.99, "Hb": 15, "CVO2u": 70, "CVO2l": 50,
            "C_d": 1/45, "C_s": 1/9000, "C_sa": 2/243, "C_pv": 20/81, "C_pa": 4/243  
        },
        "lungProblem": {
            # no compliance changes
            "HR": 110, "UVR": 45, "LVR": 35, "PVR": 20, "S_sa": 0.99, "Hb": 15, "CVO2u": 70, "CVO2l": 50,
        },
        "heartFailure": {
            "HR": 110, "UVR": 45, "LVR": 35, "PVR": 10, "S_sa": 0.99, "Hb": 15, "CVO2u": 70, "CVO2l": 50,
            "C_d": 0.018, "C_s": 1/9000, "C_sa": 1/150, "C_pv": 1/5, "C_pa": 1/75  
        } 
    }

    if condition in presets:
        preset_values = presets[condition]

        # updates compliances only if they exist in the preset
        if "C_d" in preset_values:
            update_compliance(
                preset_values["C_d"],
                preset_values["C_s"],
                preset_values["C_sa"],
                preset_values["C_pv"],
                preset_values["C_pa"]
            )
    
        # Solve for new vitals using updated values
        param_flows = (
            preset_values["UVR"], preset_values["LVR"], preset_values["PVR"],
            preset_values["HR"], C_d, C_s, C_sa, C_pv, C_pa
        )
        z0_flows = (3.1, 1.5, 1.5, 3.2, 75, 26, 2)

        result_flows = scipy.optimize.fsolve(fun_flows, z0_flows, args=param_flows, full_output=True, xtol=1e-4)
        (Q_v, Q_u, Q_l, Q_p, P_sa, P_pa, P_pv) = result_flows[0]

        param_sat = (Q_p, Q_u, Q_l, preset_values["S_sa"], preset_values["CVO2u"], preset_values["CVO2l"], preset_values["Hb"])
        z0_sat = (0.55, 0.99, 0.55, 0.55)

        result_O2_sat = scipy.optimize.fsolve(fun_sat, z0_sat, args=param_sat, full_output=True, xtol=1e-4)
        (S_pa, S_pv, S_svu, S_svl) = result_O2_sat[0]

        OER = (Q_u * (preset_values["S_sa"] - S_svu) + Q_l * (preset_values["S_sa"] - S_svl)) / ((Q_u + Q_l) * preset_values["S_sa"])

        # Remove backend-only compliance parameters before sending response
        frontend_values = {key: value for key, value in preset_values.items() if not key.startswith("C_")}

        # Add computed vitals to response
        frontend_values.update({
            "Q_v": round(Q_v, 2),
            "Q_u": round(Q_u, 2),
            "Q_l": round(Q_l, 2),
            "Q_p": round(Q_p, 2),
            "P_sa": round(P_sa, 2),
            "P_pa": round(P_pa, 2),
            "P_pv": round(P_pv, 2),
            "S_pa": round(S_pa, 2),
            "S_pv": round(S_pv, 2),
            "S_svu": round(S_svu, 2),
            "S_svl": round(S_svl, 2),
            "OER": round(OER, 2),
        })

        return jsonify(frontend_values)

    return jsonify({"error": "Invalid condition"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
