from cyder.cydns.nameserver.reverse_nameserver.models import ReverseNameserver
from cyder.cydns.nameserver.view_tests import *


class RevNSViewTests(TestCase):
    def setUp(self):
        url_slug = "reverse_nameserver"
        dname = random_label()
        self.client = Client()
        self.url_slug = url_slug
        self.domain, create = ReverseDomain.objects.get_or_create(name="255")
        server = random_label()
        self.test_obj, create = ReverseNameserver.objects.get_or_create( server=server, reverse_domain= self.domain )
        while not create:
            server = "a"+server
            self.test_obj, create = ReverseNameserver.objects.get_or_create( server=server, reverse_domain= self.domain )

    def post_data(self):
        server = random_label()
        return {'server': server, 'domain':self.domain.pk}


builder = GenericViewTests()
for test in builder.build_all_tests():
    setattr(RevNSViewTests,test.__name__+"_rev_ns", test)
