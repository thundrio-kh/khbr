from dataclasses import dataclass

@dataclass
class RandomConfig:
    unlimited_memory: bool
    utility_mods: list
    scale_boss: bool
    enemymode: str
    nightmare_enemies: bool
    bossmode: str
    nightmare_bosses: bool
    duplicate_bosses: bool

    enemies: dict
    bosses: dict

    selected_enemy: str = ''
    selected_boss: str = ''

