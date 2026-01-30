# INTERFACE.PY: ARCHIVO DIBUJA LA INTERFAZ DEL JUEGO"

import pygame
import sys
import os

from ui.config import *
from ui.components import *
from ui.events import *
from ui.assets import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class InterfazGrafica:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Tres en Raya - Machine Learning")
        
        # VARIABLES DE ESTADO 
        self.tablero_previo = [" "] * 9 
        self.animaciones_fichas = {} 
        self.ultimo_boton_hover = None
        self.modal_abierto = False
        self.arrastrando = False
        self.mouse_previo = (0, 0)
        
        # Variables de Scroll para el árbol
        self.modal_scroll_x = 0
        self.modal_scroll_y = 0
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_camino = 0
        
        # Límites
        self.scroll_camino_min = -2000
        self.scroll_camino_max = 200
        self.scroll_x_min = -1200
        self.scroll_x_max = 300
        self.scroll_y_min = -2500
        self.scroll_y_max = 200
        
        # VELOCIDADES (Las que faltaban)
        self.scroll_camino_speed = 30
        self.scroll_velocidad = 40
        self.modal_scroll_vel = 40
        
        self.fade_cache = {}
        self.fade_speed = 12

        # CARGA DE ASSETS 
        self.fuentes = cargar_fuentes()
        self.sonidos = cargar_sonidos()
        self.fondo_juego = cargar_fondos()  
        
        # Gatos
        sets_gatos = cargar_imagenes_gato()
        self.imagenes_q = sets_gatos["q"]
        self.imagenes_m = sets_gatos["m"]

        self.imagenes_q_mini = {k: pygame.transform.scale(v, (260, 310)) for k, v in self.imagenes_q.items() if v}
        self.imagenes_m_mini = {k: pygame.transform.scale(v, (260, 310)) for k, v in self.imagenes_m.items() if v}
        
        # Iconos
        self.img_home, self.img_reload, self.img_tree = cargar_iconos()

        # Configuración de Tablero
        self.ancho_juego = (TAMANO_CASILLA * 3) + (ESPACIO * 2) 
        self.inicio_x = 0
        self.inicio_y = 0

        # BOTONES 
        self.rect_home = pygame.Rect(25, 25, 50, 50)
        self.rect_reload = pygame.Rect(25, 90, 50, 50)
        self.rect_boton_arbol = pygame.Rect(ANCHO_VENTANA - 75, 25, 50, 50)
        
        # Variables que busca events.py originalmente
        self.rect_boton_salir = self.rect_home    
        self.rect_boton = self.rect_reload    
    
    # ------------------------------
    # DIBUJAR BOTÓN CON IMAGEN
    # Crea un botón interactivo con sombra, efecto hover y un ícono centrado.
    # ------------------------------
    def _dibujar_boton_con_imagen(self, rect, imagen_icon):
        mouse_pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse_pos)
        
        # Sombra
        sombra = rect.copy(); sombra.y += 5
        pygame.draw.rect(self.pantalla, (40, 40, 80), sombra, border_radius=12)
        
        # Cuerpo
        color = (60, 63, 130) if hover else (55, 58, 127)
        rect_v = rect.copy()
        if hover: rect_v.y -= 4
        pygame.draw.rect(self.pantalla, color, rect_v, border_radius=12)
        
        if imagen_icon:
            self.pantalla.blit(imagen_icon, imagen_icon.get_rect(center=rect_v.center))
        return hover

    # ------------------------------
    # DIBUJAR GRID DEL TABLERO
    # Pinta el fondo del tablero y las 9 casillas con sus fichas (X o O).
    # ------------------------------
    def _dibujar_grid_tablero(self, x_pos, y_pos, tablero):
        self.inicio_x, self.inicio_y = x_pos, y_pos
        ancho_fondo = self.ancho_juego + (PADDING_LATERAL * 2)
        alto_fondo = self.ancho_juego + (PADDING_TABLERO * 2)
        pygame.draw.rect(self.pantalla, pygame.Color(COLOR_TABLERO), (x_pos - PADDING_LATERAL, y_pos - PADDING_TABLERO, ancho_fondo, alto_fondo), border_radius=45)

        for i in range(9):
            fila, col = i // 3, i % 3
            x, y = x_pos + col * (TAMANO_CASILLA + ESPACIO), y_pos + fila * (TAMANO_CASILLA + ESPACIO)
            pygame.draw.rect(self.pantalla, pygame.Color(COLOR_CASILLA_SOMBRA_3D), (x, y + 10, TAMANO_CASILLA, TAMANO_CASILLA), border_radius=25)
            pygame.draw.rect(self.pantalla, pygame.Color(COLOR_CASILLA), (x, y, TAMANO_CASILLA, TAMANO_CASILLA), border_radius=25)
            if tablero[i] != " ":
                color = pygame.Color(COLOR_X if tablero[i] == "X" else COLOR_O)
                txt = self.fuentes['ficha'].render(tablero[i], True, color)
                self.pantalla.blit(txt, txt.get_rect(center=(x + TAMANO_CASILLA / 2, y + TAMANO_CASILLA / 2)))


    # ------------------------------
    # DIBUJAR AVATAR
    # Muestra el gato en pantalla según su tamaño (mini o grande) y estado de ánimo.
    # ------------------------------    
    def dibujar_avatar(self, superficie, estado_emocional, lado="derecha", modo_mini=False, ai_set="q"):

        # Elegir el set correcto según el tipo de IA y el tamaño
        if ai_set == "q":
            diccionario = self.imagenes_q_mini if modo_mini else self.imagenes_q
        else:
            diccionario = self.imagenes_m_mini if modo_mini else self.imagenes_m
            
        img = diccionario.get(estado_emocional) or diccionario.get("neutro")
        if not img: return
        
        # POSICIONAMIENTO 
        if modo_mini:
            # Gatos pequeños en las esquinas (IA vs IA)
            x_gato = int(ANCHO_VENTANA * 0.95 - img.get_width()) if lado == "derecha" else int(ANCHO_VENTANA * 0.05)
            y_gato = int((ALTO_VENTANA / 2) - (img.get_height() / 2)) + 50
            rect_plat = pygame.Rect(x_gato - 15, y_gato + img.get_height() - 80, img.get_width() + 30, 100)
        else:
            # Gato grande (Modo Humano)
            x_gato = int(ANCHO_VENTANA * 0.60)
            y_gato = int((ALTO_VENTANA / 2) - (img.get_height() / 2)) + 30
            rect_plat = pygame.Rect(x_gato - 20, y_gato + img.get_height() - 150, img.get_width() + 40, 160)

        pygame.draw.rect(superficie, (55, 58, 127), rect_plat, border_radius=25)
        superficie.blit(img, (x_gato, y_gato))

    # ------------------------------
    # DIBUJAR INTERFAZ HUMANO
    # Muestra la pantalla completa del modo Jugador vs IA: fondo, tablero, títulos y gato animado.
    # ------------------------------       
    def dibujar_interfaz_humano(self, tablero, mensaje, combo_ganador=None):
        if self.fondo_juego: self.pantalla.blit(self.fondo_juego, (0, 0))
        else: self.pantalla.fill(pygame.Color(COLOR_FONDO))

        # Títulos
        lbl_t = self.fuentes['titulo'].render("TABLERO DEL JUEGO", True, (55, 58, 127))
        self.pantalla.blit(lbl_t, lbl_t.get_rect(center=(ANCHO_VENTANA // 2, 60)))
        lbl_m = self.fuentes['subtitulo'].render(mensaje, True, (235, 186, 239))
        self.pantalla.blit(lbl_m, lbl_m.get_rect(center=(ANCHO_VENTANA // 2, 110)))

        # Tablero a la izquierda
        self._dibujar_grid_tablero(int(ANCHO_VENTANA * 0.20), int(ALTO_VENTANA/2 - 150), tablero)
        
        # Emoción del Gato (Q-Learning)
        emocion = "neutro"
        if "Perdiste" in mensaje or "Ganó la IA" in mensaje: emocion = "feliz"
        elif "Ganaste" in mensaje: emocion = "triste"
        elif "IA Pensando" in mensaje: emocion = "pensando"

        # DIBUJAR UN SOLO GATO GRANDE
        self.dibujar_avatar(self.pantalla, emocion, "derecha", modo_mini=False, ai_set="q")

        if combo_ganador: self.dibujar_linea_ganadora(combo_ganador)
        self._gestionar_botones_comunes()
        pygame.display.flip()

    # ------------------------------
    # DIBUJAR INTERFAZ MINIMAX
    # Muestra la pantalla del modo IA vs Minimax con tablero centrado y dos gatos pequeños enfrentados.
    # ------------------------------
    def dibujar_interfaz_minimax(self, tablero, mensaje, estructura_arbol=None, combo_ganador=None):
        if self.fondo_juego: self.pantalla.blit(self.fondo_juego, (0, 0))
        else: self.pantalla.fill((150, 150, 200))

        lbl_t = self.fuentes['titulo'].render("Q-LEARNING VS MINIMAX", True, (55, 58, 127))
        self.pantalla.blit(lbl_t, lbl_t.get_rect(center=(ANCHO_VENTANA // 2, 60)))
        lbl_m = self.fuentes['subtitulo'].render(mensaje, True, (255, 255, 255))
        self.pantalla.blit(lbl_m, lbl_m.get_rect(center=(ANCHO_VENTANA // 2, 110)))

        # Tablero Centrado
        self._dibujar_grid_tablero(ANCHO_VENTANA // 2 - (self.ancho_juego // 2), int(ALTO_VENTANA/2 - 150), tablero)

        # Emociones cruzadas
        emocion_q = "pensando" if "Q-Learning" in mensaje or "IA Pensando" in mensaje else "neutro"
        emocion_m = "pensando" if "Minimax" in mensaje else "neutro"
        if "Perdiste" in mensaje or "Ganó Q-Learning" in mensaje: emocion_q, emocion_m = "feliz", "triste"
        elif "Ganaste" in mensaje or "Ganó Minimax" in mensaje: emocion_q, emocion_m = "triste", "feliz"

        # DIBUJAR DOS GATOS PEQUEÑOS
        self.dibujar_avatar(self.pantalla, emocion_q, "izquierda", True, ai_set="q")
        self.dibujar_avatar(self.pantalla, emocion_m, "derecha", True, ai_set="m")

        self._gestionar_botones_comunes(incluir_arbol=True)
        

        if combo_ganador: self.dibujar_linea_ganadora(combo_ganador)
        if self.modal_abierto: self._dibujar_modal_arbol(estructura_arbol)
        
        pygame.display.flip()

    # ------------------------------
    # GESTIONAR BOTONES COMUNES
    # Controla los botones de salir y reiniciar, detectando cuando el mouse pasa por encima.
    # ------------------------------
    def _gestionar_botones_comunes(self, incluir_arbol=False):

        h_home = self._dibujar_boton_con_imagen(self.rect_home, self.img_home)
        h_reload = self._dibujar_boton_con_imagen(self.rect_reload, self.img_reload)
        
        h_tree = False
        if incluir_arbol:
            h_tree = self._dibujar_boton_con_imagen(self.rect_boton_arbol, self.img_tree)

        hover_actual = None
        if h_home:
            hover_actual = "SALIR"
        elif h_reload:
            hover_actual = "NUEVO"
        elif h_tree:
            hover_actual = "ARBOL"

        if hover_actual != self.ultimo_boton_hover:
            if hover_actual is not None:
                if 'menu_hover' in self.sonidos:
                    self.sonidos['menu_hover'].play()
            self.ultimo_boton_hover = hover_actual

    # ------------------------------
    # OBTENER EVENTO USUARIO
    # Captura y devuelve las acciones del teclado o mouse del jugador.
    # ------------------------------   
    def obtener_evento_usuario(self):
        return manejar_eventos(self)
    
    # ------------------------------
    # DIBUJAR LÍNEA GANADORA
    # Traza una línea dorada sobre las tres casillas que formaron el ganador.
    # ------------------------------
    def dibujar_linea_ganadora(self, combo):
        if not combo: return
        def centro(i):
            f, c = i // 3, i % 3
            return (self.inicio_x + c*(TAMANO_CASILLA+ESPACIO) + TAMANO_CASILLA//2, self.inicio_y + f*(TAMANO_CASILLA+ESPACIO) + TAMANO_CASILLA//2)
        p1, p2 = centro(combo[0]), centro(combo[2])
        pygame.draw.line(self.pantalla, (255, 215, 0), p1, p2, 15)

    # ------------------------------
    # AUXILIAR: Extraer camino lineal del árbol
    # Recorre la estructura de árbol buscando los nodos marcados como 'es_camino_ganador'
    # para reconstruir la lista lineal que se muestra a la derecha.
    # ------------------------------
    """ def _extraer_camino_lineal(self, arbol):
        camino = []
        if not arbol:
            return camino
        
        # En el primer nivel (hermanos), buscamos el ganador
        nodo_actual = None
        for nodo in arbol:
            if nodo.get("es_camino_ganador"):
                nodo_actual = nodo
                break
        
        # Si no hay ganador marcado en la raíz, tomamos el primero (fallback)
        if not nodo_actual and arbol:
            nodo_actual = arbol[0]

        # Recorrer hacia abajo
        while nodo_actual:
            camino.append(nodo_actual)
            
            # Buscar el siguiente en las sub_ramas
            siguiente = None
            if nodo_actual.get("sub_ramas"):
                for hijo in nodo_actual["sub_ramas"]:
                    if hijo.get("es_camino_ganador"):
                        siguiente = hijo
                        break
                # Si no encontramos uno marcado, tomamos el primero (fallback visual)
                if not siguiente and nodo_actual["sub_ramas"]:
                    siguiente = nodo_actual["sub_ramas"][0]
            
            nodo_actual = siguiente
            
        return camino  """

    # ------------------------------
    # ÁRBOL recursivo (usa scroll_x, scroll_y)
    # Dibuja el árbol con nodos, líneas y scroll; llama a mini-tableros y se expande solo.
    # ------------------------------
    def dibujar_arbol_recursivo(self, nodos, x_min, x_max, y_nivel, padre_pos=None):
        if not nodos: return

        cantidad = len(nodos)
        ancho_nodo_px = (TAMANO_MINI * 3) + 8
        
        # Espacio fijo entre nodos hermanos
        ESPACIO_ENTRE_HERMANOS = 140 
        
        centro_area = (x_min + x_max) / 2
        ancho_total_grupo = cantidad * ESPACIO_ENTRE_HERMANOS
        x_inicio = centro_area - (ancho_total_grupo / 2)

        for i, nodo in enumerate(nodos):
            center_x_nodo = x_inicio + (i * ESPACIO_ENTRE_HERMANOS) + (ESPACIO_ENTRE_HERMANOS / 2)
            
            # Posición final
            pos_x = center_x_nodo - (ancho_nodo_px / 2) + self.scroll_x
            pos_y = y_nivel + self.scroll_y
            
            punto_conexion_top = (pos_x + ancho_nodo_px / 2, pos_y)

            # --- DIBUJAR LÍNEAS ---
            if padre_pos:
                padre_x, padre_y = padre_pos
                hijo_x, hijo_y = punto_conexion_top
                mid_y = (padre_y + hijo_y) // 2

                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), (padre_x, padre_y), (padre_x, mid_y), 2)
                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), (padre_x, mid_y), (hijo_x, mid_y), 2)
                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), (hijo_x, mid_y), (hijo_x, hijo_y), 2)
                
            # Determinar si es camino ganador para resaltarlo
            es_camino = nodo.get("es_camino_ganador", False)
            nodo_id = id(nodo)
            
            punto_conexion_bottom = dibujar_mini_tablero(
                self.pantalla,         
                self.fuentes['mini'],       
                pos_x, pos_y, 
                nodo["tablero"], 
                TAMANO_MINI, 
                self.fade_cache,        
                self.fade_speed,        
                nodo.get("puntaje"), 
                nodo_id, 
                es_camino=es_camino
            )

            p_val = nodo.get("puntaje")
            if p_val is not None:
                col_p = pygame.Color("#ccffcc") if p_val > 0 else (pygame.Color("#ffcccc") if p_val < 0 else pygame.Color("#ffffff"))
                lbl_puntaje = self.fuentes['numeros'].render(str(p_val), True, col_p)
                self.pantalla.blit(lbl_puntaje, (pos_x + ancho_nodo_px + 3, pos_y + 10))

            if nodo.get("sub_ramas"):
                ancho_virtual = 4000 
                self.dibujar_arbol_recursivo(
                    nodo["sub_ramas"], 
                    center_x_nodo - ancho_virtual,
                    center_x_nodo + ancho_virtual, 
                    y_nivel + ESPACIO_VERTICAL_ARBOL, 
                    punto_conexion_bottom
                )   

    # ------------------------------
    # CAMINO REAL (columna con scroll propio)
    # Dibuja la columna del CAMINO REAL con scroll independiente.
    # Solo muestra la etiqueta de turno y el mini-tablero, sin puntaje.
    # ------------------------------
    def dibujar_camino_real(self, camino_real, x_inicio, y_inicio):

        if not camino_real:
            return
        
        y = y_inicio + self.scroll_camino
        
        for depth, nodo in enumerate(camino_real):
            # Deducir turno
            es_turno_ia = self._es_turno_ia(nodo["tablero"])
            turno = "IA" if es_turno_ia else "Humano"
            color = (255, 255, 255) if es_turno_ia else (255, 255, 255)
            
            self.pantalla.blit(self.fuentes['ui'].render(turno, True, color), (x_inicio, y))
            y += 20

            # Mini-tablero 
            _, bottom = dibujar_mini_tablero(
                self.pantalla, self.fuentes['mini'],
                x_inicio, y, 
                nodo["tablero"], TAMANO_MINI, 
                self.fade_cache, self.fade_speed, 
                None, id(nodo)
            )
            y = bottom + 20

            if depth < len(camino_real) - 1:
                pygame.draw.line(self.pantalla, pygame.Color(200, 200, 200),
                                 (x_inicio + 40, y - 10), (x_inicio + 40, y + 5), 2)

    # ------------------------------
    # DIBUJAR INTERFAZ (principal)
    # Dibuja toda la pantalla.
    # ------------------------------
    def dibujar_interfaz(self, tablero, mensaje, tablero_raiz=None, estructura_arbol=None, camino_real=None, combo_ganador=None):

        # Extraer el camino lineal del árbol 
        boton_hover_actual = None
        """ camino_visual = self._extraer_camino_lineal(estructura_arbol) """

        if self.fondo_juego:
            self.pantalla.blit(self.fondo_juego, (0, 0))
        else:
            self.pantalla.fill(pygame.Color(COLOR_FONDO))

        # SECCIÓN IZQUIERDA (TABLERO)
        t_tablero = self.fuentes['titulo'].render("TABLERO DEL JUEGO", True, pygame.Color(COLOR_BOTON))
        self.pantalla.blit(t_tablero, t_tablero.get_rect(center=(self.centro_izq, 80)))
        
        t_turno = self.fuentes['subtitulo'].render(mensaje, True, pygame.Color(COLOR_X))
        self.pantalla.blit(t_turno, t_turno.get_rect(center=(self.centro_izq, 130)))

        ancho_fondo = self.ancho_juego + (PADDING_LATERAL * 2)
        alto_fondo = self.ancho_juego + (PADDING_TABLERO * 2)
        
        fondo_rect = pygame.Rect(
            self.inicio_x - PADDING_LATERAL, 
            self.inicio_y - PADDING_TABLERO, 
            ancho_fondo, 
            alto_fondo
        )
        
        pygame.draw.rect(self.pantalla, pygame.Color(COLOR_TABLERO), fondo_rect, border_radius=45)

        # Detectar jugada para sonido
        jugada_detectada = False
        for i in range(9):
            if self.tablero_previo[i] == " " and tablero[i] != " ":
                self.animaciones_fichas[i] = 0 
                jugada_detectada = True

        if jugada_detectada and 'colocar' in self.sonidos:
            self.sonidos['colocar'].play()        
        
        self.tablero_previo = list(tablero)

        for i in range(9):
            fila = i // 3
            col = i % 3
            x = self.inicio_x + col * (TAMANO_CASILLA + ESPACIO)
            y = self.inicio_y + fila * (TAMANO_CASILLA + ESPACIO)

            # Sombra y Casilla
            rect_sombra = pygame.Rect(x, y + 10, TAMANO_CASILLA, TAMANO_CASILLA)
            pygame.draw.rect(self.pantalla, pygame.Color(COLOR_CASILLA_SOMBRA_3D), rect_sombra, border_radius=25)
            casilla_rect = pygame.Rect(x, y, TAMANO_CASILLA, TAMANO_CASILLA)
            pygame.draw.rect(self.pantalla, pygame.Color(COLOR_CASILLA), casilla_rect, border_radius=25)

            if tablero[i] != " ":
                color = pygame.Color(COLOR_X if tablero[i] == "X" else COLOR_O)
                txt = self.fuentes['ficha'].render(tablero[i], True, color)

                escala = 1.0
                if i in self.animaciones_fichas:
                    frame_actual = int(self.animaciones_fichas[i])
                    if frame_actual < len(SECUENCIA_PLOP):
                        escala = SECUENCIA_PLOP[frame_actual]
                        self.animaciones_fichas[i] += 1 
                    else:
                        del self.animaciones_fichas[i]
                        escala = 1.0

                if escala != 1.0:
                    txt = pygame.transform.rotozoom(txt, 0, escala)

                rect_texto = txt.get_rect(center=(x + TAMANO_CASILLA / 2, y + TAMANO_CASILLA / 2))
                self.pantalla.blit(txt, rect_texto)

        if combo_ganador:
            self.dibujar_linea_ganadora(combo_ganador)

        if dibujar_boton_redondo(self.pantalla, self.rect_boton, "Nuevo Juego", self.fuentes['boton']):
            boton_hover_actual = "NUEVO"

        # SECCIÓN DERECHA 
        """ t_agente = self.fuentes['subtitulo'].render("Decisiones del Agente", True, pygame.Color(COLOR_BOTON))
        self.pantalla.blit(t_agente, t_agente.get_rect(center=(self.centro_der, 80)))

        altura_clip = ALTO_VENTANA - 140 - 140 
        clip_rect = pygame.Rect(ANCHO_VENTANA//2, 140, ANCHO_VENTANA//2, altura_clip)
        self.pantalla.set_clip(clip_rect)

        # Dibuja el camino reconstruido
        self.dibujar_camino_real(camino_visual, self.centro_der - 100, 160)
            
        self.pantalla.set_clip(None) """

        if dibujar_boton_redondo(self.pantalla, self.rect_boton_arbol, "Ver árbol completo", self.fuentes['boton']):
            boton_hover_actual = "ARBOL"

        if dibujar_boton_salir(self.pantalla, self.rect_boton_salir):
            boton_hover_actual = "SALIR"

        if boton_hover_actual != self.ultimo_boton_hover:
            if boton_hover_actual is not None:
                if 'menu_hover' in self.sonidos:
                    self.sonidos['menu_hover'].play()
            self.ultimo_boton_hover = boton_hover_actual    

        # MODAL 
        if self.modal_abierto:
            self._dibujar_modal_arbol(estructura_arbol)

        pygame.display.flip()   
    
    # --------------------
    # Modal para ver el árbol completo
    # Overlay oscuro con árbol completo, permite arrastrar y cerrar con botón o Esc.
    # --------------------
    def _dibujar_modal_arbol(self, estructura_arbol):
        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((10, 10, 10, 220)) 
        self.pantalla.blit(overlay, (0, 0))

        margin = 40
        caja = pygame.Rect(margin, margin, ANCHO_VENTANA - margin * 2, ALTO_VENTANA - margin * 2)
        pygame.draw.rect(self.pantalla, pygame.Color("#202040"), caja, border_radius=12)
        pygame.draw.rect(self.pantalla, pygame.Color(COLOR_LINEA), caja, width=2, border_radius=12)

        titulo = self.fuentes['subtitulo'].render("Árbol Completo de Decisiones del Agente", True, pygame.Color(COLOR_TEXTO))
        titulo_rect = titulo.get_rect(center=(caja.centerx, caja.y + 25))
        self.pantalla.blit(titulo, titulo_rect)
        
        btn_cerrar = pygame.Rect(caja.right - 160, caja.y + 10, 140, 50)
        color_btn = pygame.Color(COLOR_BOTON_HOVER) if btn_cerrar.collidepoint(pygame.mouse.get_pos()) else pygame.Color(COLOR_BOTON)
        pygame.draw.rect(self.pantalla, color_btn, btn_cerrar, border_radius=12)   
        txt_cerrar = self.fuentes['ui'].render("Cerrar (Esc)", True, pygame.Color(COLOR_TEXTO))
        rect_txt = txt_cerrar.get_rect(center=btn_cerrar.center) 
        self.pantalla.blit(txt_cerrar, rect_txt)     

        inner_x = caja.x + 20
        inner_y = caja.y + 60
        inner_w = caja.width - 40
        inner_h = caja.height - 80
        rect_area_dibujo = pygame.Rect(inner_x, inner_y, inner_w, inner_h)

        previous_clip = self.pantalla.get_clip()
        self.pantalla.set_clip(rect_area_dibujo)

        backup_x, backup_y = self.scroll_x, self.scroll_y
        self.scroll_x, self.scroll_y = self.modal_scroll_x, self.modal_scroll_y

        # Dibujar árbol recursivo usando la lista completa de hermanos de nivel 0
        if estructura_arbol:
            self.dibujar_arbol_recursivo(estructura_arbol, inner_x, inner_x + inner_w, inner_y + 50)

        self.scroll_x, self.scroll_y = backup_x, backup_y
        self.pantalla.set_clip(previous_clip) 

    