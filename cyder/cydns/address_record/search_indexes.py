from haystack import indexes
from cyder.cydns.address_record.models import AddressRecord


class AddressRecordIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    fqdn = indexes.CharField(model_attr='fqdn')
    ip_str = indexes.CharField(model_attr='ip_str')
    label = indexes.CharField(model_attr='label')

    def get_model(self):
        return AddressRecord

    def index_queryset(self):
        return self.get_model().objects.all()
