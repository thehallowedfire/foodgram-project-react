import json
from pathlib import Path

from .models import Ingredient


def parse_json(file_name: str) -> list[dict[str, str]]:
    # Read the files
    with open(file_name, "r") as file:
        json_data = json.loads(file.read())

    # Convert dicts to tuples
    data: list[dict[str, str]] = [None] * len(json_data)
    for i, item in enumerate(json_data):
        name: str = item.get('name')
        units: str = item.get('measurement_unit')
        data[i] = {
            'name': name,
            'units': units
        }

    return data


def create_ingredients(data: list[dict[str, str]]) -> None:
    ingredients = [
        Ingredient(
            name=ingredient.get('name'),
            measurement_unit=ingredient.get('units')
        )
        for ingredient in data]
    Ingredient.objects.bulk_create(ingredients)
    print("Successfull insertion!")


def populate_db() -> None:
    data_path = Path(__file__).parents[2] / 'data/ingredients.json'
    create_ingredients(parse_json(data_path))
