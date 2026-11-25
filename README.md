# DeepRed — Motor de Ajedrez en IA Clásica

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/UI_Web-Gradio-FF7C00?logo=gradio&logoColor=white)](https://www.gradio.app/)
[![Pygame](https://img.shields.io/badge/UI_Desktop-Pygame-00A86B?logo=python&logoColor=white)](https://www.pygame.org/)
[![Live Demo](https://img.shields.io/badge/Demo_en_Vivo-Render-46E3B7?logo=render&logoColor=black)](https://deepred-motor-ajedrez.onrender.com/)

**DeepRed** es un motor de ajedrez construido desde cero en Python bajo el paradigma de **Inteligencia Artificial Clásica y Búsqueda Heurística**. Combina algoritmos de teoría de juegos adversarios, optimización de memoria y evaluación posicional inspirada en las arquitecturas clásicas de decisión simbólica.

**Demo en vivo:** [deepred-motor-ajedrez.onrender.com](https://deepred-motor-ajedrez.onrender.com/)  
*(Nota: Al alojarse en una instancia gratuita de Render, el servidor puede tardar entre 30 y 50 segundos en despertar tras un periodo de inactividad).*

---

## Arquitectura y Algoritmos Implementados

El núcleo de decisión (`engine/search.py` y `engine/evaluation.py`) opera sin redes neuronales ni libros de apertura externos, calculando variantes tácticas y posicionales en tiempo real mediante:

1. **Minimax con Poda Alfa-Beta (*Alpha-Beta Pruning*):**  
   Explora el árbol de juego descartando ramas matemáticamente subóptimas cuando $\beta \le \alpha$, reduciendo drásticamente el factor de ramificación efectivo.
2. **Profundización Iterativa (*Iterative Deepening*):**  
   Ejecuta búsquedas progresivas desde profundidad $d = 1$ hasta $d_{\max}$ bajo un presupuesto estricto de tiempo (`tiempo_maximo`), garantizando siempre una jugada válida incluso si se agota el reloj.
3. **Búsqueda de Quietud (*Quiescence Search*):**  
   Mitiga el **efecto horizonte** extendiendo la evaluación en posiciones tácticas activas (capturas encadenadas) hasta alcanzar una posición estable antes de asignar una puntuación estática.
4. **Ordenamiento de Jugadas (MVV-LVA + PV Move):**  
   Prioriza la mejor jugada previa de la tabla de transposición y ordena las capturas mediante *Most Valuable Victim – Least Valuable Aggressor* para maximizar los cortes Alfa-Beta tempranos.
5. **Hashing de Zobrist y Tabla de Transposición:**  
   Codifica cada estado del tablero mediante operaciones XOR de 64 bits (`Zobrist Hashing`) para almacenar evaluaciones previas y evitar recalcular posiciones alcanzadas por distintos órdenes de jugadas.
6. **Función de Evaluación Heurística $f(s)$:**  
   Combina balance material con tablas posicionales pieza-casilla (*Piece-Square Tables*) para incentivar el control central, desarrollo de piezas menores, seguridad del rey y estructura de peones.

---

## Modos de Ejecución (Dual UI)

El proyecto separa estrictamente la lógica del motor de las capas de presentación para soportar dos entornos independientes:

* **Interfaz Web (`app.py` — Gradio + SVG):**  
  Diseñada para despliegue en la nube con aislamiento de estado por sesión (`board.copy()`), renderizado vectorial del tablero, selector de tiempo de cómputo, barra de ventaja posicional y telemetría de búsqueda.
* **Interfaz de Escritorio (`main.py` — Pygame):**  
  Incluye modo de visualización del árbol en vivo (`visualizar_en_vivo=True`), permitiendo observar sobre el tablero las variantes candidatas que el motor explora en tiempo real mientras calcula su turno.

---

## Estructura del Proyecto

```text
deepred-motor-ajedrez/
├── engine/
│   ├── evaluation.py      # Valores materiales y tablas posicionales (Piece-Square Tables)
│   └── search.py          # Minimax Alfa-Beta, Quiescence Search, Zobrist Hashing y TT
├── ui/
│   └── gui.py             # Interfaz gráfica de escritorio en Pygame con árbol en vivo
├── tests/
│   └── test_engine.py     # Pruebas unitarias de búsqueda, evaluación e integridad del tablero
├── app.py                 # Aplicación web interactiva en Gradio (producción en Render)
├── main.py                # Punto de entrada para la versión de escritorio
├── requirements.txt       # Dependencias de producción
└── README.md