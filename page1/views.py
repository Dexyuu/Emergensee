from django.shortcuts import render
from Account.models import Account
from imageupload.models import Image
from django.core.paginator import Paginator

# Create your views here.

def home_screen_view(request):
    images_list = Image.objects.all().order_by('-uploaded_at')
    paginator = Paginator(images_list, 9)  # Show 9 images per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'users': Account.objects.all(),
    }

    return render(request, "page1/home.html", context)