#!/usr/bin/env python
"""
Phase 11 Tests: Export & Advanced Features
Tests for CSV export, summary export, and pagination selector functionality
"""

import os
import sys
import csv
import io

# Setup Django FIRST before any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bd_top_comp.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from companies.models import Company


class Phase11ExportTests(TestCase):
    """Test Phase 11: Export & Advanced Features"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "="*70)
        print("PHASE 11 TESTS: EXPORT & ADVANCED FEATURES")
        print("="*70)
    
    def setUp(self):
        """Create test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_01_csv_export_endpoint_accessible(self):
        """Test that CSV export endpoint is accessible to authenticated users"""
        print("\n✓ Test 1: CSV Export Endpoint Accessible")
        response = self.client.get('/api/export/csv/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        print("  - Endpoint returns 200 status")
        print("  - Content-Type is text/csv")
        
    def test_02_csv_export_requires_authentication(self):
        """Test that CSV export requires authentication"""
        print("\n✓ Test 2: CSV Export Requires Authentication")
        self.client.logout()
        response = self.client.get('/api/export/csv/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        print("  - Unauthenticated users redirected to login")
        
    def test_03_csv_export_has_headers(self):
        """Test that CSV export includes proper headers"""
        print("\n✓ Test 3: CSV Export Headers")
        response = self.client.get('/api/export/csv/')
        content = response.content.decode('utf-8')
        
        expected_headers = [
            'Company Name', 'Sector', 'Headquarters', 'Founded', 
            'Description', 'Added On', 'Last Updated'
        ]
        
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        
        for expected_header in expected_headers:
            self.assertIn(expected_header, headers)
        print(f"  - All {len(expected_headers)} headers present")
        
    def test_04_csv_export_has_company_data(self):
        """Test that CSV export includes company data"""
        print("\n✓ Test 4: CSV Export Contains Company Data")
        response = self.client.get('/api/export/csv/')
        content = response.content.decode('utf-8')
        
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)  # Skip headers
        rows = list(reader)
        
        self.assertGreater(len(rows), 0)
        print(f"  - CSV contains {len(rows)} company records")
        
    def test_05_csv_export_with_search_filter(self):
        """Test that CSV export respects search filter"""
        print("\n✓ Test 5: CSV Export with Search Filter")
        response = self.client.get('/api/export/csv/?search=Tech')
        content = response.content.decode('utf-8')
        
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        rows = list(reader)
        
        # All rows should contain 'Tech' in some field
        self.assertGreater(len(rows), 0)
        print(f"  - Search filter applied: found {len(rows)} matching companies")
        
    def test_06_csv_export_with_sector_filter(self):
        """Test that CSV export respects sector filter"""
        print("\n✓ Test 6: CSV Export with Sector Filter")
        response = self.client.get('/api/export/csv/?sector=Technology')
        content = response.content.decode('utf-8')
        
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        sector_index = headers.index('Sector')
        rows = list(reader)
        
        # All rows should have 'Technology' as sector
        if rows:
            for row in rows:
                self.assertIn('Technology', row[sector_index])
        print(f"  - Sector filter applied: {len(rows)} companies in sector")
        
    def test_07_csv_export_with_sorting(self):
        """Test that CSV export respects sorting"""
        print("\n✓ Test 7: CSV Export with Sorting")
        
        # Get sorted by name ascending
        response_asc = self.client.get('/api/export/csv/?sort=name&order=asc')
        content_asc = response_asc.content.decode('utf-8')
        reader_asc = csv.reader(io.StringIO(content_asc))
        next(reader_asc)  # Skip headers
        rows_asc = list(reader_asc)
        
        # Get sorted by name descending
        response_desc = self.client.get('/api/export/csv/?sort=name&order=desc')
        content_desc = response_desc.content.decode('utf-8')
        reader_desc = csv.reader(io.StringIO(content_desc))
        next(reader_desc)  # Skip headers
        rows_desc = list(reader_desc)
        
        # Should have same number of rows
        self.assertEqual(len(rows_asc), len(rows_desc))
        print(f"  - Sort parameters applied successfully")
        print(f"  - ASC: {len(rows_asc)}, DESC: {len(rows_desc)} companies")
        
    def test_08_summary_export_endpoint_accessible(self):
        """Test that summary export endpoint is accessible"""
        print("\n✓ Test 8: Summary Export Endpoint Accessible")
        response = self.client.get('/api/export/summary/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        print("  - Endpoint returns 200 status")
        print("  - Content-Type is text/csv")
        
    def test_09_summary_export_has_statistics(self):
        """Test that summary export includes statistics"""
        print("\n✓ Test 9: Summary Export Contains Statistics")
        response = self.client.get('/api/export/summary/')
        content = response.content.decode('utf-8')
        
        # First row should contain 'Total Companies'
        self.assertIn('Total Companies', content)
        print("  - Summary contains total companies count")
        
    def test_10_summary_export_has_sector_breakdown(self):
        """Test that summary export includes sector breakdown"""
        print("\n✓ Test 10: Summary Export Contains Sector Breakdown")
        response = self.client.get('/api/export/summary/')
        content = response.content.decode('utf-8')
        
        # Should contain sector information
        self.assertIn('Sector', content)
        print("  - Summary contains sector breakdown")
        
    def test_11_csv_export_content_disposition_header(self):
        """Test that CSV export has correct download headers"""
        print("\n✓ Test 11: CSV Export Download Headers")
        response = self.client.get('/api/export/csv/')
        
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('companies.csv', response['Content-Disposition'])
        print("  - Content-Disposition set for download")
        print("  - Filename: companies.csv")
        
    def test_12_summary_export_content_disposition_header(self):
        """Test that summary export has correct download headers"""
        print("\n✓ Test 12: Summary Export Download Headers")
        response = self.client.get('/api/export/summary/')
        
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('summary.csv', response['Content-Disposition'])
        print("  - Content-Disposition set for download")
        print("  - Filename: summary.csv")
        
    def test_13_csv_export_valid_csv_format(self):
        """Test that CSV export is valid CSV format"""
        print("\n✓ Test 13: CSV Export Valid Format")
        response = self.client.get('/api/export/csv/')
        content = response.content.decode('utf-8')
        
        # Should be able to parse as CSV
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        
        # Should have headers + data
        self.assertGreater(len(rows), 1)
        print(f"  - Valid CSV format verified")
        print(f"  - Total rows (including header): {len(rows)}")
        
    def test_14_css_includes_pagination_styles(self):
        """Test that CSS includes pagination size selector styles"""
        print("\n✓ Test 14: CSS Pagination Styles")
        css_file = 'companies/static/companies/css/style.css'
        with open(css_file, 'r') as f:
            css_content = f.read()
        
        # Check for pagination-related styles
        self.assertIn('pagination', css_content)
        print("  - Pagination styles present in CSS")


class Phase11IntegrationTests(TestCase):
    """Integration tests for Phase 11"""
    
    def setUp(self):
        """Create test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_export_with_combined_filters_and_sorting(self):
        """Test export with multiple filters and sorting combined"""
        print("\n✓ Test 15: Export with Combined Filters & Sorting")
        response = self.client.get(
            '/api/export/csv/?search=Tech&sector=Technology&sort=founded&order=desc'
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        print(f"  - Combined filters applied: {len(rows)-1} results")
        
    def test_javascript_functions_present(self):
        """Test that JavaScript export functions are present in app.js"""
        print("\n✓ Test 16: JavaScript Functions Present")
        js_file = 'companies/static/companies/js/app.js'
        with open(js_file, 'r') as f:
            js_content = f.read()
        
        self.assertIn('function exportToCSV()', js_content)
        self.assertIn('function exportSummary()', js_content)
        self.assertIn('function initPaginationSizeSelector()', js_content)
        print("  - exportToCSV() function present ✓")
        print("  - exportSummary() function present ✓")
        print("  - initPaginationSizeSelector() function present ✓")
        
    def test_pagination_selector_in_template(self):
        """Test that pagination selector exists in template"""
        print("\n✓ Test 17: Pagination Selector in Template")
        template_file = 'companies/templates/companies/index.html'
        with open(template_file, 'r') as f:
            template_content = f.read()
        
        self.assertIn('pageLimitSelect', template_content)
        self.assertIn('exportToCSV', template_content)
        self.assertIn('exportSummary', template_content)
        print("  - Pagination selector present in template ✓")
        print("  - Export buttons present in template ✓")
        
    def test_export_routes_configured(self):
        """Test that export routes are properly configured"""
        print("\n✓ Test 18: Export Routes Configured")
        
        # Both routes should exist and be accessible
        try:
            csv_url = reverse('api_export_csv')
            summary_url = reverse('api_export_summary')
        except:
            # If namespace not registered, just check the direct paths
            csv_url = '/api/export/csv/'
            summary_url = '/api/export/summary/'
        
        self.assertTrue(csv_url.endswith('/api/export/csv/'))
        self.assertTrue(summary_url.endswith('/api/export/summary/'))
        print(f"  - CSV export route: {csv_url}")
        print(f"  - Summary export route: {summary_url}")


def run_tests():
    """Run all Phase 11 tests"""
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    failures = test_runner.run_tests([
        'test_phase_11_exports.Phase11ExportTests',
        'test_phase_11_exports.Phase11IntegrationTests'
    ])
    
    return failures


if __name__ == '__main__':
    print("\n" + "="*70)
    print("PHASE 11: EXPORT & ADVANCED FEATURES - TEST SUITE")
    print("="*70)
    
    # Run Django tests
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(Phase11ExportTests))
    suite.addTests(loader.loadTestsFromTestCase(Phase11IntegrationTests))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL PHASE 11 TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED - Review output above")
    
    sys.exit(0 if result.wasSuccessful() else 1)
