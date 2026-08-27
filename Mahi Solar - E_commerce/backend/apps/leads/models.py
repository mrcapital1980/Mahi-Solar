from django.db import models

# Create your models here.
from django.db import models


class ContactLead(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class SiteVisitLead(models.Model):
    SLOT_CHOICES = [
        ('morning', 'Morning (9AM - 12PM)'),
        ('afternoon', 'Afternoon (12PM - 3PM)'),
        ('evening', 'Evening (3PM - 6PM)'),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100, default='Surat')
    preferred_date = models.DateField()
    preferred_slot = models.CharField(max_length=20, choices=SLOT_CHOICES)
    notes = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.preferred_date}"


class CalculatorLead(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    monthly_bill = models.DecimalField(max_digits=10, decimal_places=2)
    units_per_month = models.IntegerField()
    recommended_kw = models.DecimalField(max_digits=5, decimal_places=2)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    roof_area = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.recommended_kw}KW"
