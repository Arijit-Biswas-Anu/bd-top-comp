"""
Management command to load Bangladesh EdTech startups from Excel file.
Usage: python manage.py load_edtech_startups
"""

import os
import pandas as pd
from django.core.management.base import BaseCommand
from companies.models import Startup


class Command(BaseCommand):
    help = 'Load Bangladesh EdTech startups from Excel file into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='/Users/mr.pogo/Desktop/prev_lab_proj/bd_top_comp/top_bangladesh_edtech_startups_20.xlsx',
            help='Path to Excel file containing startup data'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing startups before loading'
        )

    def handle(self, *args, **options):
        excel_file = options['file']
        clear_existing = options['clear']

        # Check if file exists
        if not os.path.exists(excel_file):
            self.stdout.write(
                self.style.ERROR(f'Error: File not found: {excel_file}')
            )
            return

        # Clear existing data if requested
        if clear_existing:
            count = Startup.objects.count()
            Startup.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} existing startups')
            )

        # Read Excel file
        try:
            df = pd.read_excel(excel_file)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Read Excel file: {excel_file}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'  Found {len(df)} startups')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading Excel file: {e}')
            )
            return

        # Verify required columns
        required_columns = ['name', 'sector', 'founder(s)', 'headquarters', 
                           'year_founded', 'total_funding', 'logo_url']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self.stdout.write(
                self.style.ERROR(f'Error: Missing columns: {missing_columns}')
            )
            return

        # Load data
        created_count = 0
        skipped_count = 0

        for idx, row in df.iterrows():
            try:
                # Check if startup already exists
                if Startup.objects.filter(name=row['name']).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⊘ Skipped (already exists): {row["name"]}'
                        )
                    )
                    skipped_count += 1
                    continue

                # Create startup instance
                startup = Startup(
                    name=row['name'],
                    sector=row['sector'],
                    founders=row['founder(s)'],
                    headquarters=row['headquarters'],
                    year_founded=int(row['year_founded']),
                    total_funding=str(row['total_funding']),
                    logo_url=row['logo_url'] if pd.notna(row['logo_url']) else ''
                )
                startup.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Created: {row["name"]}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error loading {row["name"]}: {e}')
                )
                skipped_count += 1

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(
            f'✓ Successfully created: {created_count} startups'
        ))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(
                f'⊘ Skipped: {skipped_count} startups'
            ))
        self.stdout.write('='*60)
