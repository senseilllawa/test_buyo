from django.contrib import admin
from parser_app.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'parser_name',
        'title',
        'product_code',
        'regular_price',
        'sale_price',
        'manufacturer',
        'color',
        'memory',
        'reviews_count',
    )
    list_filter = ('parser_name', 'manufacturer')
    search_fields = ('title', 'product_code')
