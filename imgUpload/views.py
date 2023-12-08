from multiprocessing import Process
from django.shortcuts import render
from .forms import ImageForm
import os
import sys
import datetime
from datetime import date
import json
from .align_document import align_image
from passporteye import read_mrz


def process_image(image_path, result_dict):
    extracted_fields, formatted_text = ocr_passport(image_path)


def upload(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            image_path = img_obj.image.path

            # Start parallel processing.
            process = Process(target=process_image, args=(image_path))
            process.start()
            process.join()

            return render(request, 'index.html', {'form': form, 'img_obj': img_obj})
    else:
        form = ImageForm()    
        return render(request, 'index.html', {'form': form})
    

def extract_fields(mrz_data):
    fields = {
        "name": "",
        "expiry_date": "",
        "date_of_birth": "",
        "date_of_issue": "",
        "passport_number": "",
        "nationality": "",
        "sex": ""
    }

    fields["name"] = mrz_data.get("names", "") + " " + mrz_data.get("surname", "")
    fields["name"] = fields["name"].replace("<", "")
    fields["expiry_date"] = mrz_data.get("expiration_date", "").replace("O", "0").replace("o", "0").replace("<", "")
    fields["date_of_birth"] = mrz_data.get("date_of_birth", "").replace("O", "0").replace("o", "0").replace("<", "")
    fields["passport_number"] = mrz_data.get("number", "").replace("O", "0").replace("o", "0").replace("<", "")
    fields["nationality"] = mrz_data.get("country", "").replace("<", "")
    fields["sex"] = mrz_data.get("sex", "").replace("<", "")

    # Convert expiry date to a common format (YYMMDD to DD/MM/YYYY).
    if len(fields["expiry_date"]) == 6:
        expiry_date = datetime.strptime(fields["expiry_date"], "%y%m%d").strftime("%d/%m/%Y")
        fields["expiry_date"] = expiry_date

    # Convert date of birth to a common format (YYMMDD to DD/MM/YYYY).
    if len(fields["date_of_birth"]) == 6:
        dob = datetime.strptime(fields["date_of_birth"], "%y%m%d").strftime("%d/%m/%Y")
        fields["date_of_birth"] = dob

    # Adjust century if the birth date is in the future.
    if datetime.strptime(dob, "%d/%m/%Y").date() > date.today():
        dob = dob[:-4] + str(int(dob[-4:]) - 100)
        fields["date_of_birth"] = dob

    formatted_text = f"Name: {fields['name']}\n" \
                     f"Expiry Date: {fields['expiry_date']}\n" \
                     f"Date of Birth: {fields['date_of_birth']}\n" \
                     f"Passport Number: {fields['passport_number']}\n" \
                     f"Sex: {fields['sex']}\n" \
                     f"Nationality: {fields['nationality']}\n"

    return fields, formatted_text    

    
def ocr_passport(image_path):
    output_folder = os.path.join(sys.path[0], "Output")
    os.makedirs(output_folder, exist_ok=True)
    print("Aligning the document...")

    # Perform image alignment and save the aligned image.
    aligned_image = align_image(image_path, os.path.join(sys.path[0], "template.jpg"),
                                os.path.join(sys.path[0], "Output"), 200000, 0.01)
    
    # Preprocess image and get the path of the preprocessed image.
    preprocessed_image_path = os.path.join(sys.path[0], "Output", 
                                           os.path.splitext(os.path.basename(image_path))[0] + 
                                           "_aligned.jpg")
    # Process preprocessed image using passporteye.
    mrz = read_mrz(preprocessed_image_path)

    # Obtain MRZ data.
    mrz_data = mrz.to_dict()

    extracted_fields, formatted_text = extract_fields(mrz_data)

    output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(image_path))[0] + ".json")

    with open(output_file, "w") as file:
        json.dump(extracted_fields, file, indent=4)
    
    return extracted_fields, formatted_text


def success_processing(request, img_obj):
    pass
    return render(request,  'index.html')
