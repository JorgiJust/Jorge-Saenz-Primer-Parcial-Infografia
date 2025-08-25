from dataclasses import dataclass
from typing import List, Tuple

def add_columns_around_pig(pig_x, pig_y):
    return [
        (pig_x - 20, pig_y - 50),
        (pig_x + 30, pig_y - 50),
        (pig_x + 5, pig_y + 50, True),
    ]

@dataclass
class LevelData:
    columns: List[Tuple[float, float, bool]]
    pigs: List[Tuple[float, float]]

COLUMN_HEIGHT = 89

levels = [
    # Nivel 1: Cerdo solitario protegido
    LevelData(
        columns=[
            (900, 50),  # Base simple
            (900, 130),  # Soporte vertical
            (880, 130, True),  # Techo protector
        ],
        pigs=[(950, 50)],  # Cerdo alejado de la estructura
    ),
    # Nivel 2: Cerdos separados
    LevelData(
        columns=[
            # Torre izquierda simple
            (800, 50),
            (800, 130),
            (780, 130, True),
            # Torre derecha simple
            (1000, 50),
            (1000, 130),
            (1020, 130, True),
        ],
        pigs=[(850, 50), (1050, 50)],  # Cerdos a los lados de las torres
    ),
    # Nivel 3: Tres refugios
    LevelData(
        columns=[
            # Refugio izquierdo
            (800, 50),
            (780, 130, True),
            # Refugio central
            (900, 50),
            (900, 130, True),
            # Refugio derecho
            (1000, 50),
            (1020, 130, True),
        ],
        pigs=[(840, 50), (940, 50), (1040, 50)],  # Cerdos al lado de cada refugio
    ),
    # Nivel 4: Plataformas elevadas
    LevelData(
        columns=[
            # Plataforma izquierda
            (800, 50),
            (800, 140),
            (780, 230, True),
            # Plataforma central
            (900, 50),
            (900, 140),
            (900, 230, True),
            # Plataforma derecha
            (1000, 50),
            (1000, 140),
            (1020, 230, True),
        ],
        pigs=[(840, 140), (940, 140), (1040, 140)],  # Cerdos en espacios seguros
    ),
    # Nivel 5: Fortalezas independientes
    LevelData(
        columns=[
            # Fortaleza 1
            (750, 50),
            (750, 140),
            (730, 230, True),
            # Fortaleza 2
            (900, 50),
            (900, 140),
            (900, 230, True),
            # Fortaleza 3
            (1050, 50),
            (1050, 140),
            (1070, 230, True),
        ],
        pigs=[(790, 140), (940, 140), (1090, 140)],  # Cerdos bien espaciados
    ),
]
