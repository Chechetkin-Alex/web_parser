from dataclasses import dataclass


@dataclass
class Day:
    day_of_the_week: str
    start_cell: int = 1000
    finish_cell: int = 0
