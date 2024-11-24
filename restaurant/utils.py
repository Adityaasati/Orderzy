   
from django.conf import settings
import os
import qrcode

def generate_qr(data, filename):
    print("generate")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')


    file_path = os.path.join(settings.BASE_DIR, 'orderzy', 'static', 'qr_codes', filename)

    print("filepath",file_path)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    img.save(file_path)
