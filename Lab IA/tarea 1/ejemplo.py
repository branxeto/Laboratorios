import numpy as np
import pandas as pd

print("Librerías importadas correctamente.")

NUM_CASILLAS = 50
CARAS_DADO = 6

escaleras = {
    2: 11,
    13: 43,
    6: 24,
    16: 37,
    19: 30,
    40: 50
}

serpientes = {
    23: 11,
    41: 22,
    46: 25,
    36: 15,
    49: 17,
    18: 10
}

saltos = {**escaleras, **serpientes}

print("Escaleras:", escaleras)
print("Serpientes:", serpientes)

P = np.zeros((NUM_CASILLAS, NUM_CASILLAS))

# 1. Cálculo de Transiciones Base
for i in range(1, NUM_CASILLAS + 1):
    for d in range(1, CARAS_DADO + 1):
        prob_dado = 1 / CARAS_DADO
        pos_temp = i + d

        if pos_temp > NUM_CASILLAS:
            casilla_final = i
            P[i - 1, casilla_final - 1] += prob_dado
            continue

        if pos_temp == NUM_CASILLAS:
            casilla_final = 1
            P[i - 1, casilla_final - 1] += prob_dado
            continue

        hay_salto = pos_temp in saltos
        casilla_destino = saltos.get(pos_temp, pos_temp)

        if casilla_destino == 50:
            casilla_destino = 1

        if d == 6 and hay_salto:
            P[i - 1, casilla_destino - 1] += prob_dado
        elif d < 6:
            P[i - 1, casilla_destino - 1] += prob_dado

# 2. Solución a la Regla "Repetir Turno con un Número 6 en el Dado"
for _ in range(100):
    P_old = P.copy()
    for i in range(1, NUM_CASILLAS + 1):
        pos_temp_6 = i + 6
        if pos_temp_6 <= NUM_CASILLAS and pos_temp_6 not in saltos:
            P[i - 1, :] = P_old[i - 1, :] + (1/6) * P_old[pos_temp_6 - 1, :]
P[49, :] = 0.0
P[49, 0] = 1.0


# 3. Normalización y Exportación
row_sums = P.sum(axis=1, keepdims=True)
P = np.divide(P, row_sums, out=np.zeros_like(P), where=row_sums!=0)

df_P = pd.DataFrame(P, index=range(1, NUM_CASILLAS + 1), columns=range(1, NUM_CASILLAS + 1))
df_P.to_csv('matriz_transicion.csv')

print("Matriz de Transición P (50x50) construida.")
print("Forma de la matriz:", P.shape)
print(f"Suma de la primera fila: {P[0, :].sum():.2f}")
print("\nLa matriz se ha guardado en 'matriz_transicion.csv'")