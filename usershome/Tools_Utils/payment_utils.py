import os
import datetime
from django.conf import settings
from xhtml2pdf import pisa
from django.core.files import File
from io import BytesIO
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from ..models import PhonePeTransaction

def generate_invoice_pdf(order_id):
    txn = get_object_or_404(PhonePeTransaction, order_id=order_id)
    print('generating invoice for order_id:', order_id)
    context = {
        'username': txn.user.first_name,
        'business_name': txn.buisness.name,
        'plan_name': txn.plan.plan_name,
        'start_date': txn.created_at,
        'expiry_date': txn.expire_at,
        'duration_days': txn.plan_variant.duration,
        'price': txn.plan_variant.price,
        'gst_amount': 0,
        'total_amount': txn.plan_variant.price,
        'invoice_number': f"BI-{txn.order_id}",
        'timestamp': datetime.datetime.now().strftime("%Y%m%d%H%M%S"),

    }
    # logo_abspath = os.path.join(settings.MEDIA_ROOT, 'Home_pics', 'BI_logo.png')
    # context['logo_path'] = f'file://{logo_abspath}'


    template_path = 'payment_invoice.html'
    template = get_template(template_path)
    html = template.render(context)

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return None  # or raise an exception

    result.seek(0)
    file_name = f"invoice_{txn.id}.pdf"

    # Save to FileField
    txn.invoice.save(file_name, File(result))
    txn.save()

    return txn.invoice.url  