from django.shortcuts import render
from .forms import ImageForm





def upload(request):
    """Process images uploaded by users"""
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            print(img_obj.image.path)
            # START PARALEL PROCESSING
            return render(request, 'index.html', {'form': form, 'img_obj': img_obj})
    else:
        form = ImageForm()    
        return render(request, 'index.html', {'form': form})
    
    

def success_processing(request, img_obj):
    pass
    return render(request,  'index.html')
