from django.shortcuts import render


# index home page
def index(request):
    context_dict = {}
    return render(request, 'sleepvl/index.html', context_dict)
