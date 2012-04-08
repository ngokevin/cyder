from django.contrib import messages
from django.shortcuts import redirect

from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from cyder.core.ctnr.forms import CtnrForm
from cyder.core.ctnr.models import Ctnr, CtnrUser


class CtnrView(object):
    model = Ctnr
    queryset = Ctnr.objects.all()
    form_class = CtnrForm

    context_object_name = "ctnr"


class CtnrDeleteView(CtnrView, DeleteView):
    """ Delete View """
    template_name = "common/delete.html"


class CtnrDetailView(CtnrView, DetailView):
    """ Detail View """


class CtnrCreateView(CtnrView, CreateView):
    """ Create View """


class CtnrUpdateView(CtnrView, UpdateView):
    """ Update View """


class CtnrListView(CtnrView, ListView):
    """ List View """
    context_object_name = "objects"
    paginate_by = 30


def change_ctnr(request, pk = None):
    referer = request.META['HTTP_REFERER']

    # check if ctnr exists
    try:
        if request.method == 'POST':
            ctnr = Ctnr.objects.get(name=request.POST['ctnr_name'])
        else:
            ctnr = Ctnr.objects.get(id=pk)
    except:
        messages.error(request, "Could not change container, does not exist")
        return redirect(referer)

    # check if user has access to ctnr
    if CtnrUser.objects.filter(user=request.user, ctnr=ctnr) or \
    CtnrUser.objects.filter(user=request.user, ctnr=1):
        request.session['ctnr'] = ctnr
    else:
        messages.error(request, "You do not have access to this container.")

    return redirect(referer)
