# Create your views here.

from django.views.generic import DetailView
from django.shortcuts import render

class Cydns(DetailView): #TODO we need a more appropriate Generic CBV
    def get( self, request, *args, **kwargs ):
        return render( request, "cydns.html" )
