import random
import os
import json
import ast # Para convertir el string "('X',...)" de vuelta a tupla

# --- CAMBIO IMPORTANTE: Ahora la extensión oficial es .json ---
ARCHIVO_Q_TABLE = "conocimiento_gato.json"

class QAgent:
    def __init__(self, alpha=0.5, gamma=0.9, epsilon=1.0):
        """
        Inicializa al agente (El Gato).
        """
        self.q_table = {}  # Memoria
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995 
        
        # Intentamos cargar cerebro previo si existe
        self.cargar_conocimiento()

    def obtener_estado(self, tablero):
        """Convierte la lista del tablero en una Tupla (inmutable)."""
        return tuple(tablero)

    def obtener_accion(self, tablero, movimientos_posibles, en_entrenamiento=True):
        """
        Decide qué movimiento hacer usando Epsilon-Greedy.
        """
        estado = self.obtener_estado(tablero)

        # 1. Fase de EXPLORACIÓN (Curiosidad)
        if en_entrenamiento and random.uniform(0, 1) < self.epsilon:
            return random.choice(movimientos_posibles)

        # 2. Fase de EXPLOTACIÓN (Cerebro)
        if estado not in self.q_table:
            # Si no conoce el estado, asume valor 0 para todo
            self.q_table[estado] = {mov: 0.0 for mov in movimientos_posibles}

        valores_movimientos = self.q_table[estado]
        
        # Filtrar solo movimientos válidos
        valores_validos = {m: valores_movimientos.get(m, 0.0) for m in movimientos_posibles}
        
        # Elegir el mejor (o uno de los mejores si hay empate)
        max_valor = max(valores_validos.values())
        mejores_movimientos = [m for m, v in valores_validos.items() if v == max_valor]
        
        return random.choice(mejores_movimientos)

    def aprender(self, estado_actual, accion, recompensa, estado_siguiente, movimientos_siguientes, termino_juego):
        """
        Aplica la ECUACIÓN DE BELLMAN.
        """
        estado_t = self.obtener_estado(estado_actual)
        estado_t1 = self.obtener_estado(estado_siguiente)

        if estado_t not in self.q_table:
            self.q_table[estado_t] = {accion: 0.0}
        if estado_t1 not in self.q_table:
            self.q_table[estado_t1] = {m: 0.0 for m in movimientos_siguientes}

        q_actual = self.q_table[estado_t].get(accion, 0.0)

        if termino_juego:
            max_q_futuro = 0.0
        else:
            vals_siguientes = [self.q_table[estado_t1].get(m, 0.0) for m in movimientos_siguientes]
            max_q_futuro = max(vals_siguientes) if vals_siguientes else 0.0

        # Ecuación de Bellman
        nuevo_q = q_actual + self.alpha * (recompensa + (self.gamma * max_q_futuro) - q_actual)
        self.q_table[estado_t][accion] = nuevo_q

    def reducir_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # -----------------------------------------------------------
    # CORRECCIÓN DE MERRY AQUI ABAJO
    # -----------------------------------------------------------
    
    def guardar_conocimiento(self):
        """Guarda la Q-Table en JSON puro."""
        try:
            # Convertimos las claves (Tuplas) a String para que JSON no llore
            data_para_json = {str(k): v for k, v in self.q_table.items()}
            
            with open(ARCHIVO_Q_TABLE, "w") as f:
                json.dump(data_para_json, f, indent=4)
                
            print(f"Cerebro guardado en {ARCHIVO_Q_TABLE} ({len(self.q_table)} estados).")
        except Exception as e:
            print(f" Error guardando cerebro: {e}")

    def cargar_conocimiento(self):
        """Carga la Q-Table desde JSON y reconstruye las tuplas."""
        if os.path.exists(ARCHIVO_Q_TABLE):
            try:
                with open(ARCHIVO_Q_TABLE, "r") as f:
                    data_cargada = json.load(f)
                
                self.q_table = {}
                for k_str, v in data_cargada.items():
                    # 1. Recuperar la Tupla del estado: "('X', ' ', ...)" -> ('X', ' ', ...)
                    key_tupla = ast.literal_eval(k_str)
                    
                    # 2. Recuperar los movimientos como Enteros: "4": 0.5 -> 4: 0.5
                    valores_int = {int(m): valor for m, valor in v.items()}
                    
                    self.q_table[key_tupla] = valores_int
                    
                print(f"Cerebro cargado: {len(self.q_table)} estados aprendidos.")
                
                # IMPORTANTE: Si ya sabe jugar, bajamos la curiosidad a 0 para que juegue serio
                self.epsilon = 0.0 
                
            except Exception as e:
                print(f"Error cargando cerebro JSON: {e}")
                self.q_table = {}
        else:
            print(" No hay cerebro guardado. Se inicia desde cero.")

# Instancia global
agente_global = QAgent()