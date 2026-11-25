import threading
import pygame
import chess
from engine.search import DeepRedSearch

# Paleta de colores DeepRed (Minimalista oscuro + acento carmesí)
COLOR_FONDO = (20, 22, 26)
COLOR_PANEL = (28, 30, 36)
COLOR_CASILLA_CLARA = (226, 228, 232)
COLOR_CASILLA_OSCURA = (112, 128, 144)
COLOR_SELECCION = (220, 53, 69, 140)
COLOR_ULTIMA_JUGADA = (235, 180, 65, 130)
COLOR_MOV_LEGAL = (220, 53, 69, 130)
COLOR_ACENTO_ROJO = (220, 53, 69)
COLOR_TEXTO = (240, 242, 245)
COLOR_TEXTO_SEC = (160, 165, 175)

UNICODE_PIEZAS = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}


class ChessGUI:
    def __init__(self, tiempo_motor: float = 2.5):
        pygame.init()
        self.tam_tablero = 640
        self.tam_casilla = self.tam_tablero // 8
        self.ancho_panel = 260
        self.ancho_total = self.tam_tablero + self.ancho_panel
        self.alto_total = self.tam_tablero

        self.pantalla = pygame.display.set_mode((self.ancho_total, self.alto_total))
        pygame.display.set_caption("DeepRed — Classical AI Chess Engine")
        self.reloj = pygame.time.Clock()

        # Fuentes con soporte Unicode para piezas de ajedrez
        self.fuente_piezas = pygame.font.SysFont("segoeuisymbol,dejavusans,arial", 58)
        self.fuente_ui = pygame.font.SysFont("segoeui,arial", 17)
        self.fuente_sub = pygame.font.SysFont("segoeui,arial", 14)
        self.fuente_titulo = pygame.font.SysFont("segoeui,arial", 24, bold=True)

        self.board = chess.Board()
        self.motor = DeepRedSearch(tiempo_maximo=tiempo_motor, profundidad_max=6)

        self.casilla_seleccionada = None
        self.movimientos_validos_sel = []
        self.ultima_jugada = None
        self.motor_pensando = False

    def _coordenadas_a_casilla(self, pos_raton):
        x, y = pos_raton
        if x >= self.tam_tablero or y >= self.tam_tablero:
            return None
        col = x // self.tam_casilla
        fila = 7 - (y // self.tam_casilla)
        return chess.square(col, fila)

    def _casilla_a_rect(self, casilla: int) -> pygame.Rect:
        col = chess.square_file(casilla)
        fila = 7 - chess.square_rank(casilla)
        return pygame.Rect(col * self.tam_casilla, fila * self.tam_casilla, self.tam_casilla, self.tam_casilla)

    def _dibujar_tablero(self):
        for fila in range(8):
            for col in range(8):
                color = COLOR_CASILLA_CLARA if (fila + col) % 2 == 0 else COLOR_CASILLA_OSCURA
                rect = pygame.Rect(col * self.tam_casilla, fila * self.tam_casilla, self.tam_casilla, self.tam_casilla)
                pygame.draw.rect(self.pantalla, color, rect)

        # Resaltar última jugada
        if self.ultima_jugada:
            for sq in (self.ultima_jugada.from_square, self.ultima_jugada.to_square):
                s = pygame.Surface((self.tam_casilla, self.tam_casilla), pygame.SRCALPHA)
                s.fill(COLOR_ULTIMA_JUGADA)
                self.pantalla.blit(s, self._casilla_a_rect(sq).topleft)

        # Resaltar casilla del Rey en rojo intenso si hay Jaque
        if self.board.is_check():
            rey_sq = self.board.king(self.board.turn)
            if rey_sq is not None:
                s = pygame.Surface((self.tam_casilla, self.tam_casilla), pygame.SRCALPHA)
                s.fill((220, 20, 40, 210))
                self.pantalla.blit(s, self._casilla_a_rect(rey_sq).topleft)

        # Resaltar casilla seleccionada
        if self.casilla_seleccionada is not None:
            s = pygame.Surface((self.tam_casilla, self.tam_casilla), pygame.SRCALPHA)
            s.fill(COLOR_SELECCION)
            self.pantalla.blit(s, self._casilla_a_rect(self.casilla_seleccionada).topleft)

        # Puntos indicadores de movimientos legales
        for mov in self.movimientos_validos_sel:
            rect = self._casilla_a_rect(mov.to_square)
            s = pygame.Surface((self.tam_casilla, self.tam_casilla), pygame.SRCALPHA)
            pygame.draw.circle(s, COLOR_MOV_LEGAL, (self.tam_casilla // 2, self.tam_casilla // 2), 13)
            self.pantalla.blit(s, rect.topleft)

    def _dibujar_piezas(self):
        en_jaque = self.board.is_check()
        rey_sq = self.board.king(self.board.turn) if en_jaque else None
        piezas_salvadoras = {m.from_square for m in self.board.legal_moves} if en_jaque else set()

        for casilla in chess.SQUARES:
            pieza = self.board.piece_at(casilla)
            if pieza:
                simbolo = UNICODE_PIEZAS[pieza.symbol()]
                rect = self._casilla_a_rect(casilla)
                color_pieza = (255, 255, 255) if pieza.color == chess.WHITE else (18, 20, 24)
                borde_color = (18, 20, 24) if pieza.color == chess.WHITE else (235, 235, 240)

                texto_sombra = self.fuente_piezas.render(simbolo, True, borde_color)
                texto = self.fuente_piezas.render(simbolo, True, color_pieza)

                # Atenuar piezas que no pueden moverse durante un jaque
                if en_jaque and casilla != rey_sq and casilla not in piezas_salvadoras:
                    texto_sombra.set_alpha(80)
                    texto.set_alpha(80)

                rect_sombra = texto_sombra.get_rect(center=(rect.centerx + 1, rect.centery + 1))
                self.pantalla.blit(texto_sombra, rect_sombra)

                rect_texto = texto.get_rect(center=rect.center)
                self.pantalla.blit(texto, rect_texto)

    def _dibujar_panel_lateral(self):
        panel_rect = pygame.Rect(self.tam_tablero, 0, self.ancho_panel, self.alto_total)
        pygame.draw.rect(self.pantalla, COLOR_PANEL, panel_rect)
        pygame.draw.line(self.pantalla, COLOR_ACENTO_ROJO, (self.tam_tablero, 0), (self.tam_tablero, self.alto_total), 2)

        x_base = self.tam_tablero + 22
        titulo = self.fuente_titulo.render("DeepRed", True, COLOR_TEXTO)
        subtitulo = self.fuente_sub.render("Alpha-Beta Heuristic Engine", True, COLOR_ACENTO_ROJO)
        self.pantalla.blit(titulo, (x_base, 24))
        self.pantalla.blit(subtitulo, (x_base, 54))

        # Barra de evaluación f(s)
        eval_cp = self.motor.ultima_evaluacion
        eval_peones = max(-10.0, min(10.0, eval_cp / 100.0))
        proporcion_blancas = 0.5 + (eval_peones / 20.0)

        barra_x, barra_y, barra_w, barra_h = x_base, 92, 215, 20
        pygame.draw.rect(self.pantalla, (45, 48, 56), (barra_x, barra_y, barra_w, barra_h), border_radius=4)
        pygame.draw.rect(
            self.pantalla, (240, 240, 245),
            (barra_x, barra_y, int(barra_w * proporcion_blancas), barra_h),
            border_radius=4
        )

        # Telemetría en tiempo real con alerta de Jaque / Jaque Mate
        color_estado = COLOR_TEXTO
        if self.board.is_checkmate():
            estado = f"¡JAQUE MATE! ({self.board.result()})"
            color_estado = COLOR_ACENTO_ROJO
        elif self.board.is_game_over():
            estado = f"Fin: {self.board.result()}"
        elif self.motor_pensando:
            estado = "Calculando árbol..."
        elif self.board.is_check():
            estado = "¡JAQUE! Protege al Rey"
            color_estado = COLOR_ACENTO_ROJO
        else:
            estado = "Tu turno (Blancas)"

        surf_estado = self.fuente_ui.render(f"Estado: {estado}", True, color_estado)
        self.pantalla.blit(surf_estado, (x_base, 138))

        metricas = [
            f"Eval f(s): {eval_cp / 100:+.2f}",
            f"Profundidad: {self.motor.profundidad_alcanzada}",
            f"Nodos: {self.motor.nodos_evaluados:,}",
            f"TT Hits: {self.motor.aciertos_tt:,}",
        ]

        for i, linea in enumerate(metricas):
            surf = self.fuente_ui.render(linea, True, COLOR_TEXTO)
            self.pantalla.blit(surf, (x_base, 170 + i * 32))

        ayuda = self.fuente_sub.render("[R] Reiniciar partida", True, COLOR_TEXTO_SEC)
        self.pantalla.blit(ayuda, (x_base, self.alto_total - 40))

    def _turno_motor_async(self):
        self.motor_pensando = True
        jugada = self.motor.buscar_mejor_jugada(self.board)
        if jugada and not self.board.is_game_over():
            self.board.push(jugada)
            self.ultima_jugada = jugada
        self.motor_pensando = False

    def _manejar_clic(self, pos_raton):
        if self.motor_pensando or self.board.is_game_over() or self.board.turn != chess.WHITE:
            return

        casilla = self._coordenadas_a_casilla(pos_raton)
        if casilla is None:
            return

        if self.casilla_seleccionada is not None:
            jugada_candidata = None
            for mov in self.movimientos_validos_sel:
                if mov.to_square == casilla:
                    if mov.promotion:
                        jugada_candidata = chess.Move(self.casilla_seleccionada, casilla, promotion=chess.QUEEN)
                    else:
                        jugada_candidata = mov
                    break

            if jugada_candidata and jugada_candidata in self.board.legal_moves:
                self.board.push(jugada_candidata)
                self.ultima_jugada = jugada_candidata
                self.casilla_seleccionada = None
                self.movimientos_validos_sel = []

                if not self.board.is_game_over():
                    threading.Thread(target=self._turno_motor_async, daemon=True).start()
                return

        pieza = self.board.piece_at(casilla)
        if pieza and pieza.color == chess.WHITE:
            self.casilla_seleccionada = casilla
            self.movimientos_validos_sel = [
                m for m in self.board.legal_moves if m.from_square == casilla
            ]
        else:
            self.casilla_seleccionada = None
            self.movimientos_validos_sel = []

    def ejecutar(self):
        corriendo = True
        while corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self._manejar_clic(evento.pos)
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                    if not self.motor_pensando:
                        self.board.reset()
                        self.ultima_jugada = None
                        self.casilla_seleccionada = None
                        self.movimientos_validos_sel = []

            self._dibujar_tablero()
            self._dibujar_piezas()
            self._dibujar_panel_lateral()
            pygame.display.flip()
            self.reloj.tick(60)

        pygame.quit()