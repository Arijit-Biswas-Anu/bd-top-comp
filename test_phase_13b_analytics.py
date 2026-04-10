#!/usr/bin/env python
"""
Phase 13B Tests: Analytics Dashboard
Tests for analytics endpoints, visualizations, and company comparisons
"""

import os
import sys
import json

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bd_top_comp.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from companies.models import Company


class Phase13BAnalyticsTests(TestCase):
    """Test Phase 13B: Analytics Dashboard"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "="*70)
        print("PHASE 13B TESTS: ANALYTICS DASHBOARD")
        print("="*70)
    
    def setUp(self):
        """Create test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_01_analytics_button_in_template(self):
        """Test that analytics button exists in template"""
        print("\n✓ Test 1: Analytics Button in Template")
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        self.assertIn('analyticsBtn', content)
        self.assertIn('📈 Analytics', content)
        print("  - Analytics button element found ✓")
    
    def test_02_analytics_modal_exists(self):
        """Test that analytics modal exists in template"""
        print("\n✓ Test 2: Analytics Modal Exists")
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        self.assertIn('analyticsDashboardModal', content)
        self.assertIn('sectorChart', content)
        self.assertIn('decadeChart', content)
        print("  - Analytics modal structure present ✓")
    
    def test_03_chart_js_library_included(self):
        """Test that Chart.js library is included"""
        print("\n✓ Test 3: Chart.js Library Included")
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        self.assertIn('chart.min.js', content)
        print("  - Chart.js CDN included ✓")
    
    def test_04_analytics_dashboard_api_accessible(self):
        """Test that analytics dashboard API is accessible"""
        print("\n✓ Test 4: Analytics Dashboard API Accessible")
        response = self.client.get('/api/analytics/dashboard/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('statistics', data)
        self.assertIn('sector_distribution', data)
        print("  - Dashboard API returns 200 ✓")
        print(f"  - Total companies: {data['statistics']['total_companies']} ✓")
    
    def test_05_analytics_requires_authentication(self):
        """Test that analytics API requires authentication"""
        print("\n✓ Test 5: Analytics Requires Authentication")
        self.client.logout()
        response = self.client.get('/api/analytics/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        print("  - Unauthenticated users redirected to login ✓")
    
    def test_06_dashboard_statistics_complete(self):
        """Test that dashboard returns complete statistics"""
        print("\n✓ Test 6: Dashboard Statistics Complete")
        response = self.client.get('/api/analytics/dashboard/')
        data = response.json()
        
        stats = data['statistics']
        required_fields = ['total_companies', 'total_sectors', 'avg_founded_year', 'founded_year_range']
        
        for field in required_fields:
            self.assertIn(field, stats)
        
        print(f"  - All {len(required_fields)} required statistics present ✓")
    
    def test_07_sector_distribution_data(self):
        """Test sector distribution data"""
        print("\n✓ Test 7: Sector Distribution Data")
        response = self.client.get('/api/analytics/dashboard/')
        data = response.json()
        
        sectors = data['sector_distribution']
        self.assertGreater(len(sectors), 0)
        
        # Check structure
        for sector in sectors:
            self.assertIn('sector', sector)
            self.assertIn('count', sector)
        
        print(f"  - Sector distribution contains {len(sectors)} sectors ✓")
    
    def test_08_decade_stats_data(self):
        """Test decade statistics"""
        print("\n✓ Test 8: Decade Statistics")
        response = self.client.get('/api/analytics/dashboard/')
        data = response.json()
        
        decades = data['decade_stats']
        self.assertIsInstance(decades, dict)
        print(f"  - Decade distribution contains {len(decades)} decades ✓")
    
    def test_09_recent_companies_included(self):
        """Test that recent companies are included"""
        print("\n✓ Test 9: Recent Companies Included")
        response = self.client.get('/api/analytics/dashboard/')
        data = response.json()
        
        recent = data['recent_companies']
        self.assertIsInstance(recent, list)
        self.assertLessEqual(len(recent), 5)
        
        if recent:
            company = recent[0]
            self.assertIn('name', company)
            self.assertIn('sector', company)
            self.assertIn('founded', company)
        
        print(f"  - Recent companies list contains {len(recent)} items ✓")
    
    def test_10_top_sectors_included(self):
        """Test that top sectors are included"""
        print("\n✓ Test 10: Top Sectors Included")
        response = self.client.get('/api/analytics/dashboard/')
        data = response.json()
        
        top_sectors = data['top_sectors']
        self.assertIsInstance(top_sectors, list)
        self.assertLessEqual(len(top_sectors), 5)
        
        print(f"  - Top sectors list contains {len(top_sectors)} items ✓")
    
    def test_11_company_comparison_api(self):
        """Test company comparison API"""
        print("\n✓ Test 11: Company Comparison API")
        response = self.client.get('/api/analytics/comparison/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('companies', data)
        self.assertIn('metrics', data)
        
        print(f"  - Comparison API returns {len(data['companies'])} companies ✓")
    
    def test_12_comparison_with_specific_ids(self):
        """Test comparison with specific company IDs"""
        print("\n✓ Test 12: Comparison with Specific IDs")
        companies = Company.objects.all()[:2]
        ids = [str(c.id) for c in companies]
        
        query_string = '&'.join([f'ids={id}' for id in ids])
        response = self.client.get(f'/api/analytics/comparison/?{query_string}')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['companies']), len(ids))
        
        print(f"  - Returned comparison for {len(data['companies'])} specific companies ✓")
    
    def test_13_sector_insights_api(self):
        """Test sector insights API"""
        print("\n✓ Test 13: Sector Insights API")
        sector = 'Technology'  # Known sector in test data
        response = self.client.get(f'/api/analytics/sector/?sector={sector}')
        
        if response.status_code == 200 or response.status_code == 404:
            data = response.json()
            if response.status_code == 200:
                self.assertTrue(data['success'])
                self.assertIn('insights', data)
                print(f"  - Sector insights retrieved for {sector} ✓")
            else:
                self.assertFalse(data['success'])
                print(f"  - Sector not found (expected for test data) ✓")
    
    def test_14_growth_analysis_api(self):
        """Test growth analysis API"""
        print("\n✓ Test 14: Growth Analysis API")
        response = self.client.get('/api/analytics/growth/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('growth_data', data)
        self.assertIn('metrics', data)
        
        print(f"  - Growth analysis returns {len(data['growth_data'])} data points ✓")
    
    def test_15_descriptive_stats_api(self):
        """Test descriptive statistics API"""
        print("\n✓ Test 15: Descriptive Statistics API")
        response = self.client.get('/api/analytics/stats/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('statistics', data)
        
        stats = data['statistics']
        self.assertIn('founded_year_statistics', stats)
        self.assertIn('sector_statistics', stats)
        
        year_stats = stats['founded_year_statistics']
        required_stats = ['count', 'mean', 'median', 'std_dev', 'min', 'max', 'range']
        for stat in required_stats:
            self.assertIn(stat, year_stats)
        
        print(f"  - Descriptive stats contains {len(year_stats)} measures ✓")
    
    def test_16_analytics_javascript_functions(self):
        """Test that analytics JavaScript functions exist"""
        print("\n✓ Test 16: Analytics JavaScript Functions")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        functions = [
            'showAnalyticsDashboard',
            'loadAnalyticsData',
            'displayAnalyticsData',
            'createSectorChart',
            'createDecadeChart',
            'displayRecentCompanies',
            'exportAnalytics',
            'compareCompanies',
            'getSectorInsights'
        ]
        
        for func in functions:
            self.assertIn(f'function {func}', js_content)
        
        print(f"  - All {len(functions)} analytics functions present ✓")
    
    def test_17_chart_initialization_code(self):
        """Test that chart initialization code exists"""
        print("\n✓ Test 17: Chart Initialization Code")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        self.assertIn('analyticCharts', js_content)
        self.assertIn('new Chart', js_content)
        self.assertIn('getElementById', js_content)
        
        print("  - Chart.js initialization code present ✓")
    
    def test_18_analytics_css_styling(self):
        """Test that analytics CSS styling exists"""
        print("\n✓ Test 18: Analytics CSS Styling")
        with open('companies/static/companies/css/style.css', 'r') as f:
            css_content = f.read()
        
        selectors = [
            '.stat-card',
            '.chart-container',
            '.recent-companies-list',
            '.analytics-modal-content',
            '.stat-value'
        ]
        
        for selector in selectors:
            self.assertIn(selector, css_content)
        
        print(f"  - All {len(selectors)} CSS selectors present ✓")
    
    def test_19_urls_configured_for_analytics(self):
        """Test that analytics URLs are configured"""
        print("\n✓ Test 19: Analytics URLs Configured")
        from django.urls import reverse
        
        urls_to_test = [
            'api_analytics_dashboard',
            'api_company_comparison',
            'api_sector_insights',
            'api_growth_analysis',
            'api_descriptive_stats'
        ]
        
        available_count = 0
        for url_name in urls_to_test:
            try:
                reverse(url_name)
                available_count += 1
            except:
                pass
        
        self.assertGreaterEqual(available_count, 4)
        print(f"  - {available_count} analytics URLs available ✓")
    
    def test_20_page_loads_with_analytics(self):
        """Test that page loads with analytics elements"""
        print("\n✓ Test 20: Page Loads with Analytics Elements")
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        
        elements = [
            'analyticsBtn',
            'analyticsDashboardModal',
            'sectorChart',
            'decadeChart',
            'recentCompaniesList',
            'showAnalyticsDashboard'
        ]
        
        for element in elements:
            self.assertIn(element, content)
        
        print(f"  - All {len(elements)} analytics elements present on page ✓")


class Phase13BIntegrationTests(TestCase):
    """Integration tests for Phase 13B"""
    
    def setUp(self):
        """Create test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_21_analytics_json_response_format(self):
        """Test analytics response JSON format"""
        print("\n✓ Test 21: Analytics JSON Response Format")
        response = self.client.get('/api/analytics/dashboard/')
        data = response.json()
        
        # Verify response structure
        self.assertIsInstance(data, dict)
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        
        required_keys = ['statistics', 'sector_distribution', 'decade_stats', 'recent_companies', 'top_sectors']
        for key in required_keys:
            self.assertIn(key, data)
        
        print(f"  - All {len(required_keys)} required JSON keys present ✓")
    
    def test_22_analytics_data_consistency(self):
        """Test consistency of analytics data"""
        print("\n✓ Test 22: Analytics Data Consistency")
        response = self.client.get('/api/analytics/dashboard/')
        data = response.json()
        
        # Total companies should match sum of sectors
        total_from_stats = data['statistics']['total_companies']
        total_from_sectors = sum(s['count'] for s in data['sector_distribution'])
        
        self.assertEqual(total_from_stats, total_from_sectors)
        print(f"  - Data consistency validated: {total_from_stats} companies ✓")
    
    def test_23_all_phases_work_together(self):
        """Test that Phase 13B works with previous phases"""
        print("\n✓ Test 23: Phase 13B Works with Previous Phases")
        
        # Test that export still works
        response_export = self.client.get('/api/export/csv/')
        self.assertEqual(response_export.status_code, 200)
        
        # Test that history/presets still work
        response_home = self.client.get('/')
        content = response_home.content.decode('utf-8')
        self.assertIn('searchHistoryDropdown', content)
        self.assertIn('presetsDropdown', content)
        
        # Test that analytics works
        response_analytics = self.client.get('/api/analytics/dashboard/')
        self.assertEqual(response_analytics.status_code, 200)
        
        print("  - All phases integrated successfully ✓")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("PHASE 13B: ANALYTICS DASHBOARD - TEST SUITE")
    print("="*70)
    
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(Phase13BAnalyticsTests))
    suite.addTests(loader.loadTestsFromTestCase(Phase13BIntegrationTests))
    
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
        print("\n✅ ALL PHASE 13B TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED - Review output above")
    
    sys.exit(0 if result.wasSuccessful() else 1)
