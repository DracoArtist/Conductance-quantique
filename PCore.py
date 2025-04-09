import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
from MathCore import G0  # Assurez-vous que G0 est défini correctement dans MathCore
#from Graphics import Graphics  # Si nécessaire pour vos graphiques spécifiques

# --- Paramètres expérimentaux communs ---
source_voltage = 2.5
resistance = 20000

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
    Vwire = -np.array(data_file["Voltage_wire"])
    
    # Définition de la fonction de calcul de la tension théorique
    def expected_plateau_voltage(n: int, Rres: float, V=source_voltage, R=resistance):
        return V / (1 + R / (1/(n * G0) + Rres))
    
    # Calcul des plages attendues pour n=1 à 5
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
# ETAPE 2 : Détection des plateaux et optimisation de Rres
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

def expected_plateau_voltage(n: int, Rres: float, V=source_voltage, R=resistance):
    """
    Calcule la tension théorique aux bornes des fils d'or pour un plateau de conductance nG0.
    """
    return V / (1 + R / (1/(n * G0) + Rres))

def optimize_Rres(plateaus, V=source_voltage, R=resistance, n_range=(1, 6)):
    """
    Balaye Rres de 0 à 600 ohms pour déterminer la valeur qui minimise l'erreur globale
    sur tous les plateaux.
    Retourne le meilleur Rres et la liste des résultats.
    """
    Rres_candidates = np.linspace(0, 600, 601*10)  # par pas de 1 ohms
    results_Rres = []
    for Rres_val in Rres_candidates:
        global_error = 0
        for idx, plateau_data in plateaus.items():
            mean_voltage = np.mean(plateau_data)
            best_error = np.inf
            for n_candidate in range(n_range[0], n_range[1]):
                v_theo = expected_plateau_voltage(n_candidate, Rres_val, V, R)
                error = abs(mean_voltage - v_theo)
                if error < best_error:
                    best_error = error
            global_error += best_error
        results_Rres.append((Rres_val, global_error))
    best_Rres, best_global_error = min(results_Rres, key=lambda x: x[1])
    print(f"Meilleur Rres : {best_Rres:.1f} ohms avec une erreur globale de {best_global_error:.4f}")
    
    # Visualisation de l'erreur globale en fonction de Rres
    Rres_vals, global_errors = zip(*results_Rres)
    plt.figure(figsize=(10,6))
    plt.plot(Rres_vals, global_errors, marker='o')
    plt.title("Erreur globale en fonction de Rres")
    plt.xlabel("Rres (ohms)")
    plt.ylabel("Erreur globale")
    plt.grid(False)
    plt.show()
    
    return best_Rres, results_Rres

def assign_plateau_n(plateaus, best_Rres, V=source_voltage, R=resistance, n_range=(1, 6)):
    """
    Pour chaque plateau, attribue le n (de 1 à 5) pour lequel la tension théorique calculée avec best_Rres
    est la plus proche de la tension moyenne mesurée.
    Retourne une liste de dictionnaires contenant start_index, mean_voltage, plateau_n et l'erreur.
    """
    plateau_results = []
    for idx, plateau_data in plateaus.items():
        mean_voltage = np.mean(plateau_data)
        best_n = None
        best_error = np.inf
        for n_candidate in range(n_range[0], n_range[1]):
            v_theo = expected_plateau_voltage(n_candidate, best_Rres, V, R)
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
# ETAPE 3 : Calcul de Rinconnue à partir des résultats des plateaux
# =============================================================================

def compute_Rinconnue(V_source=source_voltage, Rres_optimal=300):
    """
    Lit le CSV plateau_results_n.csv, calcule Rinconnue pour chaque plateau et exporte le résultat dans un CSV.
    La formule utilisée est :
        Rinconnue = (V_source / mean_voltage - 1) * (1/(n * G0) + Rres_optimal)
    """
    df_plateaux = pd.read_csv("plateau_results_n.csv")
    
    def calc_Rinconnue(row):
        return (V_source / row["mean_voltage"] - 1) * (1/(row["plateau_n"] * G0) + Rres_optimal)
    
    df_plateaux["Rinconnue"] = df_plateaux.apply(calc_Rinconnue, axis=1)
    
    R_mean = df_plateaux["Rinconnue"].mean()
    R_std = df_plateaux["Rinconnue"].std()
    print(f"Moyenne de Rinconnue : {R_mean:.4f} Ω")
    print(f"Écart-type de Rinconnue : {R_std:.4f} Ω")
    
    df_plateaux.to_csv("Rinconnue_results.csv", index=False)
    print("Les résultats de Rinconnue ont été exportés dans Rinconnue_results.csv")
    
    # Visualisation de l'histogramme de Rinconnue
    plt.figure(figsize=(10,6))
    plt.hist(df_plateaux["Rinconnue"], bins=10, edgecolor='black')
    plt.title("Histogramme de Rinconnue")
    plt.xlabel("Rinconnue (Ω)")
    plt.ylabel("Fréquence")
    plt.grid(True)
    plt.show()
    
    return df_plateaux

# =============================================================================
# Fonction principale : exécute l'ensemble du pipeline
# =============================================================================

def main():
    # Étape 1 : Prétraitement et filtrage
    process_acquisition_data("acquisition_data_5.csv", "P_filtered_data_5.csv")
    
    # Étape 2 : Détection des plateaux et optimisation de Rres
    plateaus = detect_plateaus("P_filtered_data_5.csv", points_per_plateau=5, max_diff=1e-2)
    best_Rres, _ = optimize_Rres(plateaus, V=source_voltage, R=resistance, n_range=(1,6))
    plateau_results = assign_plateau_n(plateaus, best_Rres, V=source_voltage, R=resistance, n_range=(1,6))
    
    # Étape 3 : Calcul de Rinconnue
    # Ici, nous utilisons best_Rres trouvé précédemment comme Rres_optimal
    compute_Rinconnue(V_source=source_voltage, Rres_optimal=best_Rres)

if __name__ == "__main__":
    main()
