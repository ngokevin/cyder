from django import forms

from cyder.core.ctnr.models import Ctnr


class CtnrForm(forms.ModelForm):
    class Meta:
        model = Ctnr
