from dataclasses import dataclass

import pytmx

from narfecritters.models.areas import Area
from narfecritters.models.encyclopedia import Encyclopedia


@dataclass
class TransitionDetails:
    destination_area: Area
    destination_x: int
    destination_y: int


@dataclass
class EncounterLevel:
    mean: float
    sigma: float


class Map:
    def __init__(self, area: Area):
        self.area = area
        self.tmxdata = pytmx.load_pygame(f"data/tiled/{area.name.lower()}.tmx")

    def get_start_tile(self):
        return map(int, self.tmxdata.properties.get("StartTile").split(","))

    def get_area_encounter_level(self):
        mean = float(self.tmxdata.properties.get("EncounterLevelMean"))
        sigma = float(self.tmxdata.properties.get("EncounterLevelSigma"))
        return EncounterLevel(mean, sigma)

    def get_candidate_encounters(self, encyclopedia: Encyclopedia):
        candidate_encounters: list[int] = []
        encounters_str = self.tmxdata.properties.get("Encounters")
        if not encounters_str:
            return []
        for encounter in encounters_str.split("\n"):
            name, probability = str(encounter).split(",")
            id = encyclopedia.name_to_id[name]
            candidate_encounters.extend([id] * int(probability))
        return candidate_encounters

    def get_tile_type(self, tile_x, tile_y, layer):
        tile_props = self.tmxdata.get_tile_properties(tile_x, tile_y, layer) or {}
        return tile_props.get("type")

    def get_transition_details(self, tile_x, tile_y):
        object = self.tmxdata.get_object_by_name(f"transition,{tile_x},{tile_y}")
        destination_area = Area[object.properties["Destination"].upper()]
        dest_x, dest_y = map(int, object.properties["DestinationXY"].split(","))
        return TransitionDetails(destination_area, dest_x, dest_y)

    def has_colliders(self, tile_x, tile_y, layer):
        tile_props = self.tmxdata.get_tile_properties(tile_x, tile_y, layer) or {}
        return tile_props.get("colliders")

    def get_tile_image(self, tile_x, tile_y, layer):
        return self.tmxdata.get_tile_image(tile_x, tile_y, layer)

    def get_tile_layer_count(self):
        return len(list(self.tmxdata.visible_tile_layers))

    @property
    def width(self):
        return self.tmxdata.width

    @property
    def height(self):
        return self.tmxdata.height
