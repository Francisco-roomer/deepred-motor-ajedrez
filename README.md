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