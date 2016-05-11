from django.shortcuts import render


# index home page
def index(request):
    context_dict = {}
    return render(request, 'sleepvl/index.html', context_dict)


def site_admin(request):
    context_dict = {}
    return render(request,'sleepvl/site_admin.html', context_dict)