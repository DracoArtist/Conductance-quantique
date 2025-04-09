import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
from scipy.optimize import curve_fit
from MathCore import G0  # Assurez-vous que G0 est défini correctement dans MathCore
#from Graphics import Graphics  # Si nécessaire pour vos graphiques spécifiques

# --- Paramètres expérimentaux communs ---
source_voltage = 2.5
# On ne fixe plus R, on va l'estimer via l'ajustement

# =============================================================================
# ETAPE 1 : Prétraitement et filtrage des données brutes
# =============================================================================

def process_acquisition_data(acquisition_file="acquisition_data.csv", output_file="P_filtered_data.csv"):
    """
    Lit le fichier d'acquisition, calcule les plages de tension attendues,
    filtre les points et exporte le résultat dans un CSV.
    """
    # Lecture des données brutes
    data_file = pd.read_csv(acquisition_file)
    # On inverse le signe de la tension, comme dans votre code
    Vwire = np.array(data_file["Voltage_wire"])
    
    # Définition de la fonction de calcul de la tension théorique
    def expected_plateau_voltage(n: int, Rres: float, V=source_voltage, R=20000):
        return V / (1 + R / (1/(n * G0) + Rres))
    
    # Calcul des plages attendues pour n=1 à 5 (on garde ici R=20000 pour le filtrage)
    expected_plateau_voltages_min = np.array([expected_plateau_voltage(n=i+1, Rres=0) for i in range(5)])
    expected_plateau_voltages_max = np.array([expected_plateau_voltage(n=i+1, Rres=600) for i in range(5)])
    
    print("Tensions théoriques minimales:", expected_plateau_voltages_min)
    print("Tensions théoriques maximales:", expected_plateau_voltages_max)
    print("Update: expected plateaus computed")
    
    # Filtrage des points qui tombent dans l'une des plages attendues
    filtered_data = []
    for voltage in Vwire:
        in_range = False
        for i in range(len(expected_plateau_voltages_max)):
            if expected_plateau_voltages_min[i] <= voltage <= expected_plateau_voltages_max[i]:
                in_range = True
                break
        if in_range:
            filtered_data.append(voltage)
    
    print("Update: data filtered")
    # Sauvegarde des données filtrées
    df = pd.DataFrame(filtered_data, columns=["Voltage_wire"])
    df.to_csv(output_file, index=False)
    print("Update: filtered data exported dans", output_file)
    
    # Visualisation des données filtrées avec les coupures
    index_range = list(range(len(filtered_data)))
    x_range = np.linspace(0, max(index_range), 10)
    plt.figure(figsize=(10,6))
    plt.plot(index_range, filtered_data, 'o', markersize=1, label="Données filtrées")
    for i in range(len(expected_plateau_voltages_max)):
        plt.plot(x_range, [expected_plateau_voltages_min[i]] * len(x_range),
                 color=(255/255, (189 - i*85/5)/255, (136 - i*136/5)/255),
                 label=f"Min voltage for n={i+1}")
        plt.plot(x_range, [expected_plateau_voltages_max[i]] * len(x_range),
                 color=((255 - 150*i/5)/255, 0, 0),
                 label=f"Max voltage for n={i+1}")
    plt.title("Filtered voltage measures and cutoff values")
    plt.xlabel("Index")
    plt.ylabel("Voltage (V)")
    plt.legend(loc='best')
    plt.grid(False)
    plt.show()

# =============================================================================
# ETAPE 2 : Détection des plateaux et attribution de n
# =============================================================================

def detect_plateaus(filtered_data_file="P_filtered_data.csv", points_per_plateau=5, max_diff=1e-2):
    """
    Lit le fichier filtré et détecte les plateaux en fonction des différences entre points.
    Retourne un dictionnaire dont la clé est l'indice de départ et la valeur est une série de points.
    """
    data_file = pd.read_csv(filtered_data_file)
    Vwire = data_file["Voltage_wire"]
    
    plateaus = {}
    on_plateau = False
    index_start = 0
    diff = np.diff(Vwire)
    
    for i in range(len(diff)):
        if abs(diff[i]) <= max_diff and not on_plateau:
            on_plateau = True
            index_start = i
        if abs(diff[i]) > max_diff and on_plateau:
            on_plateau = False
            if i - index_start < points_per_plateau:
                continue
            plateaus[index_start] = Vwire[index_start:i]
    
    # Affichage pour vérification
    for idx in plateaus.keys():
        print(f"Plateau démarre à l'indice {idx}:")
        print(plateaus[idx])
    
    # Visualisation des plateaux
    plt.figure(figsize=(10,6))
    for idx, plateau in plateaus.items():
        indexes = plateau.index.tolist()
        plt.plot(indexes, plateau, 'o', markersize=1)
    plt.title("Plateaux détectés")
    plt.xlabel("Index")
    plt.ylabel("Voltage (V)")
    plt.grid(False)
    plt.show()
    
    # Visualisation des tensions moyennes par plateau
    plateau_values = [np.mean(plateaus[key]) for key in plateaus.keys()]
    plt.figure(figsize=(10,6))
    plt.plot(range(len(plateau_values)), plateau_values, 'o', markersize=3)
    plt.title("Tension moyenne de chaque plateau")
    plt.xlabel("Plateau (numéro)")
    plt.ylabel("Voltage moyen (V)")
    plt.grid(False)
    plt.show()
    
    return plateaus

