import gradio as gr
import chess
from engine.search import DeepRedSearch

UNICODE_PIEZAS = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

CUSTOM_CSS = """
body, .gradio-container {
    background-color: #14161a !important;
    color: #f0f2f5 !important;
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}
footer { display: none !important; }

.contenedor-maestro {
    max-width: 920px !important;
    margin: 0 auto !important;
    padding: 0 !important;
}

.deepred-app {
    display: flex;
    flex-wrap: wrap;
    width: 100%;
    background-color: #1c1e24;
    border-radius: 10px 10px 0 0;
    overflow: hidden;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
    border: 1px solid #2b2e38;
    border-bottom: none;
}

.tablero-wrapper {
    flex: 1 1 520px;
    aspect-ratio: 1 / 1;
    max-width: 600px;
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    grid-template-rows: repeat(8, 1fr);
    user-select: none;
}

.casilla {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: clamp(28px, 5.5vw, 54px);
    line-height: 1;
    transition: filter 0.15s ease, background-color 0.2s ease;
}
.casilla:hover { filter: brightness(1.06); }
.casilla.clara { background-color: #e2e4e8; }
.casilla.oscura { background-color: #708090; }
.casilla.ultima { background-color: #c9b458 !important; }
.casilla.seleccionada { background-color: rgba(220, 53, 69, 0.72) !important; }

/* Resplandor de alerta cuando el Rey está en Jaque */
@keyframes pulso-jaque {
    0% { box-shadow: inset 0 0 12px 4px rgba(255, 25, 45, 0.85); }
    50% { box-shadow: inset 0 0 24px 10px rgba(255, 25, 45, 1); }
    100% { box-shadow: inset 0 0 12px 4px rgba(255, 25, 45, 0.85); }
}

.casilla.rey-en-jaque {
    background: radial-gradient(circle, #ff3b4e 15%, #b81424 85%) !important;
    animation: pulso-jaque 1.4s infinite ease-in-out;
    z-index: 2;
}

.pieza-blanca {
    color: #ffffff;
    text-shadow: 0 2px 3px rgba(0, 0, 0, 0.85), 0 0 1px #000;
    pointer-events: none;
    transition: opacity 0.2s ease, transform 0.2s ease;
}
.pieza-negra {
    color: #14161a;
    text-shadow: 0 1px 1px rgba(255, 255, 255, 0.35);
    pointer-events: none;
    transition: opacity 0.2s ease;
}

/* Atenuar piezas que no pueden moverse durante el jaque */
.pieza-atenuada {
    opacity: 0.32 !important;
}

/* Destacar el Rey atacado */
.pieza-rey-alerta {
    transform: scale(1.1);
    filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.9));
}

.punto-legal {
    width: 26%;
    height: 26%;
    border-radius: 50%;
    background-color: rgba(220, 53, 69, 0.85);
    position: absolute;
    pointer-events: none;
}

.panel-lateral {
    flex: 1 1 260px;
    background-color: #1c1e24;
    border-left: 2px solid #dc3545;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.titulo-dr {
    font-size: 26px;
    font-weight: 700;
    color: #ffffff !important;
    margin: 0;
}
.subtitulo-dr {
    font-size: 13px;
    color: #dc3545 !important;
    margin: 2px 0 18px 0;
    font-weight: 600;
}

.barra-eval-bg {
    width: 100%;
    height: 18px;
    background-color: #2d3038;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 20px;
}
.barra-eval-fill {
    height: 100%;
    background-color: #f0f2f5;
    transition: width 0.35s ease;
}

.metrica-item {
    font-size: 15px;
    color: #e2e4e8 !important;
    margin-bottom: 12px;
}
.metrica-item strong {
    color: #ffffff !important;
    font-weight: 600;
}
.texto-alerta-jaque {
    color: #ff4d5e !important;
    font-weight: 700 !important;
}

.nota-web {
    font-size: 12px;
    color: #b0b6c3 !important;
    border-top: 1px solid #2d3038;
    padding-top: 12px;
    margin-top: 16px;
    line-height: 1.45;
}
.nota-web code {
    background-color: #2d3038 !important;
    color: #ff6b7a !important;
    padding: 2px 5px;
    border-radius: 4px;
    font-family: monospace;
}

/* Barra inferior de controles oscura unificada */
.barra-controles {
    max-width: 920px !important;
    margin: 0 auto !important;
    background-color: #181a20 !important;
    border: 1px solid #2b2e38 !important;
    border-top: 1px solid #2d3038 !important;
    border-radius: 0 0 10px 10px !important;
    padding: 14px 20px !important;
    align-items: center !important;
}

/* Forzar tema oscuro dentro de todo el componente Slider */
.barra-controles .block,
.barra-controles .wrap,
.barra-controles .head {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.barra-controles label span,
.barra-controles span {
    color: #cfd4de !important;
}
.barra-controles input[type="number"] {
    background-color: #252830 !important;
    color: #ffffff !important;
    border: 1px solid #3a3f4b !important;
    border-radius: 4px !important;
}
.barra-controles input[type="range"] {
    accent-color: #dc3545 !important;
}

#btn-reset-dr {
    background-color: #252830 !important;
    color: #f0f2f5 !important;
    border: 1px solid #dc3545 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    height: 42px !important;
    cursor: pointer !important;
    transition: background-color 0.15s ease !important;
}
#btn-reset-dr:hover {
    background-color: #dc3545 !important;
    color: #ffffff !important;
}

#bridge-sq, #bridge-btn {
    position: fixed !important;
    left: -9999px !important;
    top: -9999px !important;
    width: 10px !important;
    height: 10px !important;
}

@media (max-width: 780px) {
    .panel-lateral {
        border-left: none;
        border-top: 2px solid #dc3545;
    }
}
"""

