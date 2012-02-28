# Random functions that get used in different places.
from cyder.cydns.domain.models import Domain

def slim_form( domain_pk, form ):
    """ What is going on? We want only one domain showing up in the choices.
     We are replacing the query set with just one object. Ther are two
     querysets. I'm not really sure what the first one does, but I know
     the second one (the widget) removes the choices. The third line removes
     the default u'--------' choice from the drop down.
    """
    domain_q_set = Domain.objects.filter( id = domain_pk )
    form.fields['domain']._queryset = domain_q_set
    form.fields['domain'].widget.choices.queryset = domain_q_set
    form.fields['domain'].empty_label = None
    return form
