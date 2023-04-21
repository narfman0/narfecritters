import logging
import json
import os
from functools import cmp_to_key

from pokeclone.db import models
from pokeclone.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


def main():
    initialize_logging()
    LOGGER.info("Running db generator")
    api_root_path = os.path.join("..", "pokemon-api-data")
    api_data_path = os.path.join(api_root_path, "data", "api", "v2")
    pokemon = list(generate_pokemon(os.path.join(api_data_path, "pokemon")))
    LOGGER.info(f"Writing {len(pokemon)} pokemon to file")
    models.Pokedex(pokemon).to_yaml_file(os.path.join("data", "db", "pokemon.yml"))
    moves = list(generate_moves(os.path.join(api_data_path, "move")))
    LOGGER.info(f"Writing {len(moves)} moves to file")
    models.Moves(moves).to_yaml_file(os.path.join("data", "db", "moves.yml"))
    LOGGER.info(f"Done!")


def generate_moves(api_moves_path):
    for root, dirs, files in os.walk(api_moves_path):
        for id in sorted([int(x) for x in dirs]):
            try:
                json_path = os.path.join(api_moves_path, str(id), "index.json")
                with open(json_path, "r") as json_file:
                    move_json = json.load(json_file)
                    yield models.Move(
                        id=move_json["id"],
                        name=move_json["name"],
                        power=move_json["power"],
                        type=models.Type[str(move_json["type"]["name"]).upper()],
                    )
            except Exception as e:
                LOGGER.error(f"Error parsing {dir}: {e}")


def generate_pokemon(api_pokemon_path):
    for root, dirs, files in os.walk(api_pokemon_path):
        for dir in dirs:
            if dir == "encounters":
                continue
            try:
                pokemon_json_path = os.path.join(api_pokemon_path, dir, "index.json")
                with open(pokemon_json_path, "r") as pokemon_json_file:
                    pokemon_json = json.load(pokemon_json_file)
                    yield parse_pokemon_from_json(pokemon_json)
            except Exception as e:
                LOGGER.error(f"Error parsing {dir}: {e}")


def parse_pokemon_from_json(pokemon_json):
    pokemon_stats = models.Stats(
        pokemon_json["stats"][0]["base_stat"],
        pokemon_json["stats"][1]["base_stat"],
        pokemon_json["stats"][2]["base_stat"],
        pokemon_json["stats"][3]["base_stat"],
        pokemon_json["stats"][4]["base_stat"],
        pokemon_json["stats"][5]["base_stat"],
    )
    types = []
    for json_type in pokemon_json["types"]:
        types.append(models.Type[str(json_type["type"]["name"]).upper()])
    move_ids = []
    for move in pokemon_json["moves"]:
        move_ids.append(int(move["move"]["url"].split("/")[-2]))
    return models.Pokemon(
        id=pokemon_json["id"],
        name=pokemon_json["name"],
        base_stats=pokemon_stats,
        types=types,
        move_ids=move_ids,
    )


if __name__ == "__main__":
    main()