JS_CLICK_HANDLER = """
() => {
    window.seleccionarCasillaDeepRed = function(sqName) {
        const inputEl = document.querySelector('#bridge-sq textarea') || document.querySelector('#bridge-sq input');
        const btnEl = document.querySelector('#bridge-btn');
        if (inputEl && btnEl) {
            const proto = inputEl.tagName === 'TEXTAREA'
                ? window.HTMLTextAreaElement.prototype
                : window.HTMLInputElement.prototype;
            const nativeSetter = Object.getOwnPropertyDescriptor(proto, "value").set;
            nativeSetter.call(inputEl, sqName);
            inputEl.dispatchEvent(new Event('input', { bubbles: true }));
            inputEl.dispatchEvent(new Event('change', { bubbles: true }));
            setTimeout(() => btnEl.click(), 40);
        }
    };
}
"""


def generar_html_interfaz(board: chess.Board, seleccionada=None, ultima_jugada=None,
                          eval_cp=0, prof=0, nodos=0, tt_hits=0, estado_texto="Tu turno (Blancas)"):
    destinos_legales = set()
    if seleccionada is not None:
        destinos_legales = {m.to_square for m in board.legal_moves if m.from_square == seleccionada}

    ultimas_sq = set()
    if ultima_jugada:
        ultimas_sq = {ultima_jugada.from_square, ultima_jugada.to_square}

    en_jaque = board.is_check()
    casilla_rey_jaque = board.king(board.turn) if en_jaque else None
    piezas_salvadoras = {m.from_square for m in board.legal_moves} if en_jaque else set()

    celdas_html = []
    for fila in range(7, -1, -1):
        for col in range(8):
            sq = chess.square(col, fila)
            sq_name = chess.square_name(sq)
            es_clara = ((7 - fila) + col) % 2 == 0
            clases = ["casilla", "clara" if es_clara else "oscura"]

            if sq in ultimas_sq:
                clases.append("ultima")
            if sq == seleccionada:
                clases.append("seleccionada")
            if sq == casilla_rey_jaque:
                clases.append("rey-en-jaque")

            pieza = board.piece_at(sq)
            pieza_html = ""
            if pieza:
                simbolo = UNICODE_PIEZAS[pieza.symbol()]
                clases_pieza = ["pieza-blanca" if pieza.color == chess.WHITE else "pieza-negra"]

                if en_jaque:
                    if sq == casilla_rey_jaque:
                        clases_pieza.append("pieza-rey-alerta")
                    elif sq not in piezas_salvadoras:
                        clases_pieza.append("pieza-atenuada")

                pieza_html = f"<span class='{' '.join(clases_pieza)}'>{simbolo}</span>"

            punto_html = "<div class='punto-legal'></div>" if sq in destinos_legales else ""

            celdas_html.append(
                f"<div class='{' '.join(clases)}' onclick=\"window.seleccionarCasillaDeepRed('{sq_name}')\">"
                f"{pieza_html}{punto_html}</div>"
            )

    eval_peones = max(-10.0, min(10.0, eval_cp / 100.0))
    porcentaje_blancas = int((0.5 + (eval_peones / 20.0)) * 100)

    clase_estado = "texto-alerta-jaque" if en_jaque else ""

    return f"""
    <div class="deepred-app">
        <div class="tablero-wrapper">
            {''.join(celdas_html)}
        </div>
        <div class="panel-lateral">
            <div>
                <h1 class="titulo-dr">DeepRed</h1>
                <p class="subtitulo-dr">Alpha-Beta Heuristic Engine</p>
                <div class="barra-eval-bg">
                    <div class="barra-eval-fill" style="width: {porcentaje_blancas}%;"></div>
                </div>
                <div class="metrica-item">Estado: <strong class="{clase_estado}">{estado_texto}</strong></div>
                <div class="metrica-item">Eval f(s): <strong>{eval_cp / 100:+.2f}</strong></div>
                <div class="metrica-item">Profundidad: <strong>{prof}</strong></div>
                <div class="metrica-item">Nodos: <strong>{nodos:,}</strong></div>
                <div class="metrica-item">TT Hits: <strong>{tt_hits:,}</strong></div>
            </div>
            <div class="nota-web">
                Toca o haz clic en una pieza blanca y luego en su destino. Demo web acotada a CPU compartida; ejecuta <code>main.py</code> en local para máximo rendimiento.
            </div>
        </div>
    </div>
    """


