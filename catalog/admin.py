from django.contrib import admin
from catalog.models import Article


# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass

def difn():
    pass