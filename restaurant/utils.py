# from django.conf import settings
# import os
# import qrcode


# def generate_qr(data, filename):
#     pass
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(data)
#     qr.make(fit=True)
#     img = qr.make_image(fill='black', back_color='white')

#     file_path = os.path.join(settings.STATIC_URL, 'qr_codes', filename)
    
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)
#     img.save(file_path)
