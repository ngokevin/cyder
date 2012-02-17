# Create your views here.
from django.views.generic import DetailView, CreateView, UpdateView
from cyder.cydns.soa.models import SOAForm, SOA
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import pdb

class SOADetailView(DetailView):
    context_object_name = "soa"
    template_name = "soa_detail.html"
    queryset = SOA.objects.all()

class SOACreateView(CreateView):
    model = SOA
    form_class = SOAForm
    template_name = "soa_form.html"
    context_object_name = "soa"

    def post(self, request, *args, **kwargs ):
        try:
            soa = super(SOACreateView, self).post(request, *args, **kwargs)
        except Exception, e:
            messages.error( request, str(e) )
            return super(SOACreateView, self).get(request, *args, **kwargs)
        return soa
    def get(self, request, *args, **kwargs ):
        return super(SOACreateView, self).get(request, *args, **kwargs)

class SOAUpdateView(UpdateView):
    template_name = "soa_form.html"
    context_object_name = "soa"
    form_class = SOAForm
    queryset = SOA.objects.all()

    def post(self, request, *args, **kwargs ):
        try:
            soa = super(SOAUpdateView, self).post(request, *args, **kwargs)
        except Exception, e:
            messages.error( request, str(e) )
            request.method = 'GET'
            return super(SOAUpdateView, self).get(request, *args, **kwargs)
        return soa
    def get(self, request, *args, **kwargs ):
        return super(SOAUpdateView, self).get(request, *args, **kwargs)
