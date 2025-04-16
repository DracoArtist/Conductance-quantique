import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df = pd.read_csv(r"prise_mesure_lab\filor_vibration1.csv", usecols=[3,4], names=['colA', 'colB'])
# fig, ax = plt.subplots(2)

# ax[0].plot([i for i, _ in enumerate(df['colA'])], df['colA'], 'o', markersize=1, color='blue')
plt.plot([i for i, _ in enumerate(df['colB'])], np.array(df['colB']) - min(df['colB']), 'o', markersize=1, color='orange')

plt.show()

