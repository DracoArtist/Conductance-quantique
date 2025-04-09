from Acquisition import Acquisition
from Graphics import Graphics
from MathCore import compute_conductance
import pandas as pd
from PSearch import Search
import numpy as np
import matplotlib.pyplot as plt

"""
----------------------------------------------------------------------------------------------
Declaring general variables
----------------------------------------------------------------------------------------------
"""

"""
NImyDAQ_caracteristics:
Range width corresponds to the analog input range used. The NimyDAQ has either +- 2V or +- 10V,
    corresponding with a width of 4 or 20 V, respectively.
Number of bits is given by the manifacturer
"""
Range_width = 4
Number_of_bits = 16

"""
----------------------------------------------------------------------------------------------
Acquiring data
----------------------------------------------------------------------------------------------
"""

"""
Acquires voltage across gold wire and source channel.

Arguments:
    - gold_channel: the voltage across the gold wire
    - source_channel: the voltage across the whole circuit (so the output of the source)
"""

# acquisition = Acquisition(
#     gold_channel = "DAQ_team_3_PHS2903/ai0",  # Across the gold wires
#     source_channel = "DAQ_team_3_PHS2903/ai1",  # Across the source
#     samples_by_second = 100000,
#     # number_of_samples_per_channel = 2,
#     export_target = r"acquisition_data_1.csv"
# )

# acquisition.continuous_acquisition()
# acquisition.export_to_csv()

"""
----------------------------------------------------------------------------------------------
Create a histogram to better visualise the data
----------------------------------------------------------------------------------------------
"""

data_file = pd.read_csv(r"acquisition_data_1.csv")


"""
Histogram of the voltage. V will be the instance of the Graphics class that will compute graphics with voltage
"""

V = Graphics(
    data=data_file['Voltage_wire'],
)

V.create_histogram(
    bin_width=3.24*10**(-4)
)

V.graph_histogram(
    title="Histogram de la tension",
    ylabel="count (log)",
    xlabel="value",
    log=True
)

V.regular_plot(
    title="Tension mesuré",
    ylabel="temps (10 microsecondes)",
    xlabel="value",
    # log=True
)

Vwire = np.array(data_file['Voltage_wire'])

search = Search(
    data_to_search= Vwire
)

plateaus = search.find_plateaus_diff(
    plateau_lenght=5,
    max_diff=0.01
)

plt.plot(
    [i for i, _ in enumerate(Vwire)],
    Vwire,
    'o',
    markersize=2.5,
    color='black')

for index in plateaus.keys():
    data = plateaus[index]
    plt.plot([float(index) + i for i, _ in enumerate(data)], data, 'o', markersize=3.5),


plt.title("Les différents plateaux identifiés")
plt.ylabel("Tension (V)")
plt.xlabel("Temps (10 $\mu$s)")
plt.grid(which='both')
plt.show()