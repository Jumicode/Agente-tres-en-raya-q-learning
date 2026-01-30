# MAIN.PY: Ejecutador del juego"
import time
import sys
import pygame 
import os

from game.logic import LogicaTresRayas
from game.ai import agente_global, obtener_movimiento_minimax_adaptable, generar_arbol_visual, limpiar_cache
from ui.interface import *
from ui.menu import MenuPrincipal
from ui.assets import *
from ui.help import * 

# ------------------------------
# FUNCIÓN PRINCIPAL
# Inicia Pygame, muestra el menú y ejecuta el bucle principal del juego en el modo seleccionado.
# ------------------------------

def main():
    # INICIALIZAR PYGAME Y SONIDO
    pygame.init()
    pygame.mixer.init()
    establecer_icono_ventana() 
    iniciar_musica_fondo()

    p_q= 0
    p_m= 0
    empates_ai = 0
    
    # Set 2: Humano vs IA
    p_human = 0
    p_ia_vs_h = 0
    empates_h = 0
    
    # CONFIGURAR VENTANA PRINCIPAL
    pantalla_principal = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Tres en Raya - Machine Learning")

    # BUCLE INFINITO PARA REINICIAR EL JUEGO
    while True:
        menu = MenuPrincipal(pantalla_principal)
        en_menu = True
        clock = pygame.time.Clock()

        modo_juego = "HUMANO" 

        # BUCLE DEL MENÚ PRINCIPAL
        while en_menu:
            clock.tick(60)
            menu.actualizar()
            accion = menu.manejar_eventos()

            if accion == "SALIR":
                pygame.quit(); sys.exit()
            
            elif accion == "JUGAR":
                modo_juego = "HUMANO" 
                en_menu = False
            
            elif accion == "MINIMAX":  
                modo_juego = "MINIMAX"
                en_menu = False 

        # --- INICIO DEL JUEGO ---
        juego = LogicaTresRayas()
        ui = InterfazGrafica()
        
        turno = "X"
        mensaje_estado = "Juega la IA (X)"
        juego_corriendo = True
        juego_terminado_flag = False
        limpiar_cache()
        estructura_arbol = [] 
        
        # BUCLE PRINCIPAL DE LA PARTIDA
        while juego_corriendo:
            clock.tick(60)

            # 1. DIBUJAR INTERFAZ SEGÚN MODO DE JUEGO
            if modo_juego == "HUMANO":
                ui.dibujar_interfaz_humano(juego.tablero, mensaje_estado, p_human, p_ia_vs_h, empates_h, juego.combo_ganador)
            else:
                ui.dibujar_interfaz_minimax(juego.tablero, mensaje_estado, p_q, p_m, empates_ai, estructura_arbol, juego.combo_ganador)

            # 2. GESTIONAR EVENTOS DE USUARIO
            evento = ui.obtener_evento_usuario()

            if evento == 'SALIR':
                pygame.quit(); sys.exit()

            if evento == 'MENU':
                juego_corriendo = False 
                break 
            
            if evento == 'REINICIAR':
                juego.reiniciar()
                turno = "X" 
                mensaje_estado = "IA Pensando"
                juego_terminado_flag = False
                continue

            # IGNORAR EVENTOS SI EL JUEGO YA TERMINÓ
            if juego_terminado_flag: 
                continue
            
            # VERIFICAR ESTADO FINAL DEL JUEGO
            if juego.juego_terminado() and not juego_terminado_flag:
                ganador = juego.verificar_ganador()
                                
                if modo_juego == "HUMANO":
                    if ganador == "X": 
                        p_ia_vs_h += 1
                        mensaje_estado = "¡Perdiste! Ganó la IA."
                    elif ganador == "O": 
                        p_human += 1 
                        mensaje_estado = "¡Ganaste!"
                    else: 
                        empates_h += 1 
                        mensaje_estado = "¡Empate!"
                        if 'draw' in ui.sonidos: ui.sonidos['draw'].play()
                else: 
                    # Modo IA vs IA
                    if ganador == "X": 
                        p_q_vs_m += 1
                        mensaje_estado = "Ganó Q-Learning (X)"
                    elif ganador == "O": 
                        p_m_vs_q += 1
                        mensaje_estado = "Ganó Minimax (O)"
                    else: 
                        empates_ai += 1 
                        mensaje_estado = "¡Empate!"
                        if 'draw' in ui.sonidos: ui.sonidos['draw'].play()

                if ganador and 'win' in ui.sonidos:
                    ui.sonidos['win'].play()

                estructura_arbol = generar_arbol_visual(juego.tablero)         
                juego_terminado_flag = True
                continue

            # TURNO DE LA IA (Q-LEARNING)
            if turno == "X":
                if modo_juego == "HUMANO":
                    ui.dibujar_interfaz_humano(juego.tablero, mensaje_estado, p_human, p_ia_vs_h, empates_h, juego.combo_ganador)
                else:
                    ui.dibujar_interfaz_minimax(juego.tablero, mensaje_estado, p_q, p_m, empates_ai, estructura_arbol, juego.combo_ganador)

                pygame.display.flip()
                
                time.sleep(0.5) 

                posibles = juego.obtener_movimientos_posibles()
                
                accion_ia = agente_global.obtener_accion(juego.tablero, posibles, en_entrenamiento=False)
                
                if accion_ia is not None:
                    juego.realizar_movimiento(accion_ia, "X")
                    estructura_arbol = generar_arbol_visual(juego.tablero) 
                    turno = "O"
                    if 'colocar' in ui.sonidos: 
                        ui.sonidos['colocar'].play()
                    if modo_juego == "HUMANO":
                        mensaje_estado = "Tu turno"
                    else:
                        mensaje_estado = "Turno de Minimax"
                else:
                    pass 

            # TURNO DEL OPONENTE (HUMANO O MINIMAX)
            else:

                if modo_juego == "MINIMAX":
                    ui.dibujar_interfaz_minimax(juego.tablero, mensaje_estado, p_q, p_m, empates_ai, estructura_arbol, juego.combo_ganador)
                    pygame.display.flip()
                    time.sleep(0.5)
                    movimiento = obtener_movimiento_minimax_adaptable(juego.tablero, "O")
                    if movimiento is not None:
                        juego.realizar_movimiento(movimiento, "O")
                        estructura_arbol = generar_arbol_visual(juego.tablero) 
                        turno = "X"
                        if 'colocar' in ui.sonidos: 
                            ui.sonidos['colocar'].play()
                        mensaje_estado = "Q-Learning Pensando..."
                else: 
                    # TURNO DEL JUGADOR HUMANO
                    if isinstance(evento, int): 
                        movimiento = evento
                        
                        if juego.es_movimiento_valido(movimiento):
                            juego.realizar_movimiento(movimiento, "O")
                            estructura_arbol = generar_arbol_visual(juego.tablero) 
                            turno = "X" 
                            if 'colocar' in ui.sonidos: ui.sonidos['colocar'].play()
                        else:
                            if 'error' in ui.sonidos: ui.sonidos['error'].play()

if __name__ == "__main__":
    main()