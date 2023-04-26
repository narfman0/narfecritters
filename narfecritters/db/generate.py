import logging
import json
import os

from narfecritters.db.models import *
from narfecritters.util.logging import initialize_logging

LOGGER = logging.getLogger(__name__)


def main():
    initialize_logging()
    LOGGER.info("Running db generator")
    api_root_path = os.path.join("..", "pokemon-api-data")
    api_data_path = os.path.join(api_root_path, "data", "api", "v2")

    types = list(generate_types(os.path.join(api_data_path, "type")))
    LOGGER.info(f"Writing {len(types)} types to file")
    Types(types).to_yaml_file(os.path.join("data", "db", "types.yml"))

    pokemon = list(generate_pokemon(os.path.join(api_data_path, "pokemon")))
    LOGGER.info(f"Writing {len(pokemon)} pokemon to file")
    Pokedex(name_to_id={item.name: item.id for item in pokemon}).to_yaml_file(
        os.path.join("data", "db", "pokedex.yml")
    )
    for item in pokemon:
        item.to_yaml_file(os.path.join("data", "db", "pokemon", f"{item.id}.yml"))

    moves = list(generate_moves(os.path.join(api_data_path, "move")))
    LOGGER.info(f"Writing {len(moves)} moves to file")
    Moves(moves).to_yaml_file(os.path.join("data", "db", "moves.yml"))

    LOGGER.info(f"Done!")


def generate_types(api_types_path):
    for root, dirs, files in os.walk(api_types_path):
        for id in sorted([int(x) for x in dirs]):
            try:
                json_path = os.path.join(api_types_path, str(id), "index.json")
                with open(json_path, "r") as json_file:
                    type_json = json.load(json_file)
                    yield Type(
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
                    yield Move(
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
    pokemon_stats = Stats(
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
    return Pokemon(
        id=pokemon_json["id"],
        name=pokemon_json["name"],
        base_stats=pokemon_stats,
        type_ids=type_ids,
        moves=list(parse_pokemon_moves_from_json(pokemon_json)),
        base_experience=pokemon_json["base_experience"],
    )


def parse_pokemon_moves_from_json(pokemon_json):
    for move in pokemon_json["moves"]:
        id = int(move["move"]["url"].split("/")[-2])
        name = move["move"]["name"]
        level_learned_at = None
        learn_method = None
        for version_group_detail in move["version_group_details"]:
            if (
                level_learned_at is None
                or learn_method is None
                or version_group_detail["version_group"]["name"] == "black-white"
            ):
                level_learned_at = version_group_detail["level_learned_at"]
                learn_method = version_group_detail["move_learn_method"]["name"]
        yield PokemonMove(
            id=id,
            name=name,
            level_learned_at=level_learned_at,
            learn_method=learn_method,
        )


if __name__ == "__main__":
    main()
