from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
#import pprint

# index home page
def index(request):
    context_dict = {}
    return render(request, 'sleepvl/index.html', context_dict)

def site_admin(request):
    context_dict = {}
    #return render(request,'sleepvl/site_admin.html', context_dict)
    msgStr = 'User is authenticated {}'.format(repr(request.user))
    if not request.user.is_authenticated():
        msgStr = '<H3>Access Denied for {}: Not implemented <H3><BR>'.format(repr(request.user))
    print(msgStr)
    return HttpResponse(msgStr)

from django.contrib.auth.views import login as auth_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import is_safe_url
# additional imports

# def login(request, template_name='activity/login.html',
#         redirect_field_name=REDIRECT_FIELD_NAME):
#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint('user is ')
#     pp.pprint(request.user)
#     if hasattr(request, 'user') and request.user.is_authenticated():
#         redirect_to = request.POST.get(redirect_field_name,
#             request.GET.get(redirect_field_name, ''))
#         #if not is_safe_url(url=redirect_to, host=request.get_host()):
#          #   redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
#         pp.pprint('redirecting to ' + redirect_to)
#         return HttpResponseRedirect(redirect_to)
#     pp.pprint('trying login auth_login')
#     return auth_login(request, template_name = template_name,
#         redirect_field_name = redirect_field_name)
#

from django.contrib.auth.middleware import RemoteUserMiddleware

class CustomHeaderMiddleware(RemoteUserMiddleware):

    def process_request(self, request):
        return super(CustomHeaderMiddleware,self).process_request(request)