def obtener_texto_estado(board: chess.Board) -> str:
    if board.is_checkmate():
        return f"¡JAQUE MATE! ({board.result()})"
    if board.is_game_over():
        return f"Tablas / Fin ({board.result()})"
    if board.is_check():
        return "¡JAQUE! Protege al Rey"
    return "Tu turno (Blancas)"


def procesar_clic(sq_name: str, estado: dict, tiempo_motor: float):
    board: chess.Board = estado["board"]
    seleccionada = estado["seleccionada"]
    ultima_jugada = estado["ultima_jugada"]

    if board.is_game_over() or board.turn != chess.WHITE or not sq_name:
        return estado, generar_html_interfaz(
            board, None, ultima_jugada, estado["eval_cp"], estado["prof"],
            estado["nodos"], estado["tt_hits"], obtener_texto_estado(board)
        )

    try:
        casilla = chess.parse_square(sq_name.strip())
    except ValueError:
        return estado, generar_html_interfaz(
            board, seleccionada, ultima_jugada, estado["eval_cp"], estado["prof"],
            estado["nodos"], estado["tt_hits"], obtener_texto_estado(board)
        )

    if seleccionada is not None:
        jugada_candidata = None
        for mov in board.legal_moves:
            if mov.from_square == seleccionada and mov.to_square == casilla:
                if mov.promotion:
                    jugada_candidata = chess.Move(seleccionada, casilla, promotion=chess.QUEEN)
                else:
                    jugada_candidata = mov
                break

        if jugada_candidata and jugada_candidata in board.legal_moves:
            board.push(jugada_candidata)
            estado["ultima_jugada"] = jugada_candidata
            estado["seleccionada"] = None

            if board.is_game_over():
                return estado, generar_html_interfaz(
                    board, None, jugada_candidata, estado["eval_cp"], estado["prof"],
                    estado["nodos"], estado["tt_hits"], obtener_texto_estado(board)
                )

            motor = DeepRedSearch(tiempo_maximo=min(float(tiempo_motor), 2.5), profundidad_max=5)
            mov_motor = motor.buscar_mejor_jugada(board)
            board.push(mov_motor)

            estado["ultima_jugada"] = mov_motor
            estado["eval_cp"] = motor.ultima_evaluacion
            estado["prof"] = motor.profundidad_alcanzada
            estado["nodos"] = motor.nodos_evaluados
            estado["tt_hits"] = motor.aciertos_tt

            return estado, generar_html_interfaz(
                board, None, mov_motor, estado["eval_cp"], estado["prof"],
                estado["nodos"], estado["tt_hits"], obtener_texto_estado(board)
            )

    pieza = board.piece_at(casilla)
    if pieza and pieza.color == chess.WHITE:
        estado["seleccionada"] = casilla
    else:
        estado["seleccionada"] = None

    return estado, generar_html_interfaz(
        board, estado["seleccionada"], ultima_jugada, estado["eval_cp"],
        estado["prof"], estado["nodos"], estado["tt_hits"], obtener_texto_estado(board)
    )


def reiniciar_partida():
    nuevo_estado = {
        "board": chess.Board(),
        "seleccionada": None,
        "ultima_jugada": None,
        "eval_cp": 0,
        "prof": 0,
        "nodos": 0,
        "tt_hits": 0
    }
    return nuevo_estado, generar_html_interfaz(nuevo_estado["board"])


estado_inicial = {
    "board": chess.Board(),
    "seleccionada": None,
    "ultima_jugada": None,
    "eval_cp": 0,
    "prof": 0,
    "nodos": 0,
    "tt_hits": 0
}

with gr.Blocks(title="DeepRed — Classical AI Chess Engine", css=CUSTOM_CSS, js=JS_CLICK_HANDLER) as demo:
    estado_juego = gr.State(estado_inicial)

    with gr.Column(elem_classes="contenedor-maestro"):
        visor_principal = gr.HTML(value=generar_html_interfaz(estado_inicial["board"]))

        with gr.Row(elem_classes="barra-controles"):
            with gr.Column(scale=3):
                slider_tiempo = gr.Slider(
                    minimum=0.5, maximum=2.5, value=1.5, step=0.5,
                    label="Tiempo de búsqueda DeepRed (segundos)"
                )
            with gr.Column(scale=1):
                btn_reiniciar = gr.Button("Reiniciar partida", elem_id="btn-reset-dr")

    casilla_clicada = gr.Textbox(elem_id="bridge-sq", lines=1)
    btn_puente = gr.Button("Ejecutar", elem_id="bridge-btn")

    btn_puente.click(
        fn=procesar_clic,
        inputs=[casilla_clicada, estado_juego, slider_tiempo],
        outputs=[estado_juego, visor_principal]
    )
    btn_reiniciar.click(
        fn=reiniciar_partida,
        inputs=[],
        outputs=[estado_juego, visor_principal]
    )

if __name__ == "__main__":
    demo.launch()