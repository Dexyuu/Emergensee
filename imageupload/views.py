import os
import numpy as np
import tensorflow as tf
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.conf import settings
from .forms import ImageUploadForm
from .models import Image

# Load your TensorFlow model
model = tf.keras.models.load_model("C:/xampp/htdocs/adminpanel/imageupload/imageclassifiernewversionlive4.h5")

def preprocess_image(image_path):
    try:
        # Load the image
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(256, 256))
        # Convert the image to array
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        # Expand dimensions to match the model's input shape
        img_array = np.expand_dims(img_array, axis=0)
        # Normalize the image
        img_array /= 255.0
        return img_array
    except Exception as e:
        print(f"Error in preprocessing image: {e}")
        return None

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['image']
            image_path = default_storage.save('uploads/' + image.name, image)
            image_full_path = os.path.join(settings.MEDIA_ROOT, image_path)

            # Preprocess the image
            img_array = preprocess_image(image_full_path)
            if img_array is None:
                print("Preprocessing failed.")
                return render(request, 'imageupload/upload_image.html', {'form': form, 'error': 'Error in preprocessing image.'})

            try:
                # Make prediction
                prediction = model.predict(img_array)
                print(f"Prediction array: {prediction}")
            except Exception as e:
                print(f"Error in model prediction: {e}")
                return render(request, 'imageupload/upload_image.html', {'form': form, 'error': 'Error in model prediction.'})

            # Verify the image based on the model's prediction
            if 0.2 <= prediction[0][0] <= 0.5:  # Assuming class 1 is the desired class
                classification = 1
                title = "Fire"
                print("Classification: 1")
            elif 0.5 <= prediction[0][0] < 1.5:  # Assuming class 2 is the desired class
                classification = 2
                title = "Flood"
                print("Classification: 2")
            else:
                print("Image verification failed.")
                print(f"Prediction {prediction[0][0]} did not match any expected class.")
                # Delete the uploaded image if verification fails
                default_storage.delete(image_path)
                return render(request, 'imageupload/upload_image.html', {
                    'form': form,
                    'error': 'Image uploaded is not an accident.',
                    'prediction': prediction[0][0]
                })

            # Save the image and classification
            try:
                image_instance = form.save(commit=False)
                image_instance.classification = classification
                image_instance.title = title
                image_instance.latitude = request.POST.get('latitude')
                image_instance.longitude = request.POST.get('longitude')
                image_instance.address = request.POST.get('address')
                image_instance.save()
                print("Image and classification saved.")
            except Exception as e:
                print(f"Error saving image and classification: {e}")
                return render(request, 'imageupload/upload_image.html', {'form': form, 'error': 'Error saving image and classification.'})

            return redirect('image_list')
    else:
        form = ImageUploadForm()
    return render(request, 'imageupload/upload_image.html', {'form': form})

def image_list(request):
    images = Image.objects.all().order_by('-uploaded_at')
    latest_image = images.first()
    current_location = latest_image.address if latest_image else 'Unknown'
    return render(request, 'imageupload/image_list.html', {'current_location': current_location})