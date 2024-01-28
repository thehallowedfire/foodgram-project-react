from recipes.models import Recipe, RecipeIngredient


def add_ingredients_to_recipe(recipe: Recipe,
                              ingredients: list[dict]) -> None:
    """
    Assign the provided list of ingredients to a recipe
    by creating RecipeIngredient objects.

    Each ingredient dictionary must contain the following keys:
    - 'id' (int): The ingredient id.
    - 'amount' (int): The quantity of the ingredient.

    Parameters:
    - recipe (Recipe): Recipe object to which the ingredients will be added.
    - ingredients (list of dict): A list of dictionaries, each representing an
    ingredient.
    """
    ingredients_list = [RecipeIngredient(recipe=recipe,
                                         ingredient_id=ingredient['id'],
                                         amount=ingredient['amount'])
                        for ingredient in ingredients]
    RecipeIngredient.objects.bulk_create(ingredients_list)
