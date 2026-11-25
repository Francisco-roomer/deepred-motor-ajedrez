from ui.gui import ChessGUI


def main():
    app = ChessGUI(tiempo_motor=2.5)
    app.ejecutar()


if __name__ == "__main__":
    main()