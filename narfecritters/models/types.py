from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


@dataclass
class Type:
    id: int
    name: str
    double_damage_from: list[int] = field(default_factory=set)
    double_damage_to: list[int] = field(default_factory=set)
    half_damage_from: list[int] = field(default_factory=set)
    half_damage_to: list[int] = field(default_factory=set)
    no_damage_from: list[int] = field(default_factory=set)
    no_damage_to: list[int] = field(default_factory=set)


@dataclass
class Types(YAMLWizard):
    types: list[Type]

    @classmethod
    def load(cls):
        return Types.from_yaml_file(f"data/db/types.yml")

    def find_by_name(self, name: str):
        for type in self.types:
            if type.name == name:
                return type

    def find_by_id(self, id: int):
        for type in self.types:
            if type.id == id:
                return type
