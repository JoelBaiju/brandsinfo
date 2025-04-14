from django.http import JsonResponse, HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from ..models import Plan_Varients, PhonePeTransaction, Buisnesses
import uuid
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from brandsinfo import phonepe
from brandsinfo.phonepe import initiate_payment as phonepe_initiate_payment
from rest_framework import status as rest_framework_status

@api_view(['POST'])
def initiate_payment_view(request):
    if request.method == 'POST':
        try:
            # Get and validate parameters
            bid = request.data.get('bid')  # Changed from POST to data for DRF
            pvid = request.data.get('pvid')
            print(bid, pvid)
            if not bid or not pvid:
                return Response(
                    {'error': 'Both business ID (bid) and plan variant ID (pvid) are required'},
                    status=rest_framework_status.HTTP_400_BAD_REQUEST
                )

            # Get related objects
            try:
                plan_variant = Plan_Varients.objects.get(id=pvid)
                business = Buisnesses.objects.get(id=bid)
            except (Plan_Varients.DoesNotExist, Buisnesses.DoesNotExist):
                return Response(
                    {'error': 'Invalid business or plan variant ID'},
                    status=rest_framework_status.HTTP_400_BAD_REQUEST
                )


            response = phonepe_initiate_payment(int(plan_variant.price))  
            if response['success']:
                print(f"Redirect user to:")
                status = check_payment_status(request,response['order_id'])
                print("Payment status:" ,status)

                with transaction.atomic():
                    PhonePeTransaction.objects.create(
                        order_id=response['order_id'],   
                        user=request.user if request.user.is_authenticated else None,
                        amount=plan_variant.price,
                        business=business,
                        plan=plan_variant.plan,
                        plan_variant=plan_variant,
                        # payment_url=response['redirect_url'],
                        payment_url='',
                        # phonepe_response=response,
                        status='INITIATED'
                    )
            else:
                return Response(
                    {'error': 'Payment initiation failed', 'details': response},
                    status=rest_framework_status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'redirect_url': response['redirect_url'],
                'success': True,
                'message': 'Payment initiated successfully',
            },status=rest_framework_status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            # print(response)
            return Response(    
                {'error': 'Internal server error', 'details': str(e),'redirect_url': response['redirect_url']},
                
            )
    
    return Response(
        {'error': 'Only POST method allowed'},
    )
    
   
   
   
   
   
   
   
   
   
import json
   
   
   
@csrf_exempt
def payment_callback(request):
    print("\n=== PhonePe Callback Received ===")
    print("Method:", request.method)
    print("Headers:", dict(request.headers))
    print("GET Params:", dict(request.GET))  # Check URL query params
    print("Body:", request.body.decode('utf-8'))  # Empty for GET

    # Handle GET request (redirect after payment)
    if request.method == "GET":
        transaction_id = request.GET.get("transactionId")  # Check PhonePe docs for actual param name
        status = request.GET.get("status")  # e.g., "SUCCESS", "FAILED"

        if not transaction_id:
            return HttpResponseBadRequest("Missing transactionId")

        try:
            txn = PhonePeTransaction.objects.get(order_id=transaction_id)
            txn.status = status
            txn.save()
            return JsonResponse({"status": "success"})
        except PhonePeTransaction.DoesNotExist:
            return HttpResponseBadRequest("Transaction not found")

    # Handle POST request (webhook with JSON payload)
    elif request.method == "POST":
        auth_header = request.headers.get("X-VERIFY", "")
        callback_body = request.body.decode('utf-8')

        if not callback_body:
            return HttpResponseBadRequest("Empty callback body")

        try:
            client = phonepe.client
            callback_response = client.validate_callback(
                username="BrandsInfo",
                password="Listing2025",
                callback_header_data=auth_header,
                callback_response_data=callback_body
            )
            order_id = callback_response.order_id
            transaction_state = callback_response.state
            txn = PhonePeTransaction.objects.get(order_id=order_id)
            txn.status = transaction_state
            txn.phonepe_callback = json.loads(callback_body)
            txn.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            print("Callback Error:", str(e))
            return HttpResponseBadRequest({"error": "Invalid callback"})

    return HttpResponseBadRequest("Invalid request method")
   
   
   
   
   
   
   
   
   
   
   
   
   
   
