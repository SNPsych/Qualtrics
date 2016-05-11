from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import pprint

# index home page
def index(request):
    context_dict = {}
    return render(request, 'sleepvl/index.html', context_dict)

@login_required
def site_admin(request):
    context_dict = {}
    #return render(request,'sleepvl/site_admin.html', context_dict)
    msgStr = '<H3>Access Denied for {}: Not implemented <H3><BR>'.format(repr(request.user))
    print(msgStr)
    return HttpResponse(msgStr)


from django.contrib.auth.middleware import RemoteUserMiddleware

class CustomHeaderMiddleware(RemoteUserMiddleware):
    header = 'HTTP_AUTHUSER'

    def process_request(self, request):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(request.META)
        return super(CustomHeaderMiddleware,self).process_request(request)