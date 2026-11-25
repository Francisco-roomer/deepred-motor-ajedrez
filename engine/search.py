import time
import random
import chess
from engine.evaluation import evaluar_tablero, VALORES_PIEZAS


class TiempoAgotado(Exception):
    pass


class DeepRedSearch:
    def __init__(self, tiempo_maximo: float = 1.5, profundidad_max: int = 4):
        self.tiempo_maximo = tiempo_maximo
        self.profundidad_max = profundidad_max
        self.inicio = 0.0
        self.nodos_evaluados = 0
        self.aciertos_tt = 0
        self.profundidad_alcanzada = 0
        self.ultima_evaluacion = 0
        self.tt = {}

        random.seed(42)
        self.z_piezas = {
            (p, c, s): random.getrandbits(64)
            for p in range(1, 7)
            for c in (True, False)
            for s in range(64)
        }
        self.z_turno = random.getrandbits(64)

    def _hash(self, board: chess.Board) -> int:
        h = self.z_turno if board.turn == chess.BLACK else 0
        for sq, p in board.piece_map().items():
            h ^= self.z_piezas[(p.piece_type, p.color, sq)]
        return h

    def _ordenar(self, board: chess.Board, jugadas, mejor_tt=None):
        def peso(m):
            if mejor_tt and m == mejor_tt:
                return 100000
            if board.is_capture(m):
                v = board.piece_at(m.to_square)
                a = board.piece_at(m.from_square)
                return (
                    10000
                    + (VALORES_PIEZAS[v.piece_type] * 10 if v else 100)
                    - (VALORES_PIEZAS[a.piece_type] if a else 0)
                )
            return 0

        return sorted(jugadas, key=peso, reverse=True)

    def _quiescence(self, board: chess.Board, alfa: int, beta: int, maximizando: bool, q_depth: int = 0) -> int:
        self.nodos_evaluados += 1
        if self.nodos_evaluados % 512 == 0 and (time.perf_counter() - self.inicio) > self.tiempo_maximo:
            raise TiempoAgotado()

        stand_pat = evaluar_tablero(board)
        if q_depth >= 6:
            return stand_pat

        if maximizando:
            if stand_pat >= beta:
                return beta
            alfa = max(alfa, stand_pat)
            for m in self._ordenar(board, [x for x in board.legal_moves if board.is_capture(x)]):
                board.push(m)
                try:
                    sc = self._quiescence(board, alfa, beta, False, q_depth + 1)
                finally:
                    board.pop()
                alfa = max(alfa, sc)
                if alfa >= beta:
                    break
            return alfa
        else:
            if stand_pat <= alfa:
                return alfa
            beta = min(beta, stand_pat)
            for m in self._ordenar(board, [x for x in board.legal_moves if board.is_capture(x)]):
                board.push(m)
                try:
                    sc = self._quiescence(board, alfa, beta, True, q_depth + 1)
                finally:
                    board.pop()
                beta = min(beta, sc)
                if beta <= alfa:
                    break
            return beta

    def _alfabeta(self, board: chess.Board, prof: int, alfa: int, beta: int, maximizando: bool) -> int:
        self.nodos_evaluados += 1
        if self.nodos_evaluados % 512 == 0 and (time.perf_counter() - self.inicio) > self.tiempo_maximo:
            raise TiempoAgotado()

        h = self._hash(board)
        entrada = self.tt.get(h)
        mejor_tt = entrada[2] if entrada else None
        if entrada and entrada[0] >= prof:
            self.aciertos_tt += 1
            return entrada[1]

        if board.is_game_over():
            return evaluar_tablero(board)
        if prof <= 0:
            return self._quiescence(board, alfa, beta, maximizando, 0)

        jugadas = self._ordenar(board, list(board.legal_moves), mejor_tt)
        mejor_mov = jugadas[0]

        if maximizando:
            val = -10**9
            for m in jugadas:
                board.push(m)
                try:
                    ev = self._alfabeta(board, prof - 1, alfa, beta, False)
                finally:
                    board.pop()
                if ev > val:
                    val, mejor_mov = ev, m
                alfa = max(alfa, val)
                if beta <= alfa:
                    break
        else:
            val = 10**9
            for m in jugadas:
                board.push(m)
                try:
                    ev = self._alfabeta(board, prof - 1, alfa, beta, True)
                finally:
                    board.pop()
                if ev < val:
                    val, mejor_mov = ev, m
                beta = min(beta, val)
                if beta <= alfa:
                    break

        self.tt[h] = (prof, val, mejor_mov)
        return val

    def buscar_mejor_jugada(self, board_original: chess.Board, visualizar_en_vivo: bool = False):
        board = board_original if visualizar_en_vivo else board_original.copy()
        self.inicio = time.perf_counter()
        self.nodos_evaluados = 0
        self.aciertos_tt = 0

        jugadas = list(board.legal_moves)
        mejor_global = jugadas[0]
        maximizando = board.turn == chess.WHITE

        for prof in range(1, self.profundidad_max + 1):
            try:
                mejor_iter = mejor_global
                mejor_val = -10**9 if maximizando else 10**9
                for m in self._ordenar(board, jugadas, mejor_global):
                    board.push(m)
                    try:
                        val = self._alfabeta(board, prof - 1, -10**9, 10**9, not maximizando)
                    finally:
                        board.pop()
                    if (maximizando and val > mejor_val) or (not maximizando and val < mejor_val):
                        mejor_val, mejor_iter = val, m
                mejor_global = mejor_iter
                self.ultima_evaluacion = mejor_val
                self.profundidad_alcanzada = prof
                if abs(mejor_val) >= 90000:
                    break
            except TiempoAgotado:
                break

        return mejor_global