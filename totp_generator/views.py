import pyotp
import qrcode
import json
import time
from io import BytesIO
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

def totp_home(request):
    """Simple TOTP generator home page"""
    demo_secret = "JBSWY3DPEHPK3PXP"
    return render(request, 'totp.html', {
        'demo_secret': demo_secret
    })

@csrf_exempt
@require_http_methods(["POST"])
def generate_totp(request):
    """Generate TOTP code from secret"""
    try:
        data = json.loads(request.body)
        secret = data.get('secret', '').strip().upper()
        
        if not secret:
            return JsonResponse({
                'success': False,
                'error': 'Secret is required'
            })
        
        # Validate Base32 secret
        try:
            base64.b32decode(secret, casefold=True)
        except:
            return JsonResponse({
                'success': False,
                'error': 'Invalid Base32 secret'
            })
        
        # Generate TOTP
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        # Calculate remaining time
        remaining = totp.interval - (time.time() % totp.interval)
        
        return JsonResponse({
            'success': True,
            'code': code,
            'remaining_seconds': int(remaining)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def generate_qr(request):
    """Generate QR code for TOTP setup"""
    try:
        secret = request.GET.get('secret', '').strip().upper()
        if not secret:
            return JsonResponse({
                'success': False,
                'error': 'Secret parameter required'
            })
        
        # Create TOTP and provisioning URI
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name="Test User",
            issuer_name="TOTP Generator"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_data = base64.b64encode(buffer.getvalue()).decode()
        
        return JsonResponse({
            'success': True,
            'qr_code': f'data:image/png;base64,{img_data}',
            'secret': secret
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })