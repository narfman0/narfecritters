import logging
import json
import os

from pokeclone.db import models
from pokeclone.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


def main():
    initialize_logging()
    LOGGER.info("Running db generator")
    api_root_path = os.path.join("..", "pokemon-api-data")
    api_data_path = os.path.join(api_root_path, "data", "api", "v2")

    types = list(generate_types(os.path.join(api_data_path, "type")))
    LOGGER.info(f"Writing {len(types)} types to file")
    models.Types(types).to_yaml_file(os.path.join("data", "db", "types.yml"))

    pokemon = list(generate_pokemon(os.path.join(api_data_path, "pokemon")))
    LOGGER.info(f"Writing {len(pokemon)} pokemon to file")
    models.Pokedex(pokemon).to_yaml_file(os.path.join("data", "db", "pokemon.yml"))
    models.Pokedex(pokemon[0:9]).to_yaml_file(
        os.path.join("tests", "fixtures", "pokemon.yml")
    )

    moves = list(generate_moves(os.path.join(api_data_path, "move")))
    LOGGER.info(f"Writing {len(moves)} moves to file")
    models.Moves(moves).to_yaml_file(os.path.join("data", "db", "moves.yml"))

    LOGGER.info(f"Done!")


def generate_types(api_types_path):
    for root, dirs, files in os.walk(api_types_path):
        for id in sorted([int(x) for x in dirs]):
            try:
                json_path = os.path.join(api_types_path, str(id), "index.json")
                with open(json_path, "r") as json_file:
                    type_json = json.load(json_file)
                    yield models.Type(
                        id=type_json["id"],
                        name=type_json["name"],
                        double_damage_from=list(
                            parse_dmg_applicability(
                                type_json["damage_relations"]["double_damage_from"]
                            )
                        ),
                        double_damage_to=list(
                            parse_dmg_applicability(
                                type_json["damage_relations"]["double_damage_to"]
                            )
                        ),
                        half_damage_from=list(
                            parse_dmg_applicability(
                                type_json["damage_relations"]["half_damage_from"]
                            )
                        ),
                        half_damage_to=list(
                            parse_dmg_applicability(
                                type_json["damage_relations"]["half_damage_to"]
                            )
                        ),
                        no_damage_from=list(
                            parse_dmg_applicability(
                                type_json["damage_relations"]["no_damage_from"]
                            )
                        ),
                        no_damage_to=list(
                            parse_dmg_applicability(
                                type_json["damage_relations"]["no_damage_to"]
                            )
                        ),
                    )
            except Exception as e:
                LOGGER.error(f"Error parsing {dir}: {e}")


def parse_dmg_applicability(damage_relations_json):
    for damage_relation_json in damage_relations_json:
        yield int(damage_relation_json["url"].split("/")[-2])


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
                        type_id=int(move_json["type"]["url"].split("/")[-2]),
                    )
            except Exception as e:
                LOGGER.error(f"Error parsing {dir}: {e}")


def generate_pokemon(api_pokemon_path):
    for root, dirs, files in os.walk(api_pokemon_path):
        for dir in sorted([int(x) for x in filter(str.isdecimal, dirs)]):
            try:
                pokemon_json_path = os.path.join(
                    api_pokemon_path, str(dir), "index.json"
                )
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
    type_ids = []
    for json_type in pokemon_json["types"]:
        type_ids.append(int(json_type["type"]["url"].split("/")[-2]))
    move_ids = []
    for move in pokemon_json["moves"]:
        move_ids.append(int(move["move"]["url"].split("/")[-2]))
    return models.Pokemon(
        id=pokemon_json["id"],
        name=pokemon_json["name"],
        base_stats=pokemon_stats,
        type_ids=type_ids,
        move_ids=move_ids,
        base_experience=pokemon_json["base_experience"],
    )


if __name__ == "__main__":
    main()
