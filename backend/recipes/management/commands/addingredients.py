import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Populate the DB with default ingredients'

    def add_arguments(self, parser):
        parser.add_argument('filename',
                            type=str,
                            nargs='?',
                            default='ingredients.json',
                            help='Optional JSON file path')

    def handle(self, *args, **options):
        # By default the file should be in the Django project folder
        default_file = Path(__file__).resolve().parents[3] / 'ingredients.json'
        file_name = options.get('filename') or default_file

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
            message = 'Successfully added ingredients!'
            self.stdout.write(self.style.SUCCESS(message))
        except FileNotFoundError:
            raise CommandError(f'File {file_name} does not exist')
        except Exception as error:
            raise CommandError(f'An error occurred: {error}')
