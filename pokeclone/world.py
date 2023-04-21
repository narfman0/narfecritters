import logging
import random

LOGGER = logging.getLogger(__name__)


from pokeclone.db.models import *

MOVE_SPEED = 200


class World:
    def __init__(self):
        self.pokedex = Pokedex.load()
        self.moves = Moves.load()
        starting_pokemon = self.pokedex.create("charmander", 5)
        # TODO rebalance this
        starting_pokemon.base_stats.hp += 50
        starting_pokemon.current_hp += 50
        self.player = NPC(x=10, y=10, pokemon=[starting_pokemon])
        self.enemy = None

    def move(self, distance: int, up=False, down=False, left=False, right=False):
        if left:
            self.player.x -= distance
        elif right:
            self.player.x += distance
        if up:
            self.player.y += distance
        elif down:
            self.player.y -= distance

        if random.random() < 0.01:
            self.enemy = self.pokedex.create(
                random.choice(["charmander", "bulbasaur"]),
                round(random.random() * 4 + 1),
            )

    def end_encounter(self):
        self.enemy = None
        self.active_pokemon.current_hp = self.active_pokemon.base_stats.hp
        # TODO add experience :D

    def turn(self, move_name):
        move = self.moves.find_by_name(move_name)
        # TODO model active pokemon
        enemy_damage = self.attack(self.active_pokemon, self.enemy, move)
        self.enemy.current_hp -= enemy_damage
        enemy_move = self.moves.find_by_id(random.choice(self.enemy.move_ids))
        player_damage = self.attack(self.enemy, self.active_pokemon, enemy_move)
        self.active_pokemon.current_hp -= player_damage

        print(
            f"{self.active_pokemon.name} used {move_name} for {enemy_damage}, took {player_damage}"
        )
        if self.active_pokemon.current_hp <= 0:
            LOGGER.info(f"Your {self.active_pokemon.name} passed out!")
            self.end_encounter()
        if self.enemy.current_hp <= 0:
            LOGGER.info(f"Enemy {self.active_pokemon.name} passed out!")
            self.end_encounter()

    def attack(self, attacker: Pokemon, defender: Pokemon, move: Move):
        return (
            round(
                (
                    (round((2 * attacker.level) / 5) + 2)
                    * move.power
                    * round(attacker.attack / defender.defense)
                )
                / 50
            )
            + 2
        )

    @property
    def active_pokemon(self) -> Pokemon:
        return self.player.pokemon[0]
