from django.db import models
import uuid


class PhoneUser(models.Model):
    """User model based on phone number"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'phone_users'

    def __str__(self):
        return self.phone


class DamageAssessment(models.Model):
    """Damage assessment submission"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(PhoneUser, on_delete=models.CASCADE, related_name='assessments')
    vin = models.CharField(max_length=17)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')

    class Meta:
        db_table = 'damage_assessments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vin} - {self.created_at.strftime('%d.%m.%Y')}"


class DamagePhoto(models.Model):
    """Photos attached to damage assessment"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(DamageAssessment, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'damage_photos'

    def __str__(self):
        return f"Photo for {self.assessment.vin}"


class Calculation(models.Model):
    """Calculation result for damage assessment"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.OneToOneField(DamageAssessment, on_delete=models.CASCADE, related_name='calculation')
    created_at = models.DateTimeField(auto_now_add=True)
    total_parts_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'calculations'
        ordering = ['-created_at']

    def __str__(self):
        return f"Calculation for {self.assessment.vin}"


class SparePart(models.Model):
    """Spare part in calculation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    calculation = models.ForeignKey(Calculation, on_delete=models.CASCADE, related_name='parts')
    name = models.CharField(max_length=255)
    article = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'spare_parts'

    def __str__(self):
        return f"{self.name} ({self.article})"


class RepairWork(models.Model):
    """Repair work in calculation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    calculation = models.ForeignKey(Calculation, on_delete=models.CASCADE, related_name='works')
    name = models.CharField(max_length=255)
    part_name = models.CharField(max_length=255, blank=True)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=1500)

    class Meta:
        db_table = 'repair_works'

    def __str__(self):
        return f"{self.name} - {self.hours}ч"
