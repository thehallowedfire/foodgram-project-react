from django.contrib import admin

from .models import Ingredient, Recipe, Tag, ShoppingCart


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorited',)
    list_display_links = ('name',)
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name',)
    ordering = ('-id',)

    @admin.display(description='Added to favorites')
    def favorited(self, instance):
        return instance.favorite.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('id',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color',)
    list_display_links = ('name',)
    ordering = ('id',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
