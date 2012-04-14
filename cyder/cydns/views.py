from cyder.cydns.domain.models import Domain
from cyder.cydns.utils import slim_form
from cyder.base.views import BaseListView, BaseDetailView, BaseCreateView
from cyder.base.views import BaseUpdateView, BaseDeleteView


class CydnsListView(BaseListView):
    """ """
    template_name = 'cydns/cydns_list.html'


class CydnsDetailView(BaseDetailView):
    """ """
    template_name = 'cydns/cydns_detail.html'


class CydnsCreateView(BaseCreateView):
    """ """
    template_name = 'cydns/cydns_form.html'

    def get_form(self, form_class):
        form = super(CydnsCreateView, self).get_form(form_class)
        domain_pk = self.kwargs.get('domain', False)

        # The use of slim_form makes my eyes bleed and stomach churn.
        if domain_pk:
            form = slim_form(domain_pk=domain_pk, form=form)

        reverse_domain_pk = self.kwargs.get('reverse_domain', False)
        if reverse_domain_pk:
            slim_form(reverse_domain_pk=reverse_domain_pk, form=form)

        # This is where filtering domain selection should take place.
        # form.fields['domain'].queryset = Domain.objects.filter(name =
        # 'foo.com') This ^ line will change the query set to something
        # controllable find user credentials in self.request
        return form


class CydnsUpdateView(BaseUpdateView):
    """ """
    template_name = 'cydns/cydns_form.html'


class CydnsDeleteView(BaseDeleteView):
    """ """
    template_name = 'cydns/cydns_confirm_delete.html'
    succcess_url = '/cydns/'

