from dataclasses import dataclass, field

@dataclass
class RandomConfig:
    memory_expansion: bool
    utility_mods: list
    scale_boss: bool
    enemymode: str
    nightmare_enemies: bool
    bossmode: str
    nightmare_bosses: bool
    duplicate_bosses: bool

    enemies: dict
    combine_enemy_sizes: bool
    combine_melee_ranged: bool
    bosses: dict
    bosses_replace_enemies: bool
    boss_enemies: list=field(default_factory=list)

    mickey_rule: str='follow'

    selected_enemy: str = ''
    selected_boss: str = ''

