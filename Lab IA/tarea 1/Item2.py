from functools import lru_cache
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Saltos de escalera o serpientes
LADDERS = {2: 11, 6: 24, 13: 43, 16: 37, 19: 30, 40: 50}
SNAKES  = {18: 10, 23: 11, 36: 15, 41: 22, 46: 25, 49: 17}
JUMP = {**LADDERS, **SNAKES}

def J(k: int) -> int:
    """Devuelve la casilla destino después de aplicar serpientes/escaleras."""
    return JUMP.get(k, k)

@lru_cache(maxsize=None)
def F(i: int) -> np.ndarray:
    """Calcula el vector de transición para un turno empezando en la casilla i"""
    
    if i == 50:
        # Si ya estamos en la meta, el siguiente turno empieza en la casilla 1
        v = np.zeros(50)
        v[0] = 1.0
        return v
    
    base = np.zeros(50, dtype=float)
    
    # Tiradas de 1 a 5: agregamos probabilidad al destino de la casilla
    for r in range(1, 6):
        land = i + r
        if land == 50:
            base[0] += 1.0 / 6.0
            continue
        dest = J(land)
        if dest > 50:
            base[0] += 1.0 / 6.0
            continue  
        elif dest != land:  
            if dest == 50:
                base[0] += 1.0 / 6.0
            else:
                base[dest - 1] += 1.0 / 6.0 
            continue
        base[dest - 1] += 1.0 / 6.0  # Si no hay salto, se queda allí

    # Tirada de 6: turno extra
    t = i + 6
    if t > 50:
        base[0] += 1.0 / 6.0
        return base

    dest6 = J(t)
    if dest6 == 50:
        base[0] += 1.0 / 6.0
    elif dest6 != t:
        if dest6 == 50:
            base[0] += 1.0 / 6.0
        else:
            base[dest6 - 1] += 1.0 / 6.0
    else:
        base += (1/6) * F(dest6)
    
    return base


def build_transition_matrix() -> np.ndarray:
    P = np.zeros((50, 50), dtype=float)
    for i in range(1, 51):
        P[i - 1, :] = F(i)
    # Casilla 50 es terminal: siempre vuelve a 1
    P[49, :] = 0.0
    P[49, 0] = 1.0
    
    return P

def stationary_exact(P: np.ndarray) -> np.ndarray:
    n = P.shape[0]
    A = P.T - np.eye(n)
    b = np.zeros(n)
    A = np.vstack([A, np.ones(n)])
    b = np.append(b, 1.0)
    x, *_ = np.linalg.lstsq(A, b, rcond=None)
    x[np.abs(x) < 1e-15] = 0
    x /= x.sum()
    return x

def stationary_iterative(P: np.ndarray, tol=1e-12, max_iter=100000):
    n = P.shape[0]
    pi = np.zeros(n)
    pi[0] = 1.0

    tray = [pi.copy()]  # trayectoria completa

    for k in range(max_iter):
        pi_next = pi @ P
        pi_next /= pi_next.sum()
        tray.append(pi_next.copy())

        if np.linalg.norm(pi_next - pi, 1) < tol:
            print(f"Convergió en {k} iteraciones")
            return pi_next, np.array(tray)  # devuelvo ambos: vector final + trayectoria

        pi = pi_next

    print("No convergió en el máximo de iteraciones")
    return pi, np.array(tray)

def random_walk(num_pasos=1000, start=1) -> list:
    pos = start
    trayectoria = [pos]

    for _ in range(num_pasos):
        dado = np.random.randint(1, 7)  # número entre 1 y 6
        nueva_pos = pos + dado

        if nueva_pos > 50:
            nueva_pos = pos

        nueva_pos = J(nueva_pos)

        if nueva_pos == 50:
            pos = 1
        else:
            pos = nueva_pos

        trayectoria.append(pos)

    return trayectoria

def expected_duration_hitting(P: np.ndarray) -> float:
    # Q = estados transitorios 1..49
    Q = P[:49, :49]
    I = np.eye(49)
    ones = np.ones(49)
    # Resolvemos h = (I-Q)^(-1) * 1
    h = np.linalg.solve(I - Q, ones)
    return float(h[0])  # Duración esperada desde la casilla 1

