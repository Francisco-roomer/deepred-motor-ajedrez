# DeepRed Chess Motor

Motor de ajedrez basado en **Inteligencia Artificial Clásica (IA Simbólica)** inspirado en la arquitectura de IBM Deep Blue, desarrollado en Python con interfaz gráfica interactiva en Pygame.

## Arquitectura del Motor
* **Evaluación Estática $f(s)$ (`engine/evaluation.py`):** Balance de material en centipeones combinado con *Piece-Square Tables (PST)* para valorar el control central, desarrollo y seguridad del rey.
* **Árbol de Búsqueda (`engine/search.py`):**
  * **Minimax con Poda Alfa-Beta:** Descarta ramas subóptimas del árbol de decisión.
  * **Ordenamiento MVV-LVA:** Prioriza capturas ventajosas para maximizar los cortes $\alpha-\beta$.
  * **Quiescence Search:** Extiende el cálculo en secuencias de capturas para eliminar el efecto horizonte.
  * **Tablas de Transposición (Zobrist Hashing):** Caché de 64 bits que evita recalcular posiciones ya exploradas.
  * **Iterative Deepening:** Control estricto del tiempo por jugada con ordenamiento dinámico de la variante principal.

## Ejecución
```bash
pip install -r requirements.txt
python main.py



#  DeepRed Chess Motor

Motor de ajedrez basado en **Inteligencia Artificial Clásica (IA Simbólica)** inspirado en la arquitectura de IBM Deep Blue, desarrollado en Python con arquitectura modular: núcleo algorítmico independiente (`engine/`), interfaz nativa de escritorio (`ui/gui.py` en Pygame) y aplicación web responsiva (`app.py` en Gradio).

![Demo DeepRed](assets/demo_deepred.gif)

##  Demo Web vs. Ejecución Local

* **Demo Web (Hugging Face Spaces):** Disponible mediante URL pública con diseño responsivo para escritorio y dispositivos móviles. Al ejecutarse en **hardware gratuito compartido (2 vCPUs)**, el tiempo por jugada está acotado (0.5s – 2.5s) y puede experimentar *cold start* (30–60s) tras periodos de inactividad.
* **Recomendación — Ejecución Local:** Para evaluar miles de nodos por segundo sin restricciones de concurrencia y jugar con ratón a 60 FPS en la interfaz nativa de Pygame, se recomienda clonar y ejecutar el proyecto localmente.

##  Arquitectura del Motor (`engine/`)
* **Evaluación Estática $f(s)$ (`engine/evaluation.py`):** Balance de material en centipeones combinado con *Piece-Square Tables (PST)* para valorar control central, desarrollo y seguridad del rey.
* **Árbol de Búsqueda (`engine/search.py`):**
  * **Minimax con Poda Alfa-Beta:** Descarta ramas subóptimas del árbol de decisión.
  * **Ordenamiento MVV-LVA:** Prioriza capturas ventajosas para maximizar cortes $\alpha-\beta$.
  * **Quiescence Search:** Extiende el cálculo en secuencias de capturas para eliminar el efecto horizonte.
  * **Tablas de Transposición (Zobrist Hashing):** Caché de 64 bits que evita recalcular posiciones ya exploradas.
  * **Iterative Deepening:** Control estricto de tiempo con ordenamiento dinámico de la variante principal.

##  Instalación y Uso Local

```bash
git clone [https://github.com/TU-USUARIO/deepred-chess-motor.git](https://github.com/TU-USUARIO/deepred-chess-motor.git)
cd deepred-chess-motor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 1. Ejecutar interfaz nativa de escritorio (Recomendado)
python main.py

# 2. O lanzar la interfaz web responsiva en navegador
python app.py