import qrcode

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data('https://madannijr-outils-dsmp-reporting-app-i015z6.streamlit.app/')
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("qrcode_outil_reporting_des_flux.png")