def plot_stationary_exact(P: np.ndarray):
    pi = stationary_exact(P)
    estados = np.arange(1, len(pi)+1)

    plt.figure(figsize=(10, 5))
    plt.plot(estados, pi, marker='o', linestyle='-', color='blue')
    plt.title("Distribución estacionaria (Exacta)")
    plt.xlabel("Estado")
    plt.ylabel("Probabilidad")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()

def plot_stationary_iterative(P: np.ndarray):
    pi_final, _ = stationary_iterative(P)
    estados = np.arange(1, len(pi_final)+1)

    plt.figure(figsize=(10, 5))
    plt.plot(estados, pi_final, marker='o', linestyle='-', color='orange')
    plt.title("Distribución estacionaria (Iterativa)")
    plt.xlabel("Estado")
    plt.ylabel("Probabilidad")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()

    print("Vector estacionario (Iterativo):")
    print(pi_final)
    
def plot_random_walk(num_pasos=1000):
    tray = random_walk(num_pasos=num_pasos)

    # Calcular la frecuencia de visitas
    visitas = np.bincount(tray, minlength=max(tray)+1)[1:]  # quitar índice 0
    estados = np.arange(1, len(visitas)+1)
    probs = visitas / visitas.sum()

    # Gráfico lineal similar al exacto
    plt.figure(figsize=(10, 5))
    plt.plot(estados, probs, marker='o', linestyle='-', color='purple')
    plt.title("Distribución aproximada por Random Walk")
    plt.xlabel("Estado")
    plt.ylabel("Probabilidad estimada")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()
    
def visits_vector(P: np.ndarray) -> np.ndarray:
    I = np.eye(49)
    N = np.linalg.inv(I - P[:49, :49])   # Matriz fundamental

    visits = N[0, :]
    return visits

def plot_visits(visits: np.ndarray):
    plt.figure(figsize=(10,5))
    plt.bar(range(1, 50), visits, color="skyblue", edgecolor="black")
    plt.xlabel("Casilla")
    plt.ylabel("Turnos esperados en la casilla")
    plt.title("Vector de visitas promedio por partida (casillas 1-49)")
    plt.show()

if __name__ == "__main__":
    P = build_transition_matrix()
    df_P = pd.DataFrame(P)
    df_P.to_csv('matriz_transicion.csv', sep=',', header=True, index=True)
    pi_exact = stationary_exact(P)

    pi_exact = stationary_exact(P)
    print("<--------------Vector estacionario (exacto)-------------->")
    print(pi_exact)
    df_pi = pd.DataFrame(pi_exact)
    df_pi.to_csv('vector_pi.csv', sep=',', header=True, index=True)
    plot_stationary_exact(df_P)

    print("<--------------Vector estacionario (iterativo)-------------->")
    pi_iter, tray = stationary_iterative(P)
    print(pi_iter)
    print("Diferencia entre ambos m茅todos:", np.linalg.norm(pi_exact - pi_iter, 1))
    plot_stationary_iterative(P)

    print("<--------------Random Walk-------------->")
    tray = random_walk(100000, start=1)
    conteo = Counter(tray)
    dist_aprox = np.array([conteo[i] for i in range(1, 51)], dtype=float)
    dist_aprox /= dist_aprox.sum()
    print(dist_aprox)
    print("Diferencia entre ambos m茅todos:", np.linalg.norm(pi_iter - dist_aprox, 1))
    plot_random_walk(num_pasos=5000)

    print("<--------------Duraci贸n esperada del juego-------------->")
    duracion = expected_duration_hitting(P)
    print(f"Duraci贸n esperada del juego: {duracion:.2f} turnos")

    print("<--------------Vector de visitas promedio por partida-------------->")
    visits = visits_vector(P)
    df_v = pd.DataFrame(visits)
    df_v.to_csv('vector_visitas.csv', sep=',', header=True, index=True)
    plot_visits(visits)