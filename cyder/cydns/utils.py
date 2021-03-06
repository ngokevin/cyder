# Random functions that get used in different places.
from django.http import Http404

from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain


def tablefy(objects):
    """Given a list of objects, build a matrix that is can be printed as a table. Also return
    the headers for that table. Populate the given url with the pk of the object. Return all
    headers, field array, and urls in a seperate lists.

    :param  objects: A list of objects to make the matrix out of.
    :type   objects: AddressRecords
    """
    matrix = []
    urls   = []
    headers = []
    if not objects:
        return (None, None, None)
    # Build the headers
    for title, value in objects[0].details():
        headers.append( title )

    # Build the matrix and urls
    for obj in objects:
        row = []
        urls.append( obj.get_absolute_url() )
        for title, value in obj.details():
            row.append( value )
        matrix.append(row)

    return (headers, matrix, urls)


def slim_form(domain_pk=None, reverse_domain_pk=None, form=None):
    """ What is going on? We want only one domain showing up in the
    choices.  We are replacing the query set with just one object. Ther
    are two querysets. I'm not really sure what the first one does, but
    I know the second one (the widget) removes the choices. The third
    line removes the default u'--------' choice from the drop down.  """
    if not form:
        raise Http404
    if domain_pk:
        query_set = Domain.objects.filter(id=domain_pk)
        if not query_set:
            raise Http404
        if not form.fields.get('domain', False):
            raise Http404
        form.fields['domain']._queryset = query_set
        form.fields['domain'].widget.choices.queryset = query_set
        form.fields['domain'].empty_label = None
    if reverse_domain_pk:
        query_set = ReverseDomain.objects.filter(id=reverse_domain_pk)
        if not query_set:
            raise Http404
        if not form.fields.get('reverse_domain', False):
            raise Http404
        form.fields['reverse_domain']._queryset = query_set
        form.fields['reverse_domain'].widget.choices.queryset = query_set
        form.fields['reverse_domain'].empty_label = None
    return form
