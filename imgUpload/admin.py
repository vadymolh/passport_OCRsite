from django.contrib import admin
from .models import Person, Scan, Image

# Register your models here.

admin.site.register(Person)

admin.site.register(Scan)
