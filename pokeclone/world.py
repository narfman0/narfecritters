import logging
import random

LOGGER = logging.getLogger(__name__)


from pokeclone import models

MOVE_SPEED = 5


class World:
    def __init__(self):
        self.pokedex = models.Pokedex.load()
        starting_pokemon = self.pokedex.create("charmander", 5)
        # TODO rebalance this
        starting_pokemon.max_hp += 50
        starting_pokemon.current_hp += 50
        self.player = models.NPC(x=10, y=10, pokemon=[starting_pokemon])
        self.in_encounter = False

    def create_boss_encounter(self):
        self.in_encounter = True
        self.enemy = self.pokedex.create("charmander", round(random.random() * 9 + 4))

    def create_encounter(self):
        self.in_encounter = True
        enemy_pokemon_name = random.choice(["charmander", "bulbasaur"])
        self.enemy = self.pokedex.create(
            enemy_pokemon_name, round(random.random() * 4 + 1)
        )

    def end_encounter(self):
        self.in_encounter = False
        self.enemy = None
        self.active_pokemon().current_hp = self.active_pokemon().max_hp
        # TODO add experience :D

    def active_pokemon(self) -> models.Pokemon:
        return self.player.pokemon[0]

    def turn(self, move_name):
        move = None
        for amove in self.active_pokemon().moves:
            if amove.name == move_name:
                move = amove
        # TODO model active pokemon
        enemy_damage = models.attack(self.active_pokemon(), self.enemy, move)
        self.enemy.current_hp -= enemy_damage
        player_damage = models.attack(
            self.enemy, self.active_pokemon(), random.choice(self.enemy.moves)
        )
        self.active_pokemon().current_hp -= player_damage
        return (player_damage, enemy_damage)

    def update(self, dt):
        pass
