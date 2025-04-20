
from ..models import PhonePeTransaction
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
import datetime

def generate_invoice_pdf(order_id):
    # Get order data - replace with your actual model and logic
    txn = get_object_or_404(PhonePeTransaction, order_id=order_id)
    
    # Calculate additional fields
   
    context = {
        'username': txn.user.first_name,
        'business_name': txn.business.name,
        'plan_name': txn.plan.plan_name,
        'start_date': txn.created_at,
        'expiry_date': txn.expire_at,
        'duration_days': txn.plan_variant.duration,
        'price': txn.plan_variant.price,
        'gst_amount': 0,  # Assuming 18% GST
        'total_amount': txn.plan.price ,
        'invoice_number': f"BI-{txn.order_id}",
        'timestamp': datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
    }
    
    template_path = 'invoice_template.html'
    template = get_template(template_path)
    html = template.render(context)
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Brandsinfo_Invoice_{txn.id}.pdf"'
    
    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response








