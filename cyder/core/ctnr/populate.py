from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.cydns.domain.models import Domain

domains = Domain.objects.filter(id__lte = 3);

ctnr = Ctnr.objects.get(id=0);
for domain in domains:
    ctnr.domains.add(domain)
ctnr.save()
