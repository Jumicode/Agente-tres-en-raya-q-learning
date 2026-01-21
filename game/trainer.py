import random
import time
from game.logic import LogicaTresRayas
from game.ai import agente_global

def jugar_episodio_entrenamiento(jugar_vs_si_mismo=False):
    """
    Simula UNA partida completa de entrenamiento.
    Retorna: El resultado ('X', 'O', 'Empate')
    """
    juego = LogicaTresRayas()
    turno = "X" # El agente siempre será X en este entrenamiento
    
    # Variables para recordar el estado anterior del agente
    estado_previo_agente = None
    accion_previa_agente = None
    
    while True:
        # ---------------------------------------------------
        # TURNO DEL AGENTE (X)
        # ---------------------------------------------------
        if turno == "X":
            movimientos_validos = juego.obtener_movimientos_posibles()
            
            estado_actual = list(juego.tablero)
            
            # Elegir acción
            accion = agente_global.obtener_accion(estado_actual, movimientos_validos, en_entrenamiento=True)
            
            # Aplicar acción
            juego.realizar_movimiento(accion, "X")
            
            ganador = juego.verificar_ganador()
            
            if ganador == "X":
                # GANÓ (X)
                # Corrección: Pasamos juego.tablero como estado siguiente y [] como movimientos
                agente_global.aprender(estado_actual, accion, 10, juego.tablero, [], True)
                return "X"
            elif not juego.existe_espacio_libre():
                # EMPATE
                agente_global.aprender(estado_actual, accion, 5, juego.tablero, [], True)
                return "Empate"
            
            # Guardamos estado para evaluar después
            estado_previo_agente = estado_actual
            accion_previa_agente = accion
            
            turno = "O"

        # ---------------------------------------------------
        # TURNO DEL OPONENTE (O)
        # ---------------------------------------------------
        else:
            movimientos_validos = juego.obtener_movimientos_posibles()
            
            if jugar_vs_si_mismo:
                accion_rival = agente_global.obtener_accion(juego.tablero, movimientos_validos, en_entrenamiento=True)
            else:
                accion_rival = random.choice(movimientos_validos)
            
            juego.realizar_movimiento(accion_rival, "O")
            
            ganador = juego.verificar_ganador()
            movimientos_futuros = juego.obtener_movimientos_posibles() # Ojo: esto es para cuando NO termina
            
            # --- FASE DE APRENDIZAJE DEL AGENTE ---
            
            if ganador == "O":
                # EL RIVAL GANÓ (Castigo diferido)
                if estado_previo_agente is not None:
                    # Corrección: Agregado el argumento [] antes del True
                    agente_global.aprender(estado_previo_agente, accion_previa_agente, -10, juego.tablero, [], True)
                return "O"
            
            elif not juego.existe_espacio_libre():
                # EMPATE (Premio diferido)
                if estado_previo_agente is not None:
                    # Corrección: Agregado el argumento [] antes del True
                    agente_global.aprender(estado_previo_agente, accion_previa_agente, 5, juego.tablero, [], True)
                return "Empate"
            
            else:
                # EL JUEGO SIGUE (Neutro)
                if estado_previo_agente is not None:
                    # Aquí SÍ pasamos movimientos_futuros porque el juego no terminó
                    agente_global.aprender(estado_previo_agente, accion_previa_agente, 0, juego.tablero, movimientos_futuros, False)
            
            turno = "X"

def ejecutar_entrenamiento(n_episodios=10000):
    """
    Ejecuta el ciclo de entrenamiento masivo.
    """
    print(f"\n INICIANDO ENTRENAMIENTO ({n_episodios} Partidas)...")
    print("El agente está aprendiendo. Por favor espere.")
    
    tiempo_inicio = time.time()
    
    victorias_x = 0
    victorias_o = 0
    empates = 0
    
    for i in range(1, n_episodios + 1):
        vs_self = (i % 500 == 0)
        
        resultado = jugar_episodio_entrenamiento(jugar_vs_si_mismo=vs_self)
        
        if resultado == "X": victorias_x += 1
        elif resultado == "O": victorias_o += 1
        else: empates += 1
        
        agente_global.reducir_epsilon()
        
        if i % (n_episodios // 10) == 0:
            porcentaje = (i / n_episodios) * 100
            print(f"Progreso: {porcentaje:.0f}% | Epsilon: {agente_global.epsilon:.4f} | Gana X: {victorias_x} - Gana O: {victorias_o}")

    tiempo_fin = time.time()
    duracion = tiempo_fin - tiempo_inicio
    
    print("\n" + "="*40)
    print(" ENTRENAMIENTO FINALIZADO")
    print(f"Tiempo total: {duracion:.2f} segundos")
    print(f"Victorias IA (X): {victorias_x}")
    print(f"Derrotas IA (O):  {victorias_o}")
    print(f"Empates:          {empates}")
    print("="*40 + "\n")
    
    agente_global.guardar_conocimiento()

if __name__ == "__main__":
    ejecutar_entrenamiento(10000)