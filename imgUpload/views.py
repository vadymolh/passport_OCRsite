from multiprocessing import Process
from django.shortcuts import render
from django.contrib.gis.geoip2 import GeoIP2
from .forms import ImageForm
import os
import sys
import datetime
from datetime import date
import json
from .align_document import align_image
from passporteye import read_mrz
import pytesseract

script_directory = os.path.dirname(os.path.abspath(__file__))

tesseract_exe_path = os.path.join(script_directory, 'Tesseract-OCR', 'tesseract.exe')

# Check if the Tesseract executable exists.
if os.path.isfile(tesseract_exe_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_exe_path
else:
    print("Tesseract OCR is not found. Please ensure it is in the script's directory.")


def process_image(image_path):
    extracted_fields, formatted_text = ocr_passport(image_path)
    print(formatted_text)
    
    return extracted_fields


def upload(request):
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    #     ip = request.META.get('REMOTE_ADDR')
    
    device_type = ""
    browser_type = ""
    browser_version = ""
    os_type = ""
    os_version = ""
    if request.user_agent.is_mobile:
        device_type = "Mobile"
    if request.user_agent.is_tablet:
        device_type = "Tablet"
    if request.user_agent.is_pc:
        device_type = "PC"
    
    browser_type = request.user_agent.browser.family
    browser_version = request.user_agent.browser.version_string
    os_type = request.user_agent.os.family
    os_version = request.user_agent.os.version_string
    
    # g = GeoIP2(path=os.path.join(script_directory, 'geolite2-data'))
    # location = g.city(ip)
    # location_country = location["country_name"]
    # location_city = location["city"]
    
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            image_path = img_obj.image.path

            # # Get user's geolocation
            # user_ip = request.META.get('REMOTE_ADDR')
            # g = GeoIP2(path=os.path.join(script_directory, 'geolite2-data'))
            # try:
            #     user_location = g.city(user_ip)
            #     user_latitude = user_location['latitude']
            #     user_longitude = user_location['longitude']
                
            #     print(f"User's geolocation: Latitude - {user_latitude}, Longitude - {user_longitude}")

            # except Exception as e:
            #     print(f"Error getting user's geolocation: {e}")

            fields = process_image(image_path)
            f"Name: {fields['name']}\n" \
            f"Expiry Date: {fields['expiry_date']}\n" \
            f"Date of Birth: {fields['date_of_birth']}\n" \
            f"Passport Number: {fields['passport_number']}\n" \
            f"Sex: {fields['sex']}\n" \
            f"Nationality: {fields['nationality']}\n"
            
            context = {
                'form': form,
                'img_obj': img_obj,
                "device_type": device_type,
                "browser_type": browser_type,
                "browser_version": browser_version,
                "os_type": os_type,
                "os_version": os_version,
                "Name": fields['name'],
                "Expiry_Date": fields['expiry_date'],
                "Date_of_Birth": fields['date_of_birth'],
                "Passport_Number": fields['passport_number'],
                "Sex": fields['sex'],
                "Nationality": fields['nationality'],
                # "ip": ip,
                # "location_country": location_country,
                # "location_city": location_city
            }

            return render(request, 'index.html', context)
    else:
        form = ImageForm()
        
        context = {
            'form': form,
            "device_type": device_type,
            "browser_type": browser_type,
            "browser_version": browser_version,
            "os_type":os_type,
            "os_version":os_version,
            # "ip": ip,
            # "location_country": location_country,
            # "location_city": location_city
        }
        
        return render(request, 'index.html', context)
    

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
        expiry_date = datetime.datetime.strptime(fields["expiry_date"], "%y%m%d").strftime("%d/%m/%Y")
        fields["expiry_date"] = expiry_date

    # Convert date of birth to a common format (YYMMDD to DD/MM/YYYY).
    if len(fields["date_of_birth"]) == 6:
        dob = datetime.datetime.strptime(fields["date_of_birth"], "%y%m%d").strftime("%d/%m/%Y")
        fields["date_of_birth"] = dob

    # Adjust century if the birth date is in the future.
    if datetime.datetime.strptime(dob, "%d/%m/%Y").date() > date.today():
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
    # output_folder = os.path.join(sys.path[0], "Output")
    # os.makedirs(output_folder, exist_ok=True)
    # print("Aligning the document...")

    # # Perform image alignment and save the aligned image.
    # aligned_image = align_image(image_path, os.path.join(sys.path[0], "template.jpg"),
    #                             os.path.join(sys.path[0], "Output"), 200000, 0.01)
    
    # # Preprocess image and get the path of the preprocessed image.
    # preprocessed_image_path = os.path.join(sys.path[0], "Output", 
    #                                        os.path.splitext(os.path.basename(image_path))[0] + 
    #                                        "_aligned.jpg")
    # Process preprocessed image using passporteye.
    mrz = read_mrz(image_path, extra_cmdline_params='-l ocrb')

    # Obtain MRZ data.
    mrz_data = mrz.to_dict()

    extracted_fields, formatted_text = extract_fields(mrz_data)

    # output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(image_path))[0] + ".json")

    # with open(output_file, "w") as file:
    #     json.dump(extracted_fields, file, indent=4)
    
    return extracted_fields, formatted_text


def success_processing(request, img_obj):
    pass
    return render(request,  'index.html')