def expected_plateau_voltage(n: int, Rres: float, V=source_voltage, R=20000):
    """
    Calcule la tension théorique aux bornes des fils d'or pour un plateau de conductance nG0.
    (Ici, R=20000 est utilisé uniquement pour l'attribution de n.)
    """
    return V / (1 + R / (1/(n * G0) + Rres))

def assign_plateau_n(plateaus, dummy_Rres, V=source_voltage, R=20000, n_range=(1, 6)):
    """
    Pour chaque plateau, attribue le n (de 1 à 5) pour lequel la tension théorique
    (calculée avec dummy_Rres, par exemple 0) est la plus proche de la tension moyenne mesurée.
    Retourne une liste de dictionnaires contenant start_index, mean_voltage, plateau_n et l'erreur.
    """
    plateau_results = []
    for idx, plateau_data in plateaus.items():
        mean_voltage = np.mean(plateau_data)
        best_n = None
        best_error = np.inf
        for n_candidate in range(n_range[0], n_range[1]):
            v_theo = expected_plateau_voltage(n_candidate, dummy_Rres, V, R)
            error = abs(mean_voltage - v_theo)
            if error < best_error:
                best_error = error
                best_n = n_candidate
        plateau_results.append({
            "start_index": idx,
            "mean_voltage": mean_voltage,
            "plateau_n": best_n,
            "error": best_error
        })
    # Sauvegarde dans un CSV
    df_results = pd.DataFrame(plateau_results)
    df_results.to_csv("plateau_results_n.csv", index=False)
    print("Les résultats ont été exportés dans plateau_results_n.csv")
    return plateau_results

# =============================================================================
# NOUVELLE ETAPE : Estimation de R et R_res par ajustement du modèle théorique
# =============================================================================

def estimate_R_parameters(plateau_csv="plateau_results_n.csv", V_source=source_voltage):
    """
    Estime les valeurs de R et R_res en ajustant le modèle théorique aux données mesurées.
    
    Le modèle théorique est :
         V_plateau(n) = V_source / (1 + R / (1/(n * G0) + R_res))
         
    On utilise les valeurs de n (plateau_n) et la tension moyenne (mean_voltage) issues du CSV.
    """
    df = pd.read_csv(plateau_csv)
    # Extraction des valeurs de plateau_n et des tensions moyennes
    n_vals = df["plateau_n"].values.astype(float)
    V_plateau = df["mean_voltage"].values.astype(float)
    
    # Définition du modèle de tension théorique
    def model(n, R, R_res):
        return V_source / (1 + R / (1/(n * G0) + R_res))
    
    # Valeurs initiales pour l'ajustement (à ajuster selon vos connaissances)
    initial_guess = [20000, 236.9]  # Exemple : 20kΩ et 236.9Ω
    
    # Ajustement par curve_fit
    popt, pcov = curve_fit(model, n_vals, V_plateau, p0=initial_guess)
    R_fit, R_res_fit = popt
    # Calcul des incertitudes (erreur standard) sur les paramètres
    perr = np.sqrt(np.diag(pcov))
    
    print(f"Estimation : R = {R_fit:.2f} Ω ± {perr[0]:.2f} Ω, R_res = {R_res_fit:.2f} Ω ± {perr[1]:.2f} Ω")
    
    # Optionnel : tracer le modèle ajusté par rapport aux données mesurées
    n_fit = np.linspace(min(n_vals), max(n_vals), 100)
    V_fit = model(n_fit, R_fit, R_res_fit)
    plt.figure(figsize=(8,6))
    plt.plot(n_vals, V_plateau, 'o', label="Données mesurées")
    plt.plot(n_fit, V_fit, '-', label="Modèle ajusté")
    plt.xlabel("Plateau n")
    plt.ylabel("Tension moyenne (V)")
    plt.title("Ajustement du modèle théorique")
    plt.legend()
    plt.show()
    
    return R_fit, R_res_fit


# =============================================================================
# Fonction principale : exécute l'ensemble du pipeline
# =============================================================================

def main():
    # Étape 1 : Prétraitement et filtrage
    process_acquisition_data("acquisition_data_5.csv", "P_filtered_data_5.csv")
    
    # Étape 2 : Détection des plateaux et attribution de n
    plateaus = detect_plateaus("P_filtered_data_5.csv", points_per_plateau=5, max_diff=1e-2)
    # Pour l'attribution de n, on passe une valeur fictive pour R_res (ici 0)
    plateau_results = assign_plateau_n(plateaus, dummy_Rres=0, V=source_voltage, R=20000, n_range=(1,6))
    
    # Nouvelle étape : estimation de R et R_res par ajustement du modèle
    R_est, R_res_est = estimate_R_parameters("plateau_results_n_5.csv", V_source=source_voltage)
    
if __name__ == "__main__":
    main()
