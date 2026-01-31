import random
import os
import json
import ast
import time
from copy import deepcopy
from game.logic import LogicaTresRayas

# =============================================================================
#  MÓDULO DE INTELIGENCIA ARTIFICIAL (CEREBRO DEL AGENTE)
# =============================================================================
#  Función Principal:
#  Este archivo contiene dos paradigmas de IA:
#  1. Q-Learning (Reinforcement Learning): Un agente que aprende por experiencia
#     usando la Ecuación de Bellman y una Tabla Q (Memoria).
#  2. Minimax (Algorítmico): Un algoritmo recursivo de búsqueda exhaustiva 
#     usado como "Benchmark" o rival perfecto para validar el aprendizaje.
# =============================================================================

ARCHIVO_Q_TABLE = "conocimiento_gato.json"

class QAgent:
    def __init__(self, alpha=0.5, gamma=0.9, epsilon=1.0):
        """
        Inicializa al agente de Aprendizaje por Refuerzo (Q-Learning).
        
        Ref PDF 'Q-Learning De Cero a Maestro' (Pág. 7 - Hiperparámetros):
        :param alpha (α): Tasa de Aprendizaje. Determina qué tanto aceptamos la nueva información 
                          sobre la vieja. (0 = nada, 1 = todo).
        :param gamma (γ): Factor de Descuento. Determina la importancia de las recompensas futuras 
                          (Visionario vs Miope).
        :param epsilon (ε): Tasa de Exploración. Probabilidad de tomar una acción aleatoria 
                            para descubrir nuevas estrategias.
        """
        # Ref PDF (Pág. 5): "La Estructura de Memoria: La Tabla Q".
        # Es una Lookup Table que mapea Estados (S) -> Valores de Acciones (Q).
        self.q_table = {} 
        
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995 
        
        self.cargar_conocimiento()

    def obtener_estado(self, tablero):
        """Convierte el tablero (Lista) en una Tupla (Inmutable) para usarla como clave en el Diccionario (Tabla Q)."""
        return tuple(tablero)

    def obtener_accion(self, tablero, movimientos_posibles, en_entrenamiento=True):
        """
        Decide la siguiente jugada basándose en la Política Epsilon-Greedy.
        Ref PDF (Pág. 8): "El Dilema: Exploración vs. Explotación".
        """
        estado = self.obtener_estado(tablero)

        # ---------------------------------------------------------
        # 1. FASE DE EXPLORACIÓN (Curiosidad)
        # ---------------------------------------------------------
        # Si el número aleatorio es menor que Epsilon, el agente "Explora" (prueba algo nuevo).
        # Esto permite llenar la tabla con estados desconocidos al inicio.
        if en_entrenamiento and random.uniform(0, 1) < self.epsilon:
            return random.choice(movimientos_posibles)

        # ---------------------------------------------------------
        # 2. FASE DE EXPLOTACIÓN (Usar conocimiento)
        # ---------------------------------------------------------
        # El agente consulta su Tabla Q y elige la acción con el valor más alto (Max Q).
        
        # Si el estado es nuevo, lo inicializamos en 0 (Tabula Rasa).
        if estado not in self.q_table:
            self.q_table[estado] = {mov: 0.0 for mov in movimientos_posibles}

        valores_movimientos = self.q_table[estado]
        valores_validos = {m: valores_movimientos.get(m, 0.0) for m in movimientos_posibles}
        
        # Buscamos el valor máximo (Argmax)
        max_valor = max(valores_validos.values())
        mejores_movimientos = [m for m, v in valores_validos.items() if v == max_valor]
        
        return random.choice(mejores_movimientos)

    def aprender(self, estado_actual, accion, recompensa, estado_siguiente, movimientos_siguientes, termino_juego):
        """
        Núcleo del algoritmo: Aplica la ECUACIÓN DE BELLMAN para actualizar la memoria.
        Ref PDF (Pág. 6): "La Ecuación de Bellman: El Motor de Aprendizaje".
        
        Fórmula: Q_new(s,a) = Q(s,a) + alpha * [ R + gamma * max(Q(s',a')) - Q(s,a) ]
        """
        estado_t = self.obtener_estado(estado_actual)
        estado_t1 = self.obtener_estado(estado_siguiente)

        # Asegurar que los estados existan en la memoria
        if estado_t not in self.q_table:
            self.q_table[estado_t] = {accion: 0.0}
        if estado_t1 not in self.q_table:
            self.q_table[estado_t1] = {m: 0.0 for m in movimientos_siguientes}

        # 1. Obtener Q(s,a) -> Valor Antiguo (Lo que creíamos saber)
        q_actual = self.q_table[estado_t].get(accion, 0.0)

        # 2. Calcular max Q(s',a') -> Mejor Futuro Estimado (La promesa del siguiente estado)
        if termino_juego:
            max_q_futuro = 0.0 # No hay futuro si el juego terminó
        else:
            vals_siguientes = [self.q_table[estado_t1].get(m, 0.0) for m in movimientos_siguientes]
            max_q_futuro = max(vals_siguientes) if vals_siguientes else 0.0

        # [cite_start]3. Aplicar la Ecuación de Bellman [cite: 63]
        # Nuevo Valor = Valor Viejo + Tasa Aprendizaje * (Recompensa + Descuento * Mejor Futuro - Valor Viejo)
        nuevo_q = q_actual + self.alpha * (recompensa + (self.gamma * max_q_futuro) - q_actual)
        
        # 4. Actualizar la Tabla Q
        self.q_table[estado_t][accion] = nuevo_q

    def reducir_epsilon(self):
        """
        Decay de Epsilon: Reduce gradualmente la curiosidad.
        Al principio explora mucho (E=1.0), al final explota lo aprendido (E=0.01).
        Ref PDF (Pág. 11): "Convergencia: De Principiante a Maestro".
        """
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def guardar_conocimiento(self):
        """Persistencia de datos: Guarda la Tabla Q en un archivo JSON."""
        try:
            data_para_json = {str(k): v for k, v in self.q_table.items()}
            with open(ARCHIVO_Q_TABLE, "w") as f:
                json.dump(data_para_json, f, indent=4)
            print(f" Cerebro guardado en {ARCHIVO_Q_TABLE} ({len(self.q_table)} estados).")
        except Exception as e:
            print(f" Error guardando cerebro: {e}")

    def cargar_conocimiento(self):
        """Carga la Tabla Q para jugar usando el conocimiento previo."""
        if os.path.exists(ARCHIVO_Q_TABLE):
            try:
                with open(ARCHIVO_Q_TABLE, "r") as f:
                    data_cargada = json.load(f)
                
                self.q_table = {}
                for k_str, v in data_cargada.items():
                    # Reconstruye la tupla del estado desde el string del JSON
                    key_tupla = ast.literal_eval(k_str)
                    valores_int = {int(m): valor for m, valor in v.items()}
                    self.q_table[key_tupla] = valores_int
                    
                print(f"Cerebro cargado: {len(self.q_table)} estados aprendidos.")
                # IMPORTANTE: Si cargamos un cerebro, asumimos que ya sabe jugar.
                # Bajamos Epsilon a 0.0 para que juegue en modo "Experto" (Solo Explotación).
                self.epsilon = 0.0 
            except Exception as e:
                print(f" Error cargando cerebro JSON: {e}")
                self.q_table = {}
        else:
            print("No hay cerebro guardado.")

