"""
Management command to create demo calculation data for testing
"""
from django.core.management.base import BaseCommand
from damage_project.models import (
    PhoneUser, DamageAssessment, Calculation, SparePart, RepairWork
)
from decimal import Decimal


class Command(BaseCommand):
    help = 'Creates demo calculation data for testing the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            default='+79991234567',
            help='Phone number of the user to create demo data for'
        )

    def handle(self, *args, **options):
        phone = options['phone']
        
        # Get or create user
        user, created = PhoneUser.objects.get_or_create(
            phone=phone,
            defaults={'is_verified': True}
        )
        if created:
            self.stdout.write(f'Created new user: {phone}')
        else:
            self.stdout.write(f'Using existing user: {phone}')
        
        # Demo data for assessments
        demo_assessments = [
            {
                'vin': 'WVWZZZ3CZWE123456',
                'description': 'Повреждение переднего бампера и левого крыла после ДТП на парковке',
                'status': 'completed',
                'parts': [
                    {'name': 'Бампер передний', 'article': 'VAG-5G0807221', 'price': 28500, 'quantity': 1},
                    {'name': 'Крыло переднее левое', 'article': 'VAG-5G0821105', 'price': 15200, 'quantity': 1},
                    {'name': 'Фара левая', 'article': 'VAG-5G0941005', 'price': 42000, 'quantity': 1},
                    {'name': 'Решетка радиатора', 'article': 'VAG-5G0853651', 'price': 8900, 'quantity': 1},
                    {'name': 'Усилитель бампера', 'article': 'VAG-5G0807109', 'price': 12300, 'quantity': 1},
                ],
                'works': [
                    {'name': 'Снятие/установка бампера', 'part_name': 'Бампер передний', 'hours': 2.0, 'rate': 1500},
                    {'name': 'Окраска бампера', 'part_name': 'Бампер передний', 'hours': 4.5, 'rate': 1800},
                    {'name': 'Замена крыла', 'part_name': 'Крыло переднее левое', 'hours': 3.0, 'rate': 1500},
                    {'name': 'Окраска крыла', 'part_name': 'Крыло переднее левое', 'hours': 3.5, 'rate': 1800},
                    {'name': 'Регулировка фары', 'part_name': 'Фара левая', 'hours': 0.5, 'rate': 1500},
                    {'name': 'Замена решетки', 'part_name': 'Решетка радиатора', 'hours': 0.5, 'rate': 1500},
                ],
            },
            {
                'vin': 'XTA21703090012345',
                'description': 'Вмятина на задней двери и царапины на боковой части',
                'status': 'completed',
                'parts': [
                    {'name': 'Дверь задняя левая', 'article': 'LADA-21700620001', 'price': 18500, 'quantity': 1},
                    {'name': 'Молдинг двери', 'article': 'LADA-21700821405', 'price': 2100, 'quantity': 1},
                    {'name': 'Ручка двери наружная', 'article': 'LADA-21700610515', 'price': 1850, 'quantity': 1},
                ],
                'works': [
                    {'name': 'Замена двери', 'part_name': 'Дверь задняя левая', 'hours': 2.5, 'rate': 1400},
                    {'name': 'Окраска двери', 'part_name': 'Дверь задняя левая', 'hours': 3.0, 'rate': 1600},
                    {'name': 'Полировка кузова', 'part_name': '', 'hours': 2.0, 'rate': 1200},
                    {'name': 'Установка молдинга', 'part_name': 'Молдинг двери', 'hours': 0.3, 'rate': 1400},
                ],
            },
            {
                'vin': 'WBAPH5C55BA123789',
                'description': 'Ожидает обработки - повреждение заднего бампера',
                'status': 'pending',
                'parts': [],
                'works': [],
            },
        ]
        
        for demo in demo_assessments:
            # Check if assessment with this VIN already exists for user
            existing = DamageAssessment.objects.filter(user=user, vin=demo['vin']).first()
            if existing:
                self.stdout.write(f"Assessment for VIN {demo['vin']} already exists, skipping...")
                continue
            
            # Create assessment
            assessment = DamageAssessment.objects.create(
                user=user,
                vin=demo['vin'],
                description=demo['description'],
                status=demo['status']
            )
            self.stdout.write(f"Created assessment: {demo['vin']}")
            
            # Create calculation if parts/works exist
            if demo['parts'] or demo['works']:
                # Calculate totals
                total_parts = sum(Decimal(str(p['price'])) * p['quantity'] for p in demo['parts'])
                total_labor = sum(Decimal(str(w['hours'])) * Decimal(str(w['rate'])) for w in demo['works'])
                
                calc = Calculation.objects.create(
                    assessment=assessment,
                    total_parts_cost=total_parts,
                    total_labor_cost=total_labor,
                    total_cost=total_parts + total_labor
                )
                
                # Create parts
                for part_data in demo['parts']:
                    SparePart.objects.create(
                        calculation=calc,
                        name=part_data['name'],
                        article=part_data['article'],
                        price=Decimal(str(part_data['price'])),
                        quantity=part_data['quantity']
                    )
                
                # Create works
                for work_data in demo['works']:
                    RepairWork.objects.create(
                        calculation=calc,
                        name=work_data['name'],
                        part_name=work_data['part_name'],
                        hours=Decimal(str(work_data['hours'])),
                        rate_per_hour=Decimal(str(work_data['rate']))
                    )
                
                self.stdout.write(
                    f"  -> Added calculation: {len(demo['parts'])} parts, {len(demo['works'])} works, "
                    f"total: {total_parts + total_labor} ₽"
                )
        
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
