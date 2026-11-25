import unittest
import chess
from engine.search import DeepRedSearch


class TestDeepRedEngine(unittest.TestCase):
    def test_evita_efecto_horizonte(self):
        # Dama blanca en d4, peón negro en d5 defendido por peón en e6
        board = chess.Board("4k3/8/4p3/3p4/3Q4/8/8/4K3 w - - 0 1")
        motor = DeepRedSearch(tiempo_maximo=1.0, profundidad_max=2)
        jugada = motor.buscar_mejor_jugada(board)
        self.assertNotEqual(jugada.uci(), "d4d5", "El motor cayó en el efecto horizonte y regaló la dama")


if __name__ == "__main__":
    unittest.main()