# Instancia global del Q-Agent
agente_global = QAgent()


# =============================================================================
# SECCIÓN 2: ALGORITMO MINIMAX (El Dios Calculador - Benchmark)
# =============================================================================
# Implementación clásica recursiva para comparar contra el Q-Learning.

CACHE_MINIMAX = {}

def limpiar_cache():
    """Limpia la memoria de memoización del Minimax."""
    CACHE_MINIMAX.clear()

def minimax(tablero, profundidad, es_turno_max):
    """
    Algoritmo Minimax.
    Explora el árbol de juego completo para encontrar la jugada matemáticamente perfecta.
    """
    estado_clave = (tuple(tablero), es_turno_max)
    if estado_clave in CACHE_MINIMAX:
        return CACHE_MINIMAX[estado_clave]

    juego = LogicaTresRayas()
    juego.tablero = list(tablero)
    ganador = juego.verificar_ganador()

    # Función de Utilidad Ponderada por Profundidad
    if ganador == "X":
        return 10 - profundidad # Ganar rápido es mejor
    elif ganador == "O":
        return profundidad - 10 # Perder lento es mejor (si es inevitable)
    elif not juego.existe_espacio_libre():
        return 0

    movimientos = juego.obtener_movimientos_posibles()
    
    if es_turno_max: # Turno de Maximizar (X)
        mejor_puntaje = -float('inf')
        for mov in movimientos:
            juego.tablero[mov] = "X"
            puntaje = minimax(juego.tablero, profundidad + 1, False)
            juego.tablero[mov] = " "
            mejor_puntaje = max(mejor_puntaje, puntaje)
    else: # Turno de Minimizar (O)
        mejor_puntaje = float('inf')
        for mov in movimientos:
            juego.tablero[mov] = "O"
            puntaje = minimax(juego.tablero, profundidad + 1, True)
            juego.tablero[mov] = " "
            mejor_puntaje = min(mejor_puntaje, puntaje)
    
    CACHE_MINIMAX[estado_clave] = mejor_puntaje
    return mejor_puntaje

