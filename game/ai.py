import random
import pickle
import os

# Definimos constantes para el aprendizaje
ARCHIVO_Q_TABLE = "conocimiento_gato.pkl"

class QAgent:
    def __init__(self, alpha=0.5, gamma=0.9, epsilon=1.0):
        """
        Inicializa al agente (El Gato).
        :param alpha: Tasa de aprendizaje (0 = no aprende nada, 1 = olvida lo viejo por lo nuevo).
        :param gamma: Factor de descuento (importancia del futuro).
        :param epsilon: Probabilidad de explorar (1.0 = 100% aleatorio al inicio).
        """
        self.q_table = {}  # Aquí se guarda la "Memoria" del gato
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995 # Velocidad a la que deja de ser curioso
        
        # Intentamos cargar cerebro previo si existe
        self.cargar_conocimiento()

    def obtener_estado(self, tablero):
        """Convierte la lista del tablero en una Tupla (inmutable) para usarla de clave."""
        return tuple(tablero)

    def obtener_accion(self, tablero, movimientos_posibles, en_entrenamiento=True):
        """
        Decide qué movimiento hacer usando la estrategia Epsilon-Greedy.
        """
        estado = self.obtener_estado(tablero)

        # 1. Fase de EXPLORACIÓN (Curiosidad)
        # Si estamos entrenando y sale un número menor a epsilon, elegimos al azar.
        if en_entrenamiento and random.uniform(0, 1) < self.epsilon:
            return random.choice(movimientos_posibles)

        # 2. Fase de EXPLOTACIÓN (Usar conocimiento)
        # Si el estado no existe en memoria, inicializamos con ceros
        if estado not in self.q_table:
            self.q_table[estado] = {mov: 0.0 for mov in movimientos_posibles}

        # Buscamos el movimiento con el valor más alto en la tabla Q para este estado
        # Si hay varios empates, elige uno al azar entre los mejores
        valores_movimientos = self.q_table[estado]
        
        # Filtramos solo los movimientos válidos actuales
        valores_validos = {m: valores_movimientos.get(m, 0.0) for m in movimientos_posibles}
        
        max_valor = max(valores_validos.values())
        mejores_movimientos = [m for m, v in valores_validos.items() if v == max_valor]
        
        return random.choice(mejores_movimientos)

    def aprender(self, estado_actual, accion, recompensa, estado_siguiente, movimientos_siguientes, termino_juego):
        """
        Aplica la ECUACIÓN DE BELLMAN para actualizar la Q-Table.
        """
        estado_t = self.obtener_estado(estado_actual)
        estado_t1 = self.obtener_estado(estado_siguiente)

        # Asegurar que los estados existan en la tabla
        if estado_t not in self.q_table:
            self.q_table[estado_t] = {accion: 0.0} # Se expandirá luego si hay más acciones
        if estado_t1 not in self.q_table:
            # Inicializamos el siguiente estado con ceros para sus posibles acciones
            self.q_table[estado_t1] = {m: 0.0 for m in movimientos_siguientes}

        # Valor actual (Viejo)
        q_actual = self.q_table[estado_t].get(accion, 0.0)

        # Valor futuro máximo (El mejor movimiento que podría hacer después)
        if termino_juego:
            max_q_futuro = 0.0 # No hay futuro si el juego terminó
        else:
            # Buscamos el max valor entre las opciones del siguiente estado
            # Nota: Si movimientos_siguientes está vacío, max_q es 0
            vals_siguientes = [self.q_table[estado_t1].get(m, 0.0) for m in movimientos_siguientes]
            max_q_futuro = max(vals_siguientes) if vals_siguientes else 0.0

        # --- ECUACIÓN DE BELLMAN ---
        # Q(s,a) = Q(s,a) + alpha * (Recompensa + gamma * max(Q(s')) - Q(s,a))
        nuevo_q = q_actual + self.alpha * (recompensa + (self.gamma * max_q_futuro) - q_actual)
        
        # Actualizamos la tabla
        self.q_table[estado_t][accion] = nuevo_q

    def reducir_epsilon(self):
        """Reduce la curiosidad del gato poco a poco después de cada partida."""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def guardar_conocimiento(self):
        """Guarda la Q-Table en un archivo."""
        try:
            with open(ARCHIVO_Q_TABLE, "wb") as f:
                pickle.dump(self.q_table, f)
            print(f"Cerebro guardado: {len(self.q_table)} estados aprendidos.")
        except Exception as e:
            print(f"Error guardando cerebro: {e}")

    def cargar_conocimiento(self):
        """Carga la Q-Table desde un archivo."""
        if os.path.exists(ARCHIVO_Q_TABLE):
            try:
                with open(ARCHIVO_Q_TABLE, "rb") as f:
                    self.q_table = pickle.load(f)
                print(f"Cerebro cargado con éxito. Estados conocidos: {len(self.q_table)}")
                # Si cargamos un cerebro, bajamos epsilon porque ya sabe jugar
                self.epsilon = 0.2 
            except Exception as e:
                print(f"Error cargando cerebro: {e}")
                self.q_table = {}

# Instancia global para usar en main.py
agente_global = QAgent()