@csrf_exempt
def payment_callback2(request):
    print("\n=== PhonePe Callback 22222 Received ===")
    print("Method:", request.method)
    print("Headers:", dict(request.headers))
    print("GET Params:", dict(request.GET))  # Check URL query params
    print("Body:", request.body.decode('utf-8'))  # Empty for GET

    # Handle GET request (redirect after payment)
    if request.method == "GET":
        transaction_id = request.GET.get("transactionId")  # Check PhonePe docs for actual param name
        status = request.GET.get("status")  # e.g., "SUCCESS", "FAILED"

        if not transaction_id:
            return HttpResponseBadRequest("Missing transactionId")

        try:
            txn = PhonePeTransaction.objects.get(order_id=transaction_id)
            txn.status = status
            txn.save()
            return JsonResponse({"status": "success"})
        except PhonePeTransaction.DoesNotExist:
            return HttpResponseBadRequest("Transaction not found")

    # Handle POST request (webhook with JSON payload)
    elif request.method == "POST":
        auth_header = request.headers.get("X-VERIFY", "")
        callback_body = request.body.decode('utf-8')

        if not callback_body:
            return HttpResponseBadRequest("Empty callback body")

        try:
            client = phonepe.client
            callback_response = client.validate_callback(
                username="BrandsInfo",
                password="Listing2025",
                callback_header_data=auth_header,
                callback_response_data=callback_body
            )
            order_id = callback_response.order_id
            transaction_state = callback_response.state
            txn = PhonePeTransaction.objects.get(order_id=order_id)
            txn.status = transaction_state
            txn.phonepe_callback = json.loads(callback_body)
            txn.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            print("Callback Error:", str(e))
            return HttpResponseBadRequest({"error": "Invalid callback"})

    return HttpResponseBadRequest("Invalid request method")
   
   
   
   
   
   
   
   
   
   












































































def check_payment_status(request, order_id):
    try:
        txn = PhonePeTransaction.objects.get(
            order_id=order_id
        )
        
        status_response = phonepe.check_payment_status(order_id)
        
        # Update our record if status changed
        if status_response['status'] != txn.status:
            txn.status = status_response['status']
            txn.phonepe_response = status_response
            txn.save()
        
        return JsonResponse({
            'order_id': order_id,
            'amount': txn.amount,
            'status': txn.status,
            'user_email': txn.user_email,
            'timestamp': txn.created_at.isoformat(),
            'gateway_response': status_response
        })
        
    except PhonePeTransaction.DoesNotExist:
        return HttpResponseBadRequest({'error': 'Transaction not found'})
    except Exception as e:
        return HttpResponseServerError({'error': str(e)})
    
    
    
    
    
# from communications.notifications import new_plan_purchased
    
# def puchase_plan(request):
#     pvid = request.POST.get('pvid')
#     bid = request.POST.get('bid')
#     plan_varient = Plan_Varients.objects.get(id=pvid)
#     buisness = Buisnesses.objects.get(id=bid)
#     if not pvid or not bid:
#         return Response({'error': 'pvid and bid are required'}, 400)
#     new_plan_purchased(buisness, plan_varient)




















from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
import datetime

# def generate_invoice_pdf(request, order_id):
#     # Get order data - replace with your actual model and logic
#     order = get_object_or_404(Order, id=order_id)
    
#     # Calculate additional fields
#     context = {
#         'username': order.user.username,
#         'business_name': order.business.name,
#         'plan_name': order.plan.name,
#         'start_date': order.start_date,
#         'expiry_date': order.expiry_date,
#         'duration_days': (order.expiry_date - order.start_date).days,
#         'price': order.plan.price,
#         'gst_amount': order.plan.price * 0.18,  # Assuming 18% GST
#         'total_amount': order.plan.price * 1.18,
#         'invoice_number': f"BI-{order.id}",
#         'timestamp': datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
#     }
    
#     template_path = 'invoice_template.html'
#     template = get_template(template_path)
#     html = template.render(context)
    
#     # Create PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="Brandsinfo_Invoice_{order.id}.pdf"'
    
#     # Generate PDF
#     pisa_status = pisa.CreatePDF(html, dest=response)
    
#     if pisa_status.err:
#         return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response