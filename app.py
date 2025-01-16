from flask import Flask, render_template, request, jsonify
from hlhs_model import fun_flows, fun_sat, C_d, C_s, C_sa, C_pv, C_pa
import scipy.optimize

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
