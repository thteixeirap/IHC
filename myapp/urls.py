# myapp/urls.py
from django.urls import path
from .views import home, fuzzy_graph_view

urlpatterns = [
    path('', home, name='home'),
    path('fuzzy-graphs/', fuzzy_graph_view, name='fuzzy_graphs'),
]
