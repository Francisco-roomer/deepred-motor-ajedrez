import time
import chess
import chess.polyglot
from .evaluation import evaluar_tablero, VALORES_PIEZAS

EXACTO = 0
COTA_INFERIOR = 1
COTA_SUPERIOR = 2


class DeepRedSearch:
    def __init__(self, tiempo_maximo: float = 2.5, profundidad_max: int = 6):
        self.tiempo_maximo = tiempo_maximo
        self.profundidad_max = profundidad_max
        self.nodos_evaluados = 0
        self.aciertos_tt = 0
        self.tabla_transposicion = {}
        self.ultima_evaluacion = 0
        self.profundidad_alcanzada = 0

    def _puntuar_jugada(self, board: chess.Board, jugada: chess.Move) -> int:
        puntuacion = 0
        if board.is_capture(jugada):
            atacante = board.piece_at(jugada.from_square)
            victima = board.piece_at(jugada.to_square)
            val_atacante = VALORES_PIEZAS[atacante.piece_type] if atacante else 0
            val_victima = VALORES_PIEZAS[victima.piece_type] if victima else VALORES_PIEZAS[chess.PAWN]
            puntuacion += 10 * val_victima - val_atacante

        if jugada.promotion:
            puntuacion += VALORES_PIEZAS[jugada.promotion]

        return puntuacion

    def _obtener_jugadas_ordenadas(self, board: chess.Board):
        return sorted(board.legal_moves, key=lambda j: self._puntuar_jugada(board, j), reverse=True)

    def _obtener_capturas_ordenadas(self, board: chess.Board):
        capturas = [j for j in board.legal_moves if board.is_capture(j)]
        return sorted(capturas, key=lambda j: self._puntuar_jugada(board, j), reverse=True)

    def _quiescence(self, board: chess.Board, alfa: float, beta: float, es_maximizador: bool) -> float:
        self.nodos_evaluados += 1
        stand_pat = evaluar_tablero(board)

        if es_maximizador:
            if stand_pat >= beta:
                return beta
            if alfa < stand_pat:
                alfa = stand_pat

            for jugada in self._obtener_capturas_ordenadas(board):
                board.push(jugada)
                valor = self._quiescence(board, alfa, beta, False)
                board.pop()
                if valor >= beta:
                    return beta
                if valor > alfa:
                    alfa = valor
            return alfa
        else:
            if stand_pat <= alfa:
                return alfa
            if beta > stand_pat:
                beta = stand_pat

            for jugada in self._obtener_capturas_ordenadas(board):
                board.push(jugada)
                valor = self._quiescence(board, alfa, beta, True)
                board.pop()
                if valor <= alfa:
                    return alfa
                if valor < beta:
                    beta = valor
            return beta

    def _minimax_tt(self, board: chess.Board, profundidad: int, alfa: float, beta: float, es_maximizador: bool) -> float:
        alfa_original = alfa
        beta_original = beta
        hash_pos = chess.polyglot.zobrist_hash(board)

        entrada = self.tabla_transposicion.get(hash_pos)
        if entrada is not None and entrada["profundidad"] >= profundidad:
            self.aciertos_tt += 1
            val_guardado = entrada["valor"]
            bandera = entrada["bandera"]

            if bandera == EXACTO:
                return val_guardado
            elif bandera == COTA_INFERIOR:
                alfa = max(alfa, val_guardado)
            elif bandera == COTA_SUPERIOR:
                beta = min(beta, val_guardado)

            if alfa >= beta:
                return val_guardado

        if board.is_game_over():
            self.nodos_evaluados += 1
            return evaluar_tablero(board)

        if profundidad == 0:
            return self._quiescence(board, alfa, beta, es_maximizador)

        self.nodos_evaluados += 1
        jugadas = self._obtener_jugadas_ordenadas(board)

        if es_maximizador:
            mejor_valor = -float('inf')
            for jugada in jugadas:
                board.push(jugada)
                valor = self._minimax_tt(board, profundidad - 1, alfa, beta, False)
                board.pop()
                mejor_valor = max(mejor_valor, valor)
                alfa = max(alfa, mejor_valor)
                if beta <= alfa:
                    break
        else:
            mejor_valor = float('inf')
            for jugada in jugadas:
                board.push(jugada)
                valor = self._minimax_tt(board, profundidad - 1, alfa, beta, True)
                board.pop()
                mejor_valor = min(mejor_valor, valor)
                beta = min(beta, mejor_valor)
                if beta <= alfa:
                    break

        if mejor_valor <= alfa_original:
            bandera = COTA_SUPERIOR
        elif mejor_valor >= beta_original:
            bandera = COTA_INFERIOR
        else:
            bandera = EXACTO

        self.tabla_transposicion[hash_pos] = {
            "profundidad": profundidad,
            "valor": mejor_valor,
            "bandera": bandera
        }
        return mejor_valor

    def buscar_mejor_jugada(self, board: chess.Board) -> chess.Move:
        self.nodos_evaluados = 0
        self.aciertos_tt = 0
        self.tabla_transposicion.clear()

        inicio = time.time()
        es_blancas = (board.turn == chess.WHITE)
        mejor_jugada_global = None
        mejor_valor_global = 0

        for prof in range(1, self.profundidad_max + 1):
            if (time.time() - inicio) > self.tiempo_maximo * 0.65 and mejor_jugada_global is not None:
                break

            mejor_jugada_actual = None
            mejor_valor_actual = -float('inf') if es_blancas else float('inf')
            alfa = -float('inf')
            beta = float('inf')

            jugadas = self._obtener_jugadas_ordenadas(board)
            if mejor_jugada_global in jugadas:
                jugadas.remove(mejor_jugada_global)
                jugadas.insert(0, mejor_jugada_global)

            tiempo_agotado = False
            for jugada in jugadas:
                if (time.time() - inicio) > self.tiempo_maximo and mejor_jugada_global is not None:
                    tiempo_agotado = True
                    break

                board.push(jugada)
                valor = self._minimax_tt(board, prof - 1, alfa, beta, not es_blancas)
                board.pop()

                if es_blancas:
                    if valor > mejor_valor_actual:
                        mejor_valor_actual = valor
                        mejor_jugada_actual = jugada
                    alfa = max(alfa, mejor_valor_actual)
                else:
                    if valor < mejor_valor_actual:
                        mejor_valor_actual = valor
                        mejor_jugada_actual = jugada
                    beta = min(beta, mejor_valor_actual)

            if not tiempo_agotado and mejor_jugada_actual is not None:
                mejor_jugada_global = mejor_jugada_actual
                mejor_valor_global = mejor_valor_actual
                self.profundidad_alcanzada = prof

        self.ultima_evaluacion = mejor_valor_global
        tiempo_total = time.time() - inicio
        print(
            f"[DeepRed] Prof: {self.profundidad_alcanzada} | Jugada: {mejor_jugada_global} | "
            f"Eval: {self.ultima_evaluacion} | Nodos: {self.nodos_evaluados} | "
            f"TT Hits: {self.aciertos_tt} | Tiempo: {tiempo_total:.2f}s"
        )
        return mejor_jugada_global