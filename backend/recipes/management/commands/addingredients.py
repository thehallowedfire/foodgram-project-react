import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Populate the DB with default ingredients'

    def add_arguments(self, parser):
        default_file_path = (Path(__file__).resolve().parents[4]
                             / 'backend_static/data/ingredients.json')
        parser.add_argument('filename',
                            type=str,
                            nargs='?',
                            default=default_file_path,
                            help='Optional JSON file path')

    def handle(self, *args, **options):
        # By default the file is in the volume: <root>/backend_static/data/
        file_name = options.get('filename')
        self.stdout.write(f'Reading a file: {self.style.NOTICE(file_name)}')
        try:
            with open(file_name, "r", encoding='utf-8') as file:
                data = json.load(file)
            ingredients = [
                Ingredient(
                    name=ingredient.get('name'),
                    measurement_unit=ingredient.get('measurement_unit')
                ) for ingredient in data
            ]
            Ingredient.objects.bulk_create(ingredients)
            message = 'Ingredients have been successfully added!'
            self.stdout.write(self.style.SUCCESS(message))
        except FileNotFoundError:
            raise CommandError(f'File {file_name} does not exist')
        except Exception as error:
            raise CommandError(f'An error occurred: {error}')
