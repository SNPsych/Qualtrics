from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

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