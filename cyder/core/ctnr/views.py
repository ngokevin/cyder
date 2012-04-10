import simplejson

from django.contrib import messages
from django import forms
from django.shortcuts import redirect, render

from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from cyder.core.ctnr.forms import CtnrForm
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.cyuser.utils import tablefy_users
from cyder.cydns.utils import tablefy


class CtnrView(object):
    model = Ctnr
    queryset = Ctnr.objects.all()
    form_class = CtnrForm


class CtnrDeleteView(CtnrView, DeleteView):
    """ Delete View """
    template_name = "confirm_delete.html"


class CtnrDetailView(CtnrView, DetailView):
    """ Detail View """
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        ctnr = kwargs.get('object', False)
        if not ctnr:
            return context

        users = ctnr.users.all()
        user_headers, user_matrix, user_urls = tablefy_users(users)

        domains = ctnr.domains.all()
        domain_headers, domain_matrix, domain_urls = tablefy(domains)

        rdomains = ctnr.reverse_domains.all()
        rdomain_headers, rdomain_matrix, rdomain_urls = tablefy(rdomains)

        return dict({
            "user_headers": user_headers,
            "user_matrix": user_matrix,
            "user_urls": user_urls,

            "domain_headers": domain_headers,
            "domain_matrix": domain_matrix,
            "domain_urls": domain_urls,

            "rdomain_headers": rdomain_headers,
            "rdomain_matrix": rdomain_matrix,
            "rdomain_urls": rdomain_urls,
        }.items() + context.items())


class CtnrCreateView(CtnrView, CreateView):
    """ Create View """
    def post(self, request, *args, **kwargs):
        ctnr_form = CtnrForm(request.POST)

        # try to save the ctnr TODO: call has_perms
        try:
            ctnr = ctnr_form.save(commit=False)
        except ValueError as e:
            return render(request, "ctnr/ctnr_form.html", {'form': ctnr_form})

        ctnr.save()

        # update ctnr-related session variables
        request.session['ctnrs'].append(ctnr)
        ctnr_names = simplejson.loads(request.session['ctnr_names_json'])
        ctnr_names.append(ctnr.name)
        request.session['ctnr_names_json'] = simplejson.dumps(ctnr_names)

        return redirect('/ctnr/' + str(ctnr.id))

    def get(self, request, *args, **kwargs):
        return super(CtnrCreateView, self).get(request, *args, **kwargs)


class CtnrUpdateView(CtnrView, UpdateView):
    """ Update View """


class CtnrListView(CtnrView, ListView):
    """ List View """
    paginate_by = 30


def change_ctnr(request, pk = None):
    try:
        referer = request.META['HTTP_REFERER']
    except KeyError:
        referer = '/'

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
    try:
        global_ctnr_user = CtnrUser.objects.get(user=request.user, ctnr=1)
    except CtnrUser.DoesNotExist:
        global_ctnr_user = None
    try:
        ctnr_user = CtnrUser.objects.get(user=request.user, ctnr=ctnr)
    except CtnrUser.DoesNotExist:
        ctnr_user = None

    if ctnr_user or global_ctnr_user:
        # set session ctnr and level
        request.session['ctnr'] = ctnr

        # higher level overrides
        if ctnr_user:
            level = ctnr_user.level
        else:
            level = 0
        if global_ctnr_user:
            global_level = global_ctnr_user.level
        else:
            global_level = 0
        request.session['level'] = max(level, global_level)

    else:
        messages.error(request, "You do not have access to this container.")

    return redirect(referer)