def obtener_movimiento_minimax_adaptable(tablero, ficha_jugador):
    """
    Wrapper para permitir que Minimax juegue como 'X' o 'O' en el duelo de IAs.
    """
    mejor_movimiento = None
    es_maximizador = (ficha_jugador == "X")
    
    if es_maximizador:
        mejor_puntaje = -float('inf')
    else:
        mejor_puntaje = float('inf')

    for movimiento in range(9):
        if tablero[movimiento] == " ":
            tablero_copia = list(tablero)
            tablero_copia[movimiento] = ficha_jugador
            
            # Se invierte el turno para la llamada recursiva
            puntaje = minimax(tablero_copia, 0, not es_maximizador)
            
            if es_maximizador:
                if puntaje > mejor_puntaje:
                    mejor_puntaje = puntaje
                    mejor_movimiento = movimiento
            else:
                if puntaje < mejor_puntaje:
                    mejor_puntaje = puntaje
                    mejor_movimiento = movimiento
                    
    return mejor_movimiento

# =============================================================================
# SECCIÓN 3: VISUALIZACIÓN (Legado)
# =============================================================================

def generar_arbol_visual(historial):
    
    def construir_nivel_recursivo(tablero_actual, paso_idx):
        if paso_idx >= len(historial):
            return []

        mov_real = historial[paso_idx]
        turno_quien_jugo = "X" if paso_idx % 2 == 0 else "O"
        
        nodos_hermanos = []
        movimientos_posibles = [i for i, c in enumerate(tablero_actual) if c == " "]
        
        nodo_camino_real = None

        for mov in movimientos_posibles:
            t_futuro = list(tablero_actual)
            t_futuro[mov] = turno_quien_jugo
            
            es_turno_max_siguiente = (turno_quien_jugo == "O")
            puntaje = minimax(t_futuro, 0, es_turno_max_siguiente)
            
            es_el_elegido = (mov == mov_real)
            
            nodo = {
                "movimiento": mov,
                "tablero": t_futuro,
                "puntaje": puntaje,
                "es_camino_ganador": es_el_elegido,
                "sub_ramas": [] 
            }
            nodos_hermanos.append(nodo)
            
            if es_el_elegido:
                nodo_camino_real = nodo
        
        if nodo_camino_real:
            nodo_camino_real["sub_ramas"] = construir_nivel_recursivo(
                nodo_camino_real["tablero"], paso_idx + 1
            )
            
        return nodos_hermanos

    return construir_nivel_recursivo([" "]*9, 0)