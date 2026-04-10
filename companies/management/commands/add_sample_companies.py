from django.core.management.base import BaseCommand
from companies.models import Company


class Command(BaseCommand):
    help = 'Add sample Bangladeshi companies to the database'

    def handle(self, *args, **options):
        # Sample Bangladeshi companies data
        companies_data = [
            {
                'name': 'Grameenphone Ltd.',
                'sector': 'Telecom',
                'headquarters': 'Dhaka',
                'founded': 1996,
                'logo_url': 'https://logo.clearbit.com/grameenphone.com.bd',
                'description': 'Leading telecommunications operator in Bangladesh providing mobile, broadband, and digital services.'
            },
            {
                'name': 'Square Pharmaceuticals Ltd.',
                'sector': 'Pharmaceuticals',
                'headquarters': 'Dhaka',
                'founded': 1958,
                'logo_url': 'https://logo.clearbit.com/squarebd.com',
                'description': 'One of the largest pharmaceutical companies in Bangladesh manufacturing and exporting medicines.'
            },
            {
                'name': 'Dhaka Bank Limited',
                'sector': 'Banking',
                'headquarters': 'Dhaka',
                'founded': 1995,
                'logo_url': 'https://logo.clearbit.com/dhakabank.com.bd',
                'description': 'Commercial bank providing comprehensive banking solutions including retail and corporate services.'
            },
            {
                'name': 'BRAC Bank Limited',
                'sector': 'Banking',
                'headquarters': 'Dhaka',
                'founded': 1999,
                'logo_url': 'https://logo.clearbit.com/bracbank.com',
                'description': 'Fastest growing bank in Bangladesh with innovative financial solutions and digital services.'
            },
            {
                'name': 'Beximco Pharmaceuticals Ltd.',
                'sector': 'Pharmaceuticals',
                'headquarters': 'Dhaka',
                'founded': 1966,
                'logo_url': 'https://logo.clearbit.com/beximco.com.bd',
                'description': 'Major pharmaceutical manufacturer and exporter with presence in multiple therapeutic categories.'
            },
            {
                'name': 'ACI Limited',
                'sector': 'Conglomerate',
                'headquarters': 'Dhaka',
                'founded': 1973,
                'logo_url': 'https://logo.clearbit.com/aci.com.bd',
                'description': 'Diversified conglomerate with interests in pharmaceuticals, chemicals, consumer goods, and IT services.'
            },
            {
                'name': 'Banglalink Digital Communications Ltd.',
                'sector': 'Telecom',
                'headquarters': 'Dhaka',
                'founded': 2005,
                'logo_url': 'https://logo.clearbit.com/banglalink.com.bd',
                'description': 'Major telecommunications provider offering mobile, broadband, and digital services in Bangladesh.'
            },
            {
                'name': 'National Bank Limited',
                'sector': 'Banking',
                'headquarters': 'Dhaka',
                'founded': 1983,
                'logo_url': 'https://logo.clearbit.com/nblbd.com',
                'description': 'One of the oldest commercial banks in Bangladesh providing diverse financial services.'
            },
            {
                'name': 'Unilever Bangladesh Limited',
                'sector': 'Consumer Goods',
                'headquarters': 'Dhaka',
                'founded': 1965,
                'logo_url': 'https://logo.clearbit.com/unilever.com',
                'description': 'FMCG company manufacturing and distributing diverse consumer products including personal care and foods.'
            },
            {
                'name': 'Robi Axiata Limited',
                'sector': 'Telecom',
                'headquarters': 'Dhaka',
                'founded': 1997,
                'logo_url': 'https://logo.clearbit.com/robi.com.bd',
                'description': 'Second largest mobile operator in Bangladesh providing comprehensive telecom and digital services.'
            },
            {
                'name': 'Incepta Pharmaceuticals Ltd.',
                'sector': 'Pharmaceuticals',
                'headquarters': 'Dhaka',
                'founded': 1999,
                'logo_url': 'https://logo.clearbit.com/inceptapharma.com',
                'description': 'Leading pharmaceutical manufacturer with focus on research and development of quality medicines.'
            },
            {
                'name': 'Bangladesh Shipping Corporation',
                'sector': 'Shipping',
                'headquarters': 'Dhaka',
                'founded': 1972,
                'logo_url': '',
                'description': 'State-owned shipping company responsible for maritime transport and cargo management.'
            },
        ]

        # Add companies to database
        created_count = 0
        skipped_count = 0

        for company_data in companies_data:
            company, created = Company.objects.get_or_create(
                name=company_data['name'],
                defaults={
                    'sector': company_data['sector'],
                    'headquarters': company_data['headquarters'],
                    'founded': company_data['founded'],
                    'logo_url': company_data.get('logo_url', ''),
                    'description': company_data.get('description', ''),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Added: {company.name}'))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'→ Skipped: {company.name} (already exists)'))

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} companies'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count} companies'))
        self.stdout.write(self.style.SUCCESS('Sample data added successfully! ✨'))
        self.stdout.write('='*50)
