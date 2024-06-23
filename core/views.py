from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

# Creating TemplateView
class HomeView(TemplateView):
    template_name = 'index.html'