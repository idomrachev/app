from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import random
import re
from .models import PhoneUser, DamageAssessment, DamagePhoto, Calculation, SparePart, RepairWork


def get_current_user(request):
    """Get current user from session"""
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return PhoneUser.objects.get(id=user_id, is_verified=True)
        except PhoneUser.DoesNotExist:
            pass
    return None


def login_required_custom(view_func):
    """Custom login required decorator"""
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return redirect('phone_input')
        request.current_user = user
        return view_func(request, *args, **kwargs)
    return wrapper


def phone_input(request):
    """Page 1: Phone number input"""
    if get_current_user(request):
        return redirect('damage_form')
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        # Clean phone number
        phone_clean = re.sub(r'[^\d+]', '', phone)
        
        if not phone_clean or len(phone_clean) < 10:
            messages.error(request, 'Введите корректный номер телефона')
            return render(request, 'pages/phone_input.html')
        
        # Generate code (mock - always 1234 for testing)
        code = '1234'  # In production: str(random.randint(1000, 9999))
        
        # Create or update user
        user, created = PhoneUser.objects.get_or_create(phone=phone_clean)
        user.verification_code = code
        user.save()
        
        # Store phone in session for verification
        request.session['pending_phone'] = phone_clean
        
        # Mock SMS sending
        print(f"[SMS] Code {code} sent to {phone_clean}")
        messages.success(request, f'Код подтверждения отправлен на {phone_clean}')
        
        return redirect('verify_code')
    
    return render(request, 'pages/phone_input.html')


def verify_code(request):
    """Page 2: SMS code verification"""
    if get_current_user(request):
        return redirect('damage_form')
    
    pending_phone = request.session.get('pending_phone')
    if not pending_phone:
        return redirect('phone_input')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        try:
            user = PhoneUser.objects.get(phone=pending_phone)
            if user.verification_code == code:
                user.is_verified = True
                user.verification_code = None
                user.save()
                
                request.session['user_id'] = str(user.id)
                del request.session['pending_phone']
                
                messages.success(request, 'Вход выполнен успешно!')
                return redirect('damage_form')
            else:
                messages.error(request, 'Неверный код подтверждения')
        except PhoneUser.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
            return redirect('phone_input')
    
    return render(request, 'pages/verify_code.html', {'phone': pending_phone})


@login_required_custom
def damage_form(request):
    """Page 3: Damage assessment form"""
    if request.method == 'POST':
        vin = request.POST.get('vin', '').strip().upper()
        description = request.POST.get('description', '').strip()
        photos = request.FILES.getlist('photos')
        
        if not vin or len(vin) != 17:
            messages.error(request, 'VIN-номер должен содержать 17 символов')
            return render(request, 'pages/damage_form.html')
        
        if not photos:
            messages.error(request, 'Прикрепите хотя бы одну фотографию')
            return render(request, 'pages/damage_form.html')
        
        # Create assessment
        assessment = DamageAssessment.objects.create(
            user=request.current_user,
            vin=vin,
            description=description
        )
        
        # Save photos
        for photo in photos:
            DamagePhoto.objects.create(
                assessment=assessment,
                image=photo
            )
        
        messages.success(request, 'Заявка успешно отправлена!')
        return redirect('calculations')
    
    return render(request, 'pages/damage_form.html')


@login_required_custom
def calculations(request):
    """Page 4: My calculations"""
    assessments = DamageAssessment.objects.filter(user=request.current_user).prefetch_related(
        'calculation', 'calculation__parts', 'calculation__works'
    )
    return render(request, 'pages/calculations.html', {'assessments': assessments})


@login_required_custom
def calculation_detail(request, calc_id):
    """API: Get calculation detail as JSON"""
    try:
        assessment = DamageAssessment.objects.get(id=calc_id, user=request.current_user)
        calc = getattr(assessment, 'calculation', None)
        
        data = {
            'vin': assessment.vin,
            'date': assessment.created_at.strftime('%d.%m.%Y'),
            'status': assessment.status,
            'description': assessment.description,
            'parts': [],
            'works': [],
            'total_parts_cost': 0,
            'total_labor_cost': 0,
            'total_cost': 0
        }
        
        if calc:
            data['parts'] = [
                {'name': p.name, 'article': p.article, 'price': float(p.price), 'quantity': p.quantity}
                for p in calc.parts.all()
            ]
            data['works'] = [
                {'name': w.name, 'part_name': w.part_name, 'hours': float(w.hours), 'rate': float(w.rate_per_hour)}
                for w in calc.works.all()
            ]
            data['total_parts_cost'] = float(calc.total_parts_cost)
            data['total_labor_cost'] = float(calc.total_labor_cost)
            data['total_cost'] = float(calc.total_cost)
        
        return JsonResponse(data)
    except DamageAssessment.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


def contacts(request):
    """Page 5: Contacts"""
    return render(request, 'pages/contacts.html')


def logout_view(request):
    """Logout and clear session"""
    request.session.flush()
    messages.success(request, 'Вы вышли из системы')
    return redirect('phone_input')
