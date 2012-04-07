from django.contrib import messages
from django.shortcuts import redirect

from cyder.core.ctnr.models import Ctnr, CtnrUser

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
