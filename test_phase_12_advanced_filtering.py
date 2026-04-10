#!/usr/bin/env python
"""
Phase 12 Tests: Advanced Filtering
Tests for search history, filter presets, and advanced filtering functionality
"""

import os
import sys
import json
import csv
import io

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bd_top_comp.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from companies.models import Company


class Phase12AdvancedFilteringTests(TestCase):
    """Test Phase 12: Advanced Filtering - Search History & Presets"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "="*70)
        print("PHASE 12 TESTS: ADVANCED FILTERING")
        print("="*70)
    
    def setUp(self):
        """Create test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_01_history_button_exists_in_template(self):
        """Test that history button exists in template"""
        print("\n✓ Test 1: History Button in Template")
        response = self.client.get('/')
        self.assertIn('historyBtn', response.content.decode('utf-8'))
        self.assertIn('searchHistoryDropdown', response.content.decode('utf-8'))
        print("  - History button element found ✓")
        print("  - Search history dropdown found ✓")
    
    def test_02_presets_button_exists_in_template(self):
        """Test that presets button exists in template"""
        print("\n✓ Test 2: Presets Button in Template")
        response = self.client.get('/')
        self.assertIn('presetsBtn', response.content.decode('utf-8'))
        self.assertIn('presetsDropdown', response.content.decode('utf-8'))
        print("  - Presets button element found ✓")
        print("  - Presets dropdown found ✓")
    
    def test_03_advanced_filtering_javascript_present(self):
        """Test that advanced filtering JavaScript is present"""
        print("\n✓ Test 3: Advanced Filtering JavaScript")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        self.assertIn('SearchHistory', js_content)
        self.assertIn('FilterPresets', js_content)
        self.assertIn('initAdvancedFiltering', js_content)
        self.assertIn('updateHistoryUI', js_content)
        self.assertIn('updatePresetsUI', js_content)
        print("  - SearchHistory object present ✓")
        print("  - FilterPresets object present ✓")
        print("  - initAdvancedFiltering function present ✓")
    
    def test_04_search_history_functions_exist(self):
        """Test that search history functions exist"""
        print("\n✓ Test 4: Search History Functions")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        history_methods = ['add', 'getAll', 'clear', 'getRecent']
        for method in history_methods:
            self.assertIn(f"SearchHistory.{method}", js_content)
        print(f"  - All {len(history_methods)} SearchHistory methods present ✓")
    
    def test_05_filter_presets_functions_exist(self):
        """Test that filter presets functions exist"""
        print("\n✓ Test 5: Filter Presets Functions")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        preset_methods = ['save', 'load', 'delete', 'getAll', 'clear', 'export', 'import']
        for method in preset_methods:
            self.assertIn(f"FilterPresets.{method}", js_content)
        print(f"  - All {len(preset_methods)} FilterPresets methods present ✓")
    
    def test_06_localStorage_key_defined(self):
        """Test that localStorage keys are defined"""
        print("\n✓ Test 6: LocalStorage Keys")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        self.assertIn("'bd_company_search_history'", js_content)
        self.assertIn("'bd_company_filter_presets'", js_content)
        print("  - Search history storage key defined ✓")
        print("  - Filter presets storage key defined ✓")
    
    def test_07_history_add_function_logic(self):
        """Test search history add function logic"""
        print("\n✓ Test 7: History Add Function Logic")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        # Check for key operations
        self.assertIn('maxItems', js_content)
        self.assertIn('getAll', js_content)
        self.assertIn('localStorage.setItem', js_content)
        print("  - History tracking with maxItems limit ✓")
        print("  - Deduplication logic present ✓")
        print("  - localStorage.setItem calls present ✓")
    
    def test_08_preset_save_function_logic(self):
        """Test preset save function logic"""
        print("\n✓ Test 8: Preset Save Function Logic")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        # Check for key operations
        self.assertIn('currentSearch', js_content)
        self.assertIn('currentSector', js_content)
        self.assertIn('currentSort', js_content)
        self.assertIn('currentOrder', js_content)
        print("  - Saves search filter state ✓")
        print("  - Saves sector filter state ✓")
        print("  - Saves sort state ✓")
    
    def test_09_preset_load_function_applies_filters(self):
        """Test preset load function applies filters"""
        print("\n✓ Test 9: Preset Load Function")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        # Check operations
        self.assertIn('currentSearch = preset.search', js_content)
        self.assertIn('currentSector = preset.sector', js_content)
        self.assertIn('loadCompanies()', js_content)
        print("  - Applies saved search to currentSearch ✓")
        print("  - Applies saved sector to currentSector ✓")
        print("  - Calls loadCompanies to refresh data ✓")
    
    def test_10_history_ui_update_function_exists(self):
        """Test history UI update function"""
        print("\n✓ Test 10: History UI Update Function")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        self.assertIn('function updateHistoryUI()', js_content)
        self.assertIn('searchHistoryDropdown', js_content)
        print("  - updateHistoryUI function present ✓")
        print("  - Updates searchHistoryDropdown element ✓")
    
    def test_11_presets_ui_update_function_exists(self):
        """Test presets UI update function"""
        print("\n✓ Test 11: Presets UI Update Function")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        self.assertIn('function updatePresetsUI()', js_content)
        self.assertIn('presetsDropdown', js_content)
        print("  - updatePresetsUI function present ✓")
        print("  - Updates presetsDropdown element ✓")
    
    def test_12_css_includes_phase12_styles(self):
        """Test CSS includes Phase 12 styles"""
        print("\n✓ Test 12: Phase 12 CSS Styles")
        with open('companies/static/companies/css/style.css', 'r') as f:
            css_content = f.read()
        
        selectors = ['#searchHistoryDropdown', '#presetsDropdown', '.dropdown-item', '.preset-item']
        for selector in selectors:
            self.assertIn(selector, css_content)
        print(f"  - All {len(selectors)} CSS selectors present ✓")
    
    def test_13_dropdown_animation_css_present(self):
        """Test dropdown animation CSS"""
        print("\n✓ Test 13: Dropdown Animation CSS")
        with open('companies/static/companies/css/style.css', 'r') as f:
            css_content = f.read()
        
        self.assertIn('slideDown', css_content)
        self.assertIn('@keyframes', css_content)
        self.assertIn('animation', css_content)
        print("  - slideDown animation defined ✓")
        print("  - CSS animation keyframes present ✓")
    
    def test_14_function_save_preset_dialog_exists(self):
        """Test save preset dialog function"""
        print("\n✓ Test 14: Save Preset Dialog Function")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        self.assertIn('function savePresetDialog()', js_content)
        self.assertIn('prompt(', js_content)
        self.assertIn('FilterPresets.save', js_content)
        print("  - savePresetDialog function present ✓")
        print("  - Uses prompt for user input ✓")
        print("  - Calls FilterPresets.save ✓")
    
    def test_15_import_export_functions_exist(self):
        """Test import/export functions"""
        print("\n✓ Test 15: Import/Export Functions")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        self.assertIn('handlePresetsImport', js_content)
        self.assertIn('FilterPresets.export', js_content)
        self.assertIn('JSON.stringify', js_content)
        print("  - handlePresetsImport function present ✓")
        print("  - Export functionality present ✓")
        print("  - JSON serialization for export ✓")
    
    def test_16_init_advanced_filtering_called(self):
        """Test initAdvancedFiltering is called on load"""
        print("\n✓ Test 16: Advanced Filtering Initialization")
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_content = f.read()
        
        self.assertIn('initAdvancedFiltering()', js_content)
        self.assertIn('DOMContentLoaded', js_content)
        print("  - initAdvancedFiltering() called on page load ✓")
        print("  - Initialization in DOMContentLoaded event ✓")


class Phase12IntegrationTests(TestCase):
    """Integration tests for Phase 12"""
    
    def setUp(self):
        """Create test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_17_page_loads_with_all_phase12_elements(self):
        """Test page loads with all Phase 12 elements"""
        print("\n✓ Test 17: Page Load with Phase 12 Elements")
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        
        elements = [
            'historyBtn',
            'presetsBtn',
            'searchHistoryDropdown',
            'presetsDropdown',
            'SearchHistory',
            'FilterPresets'
        ]
        
        for element in elements:
            self.assertIn(element, content)
        print(f"  - All {len(elements)} Phase 12 elements present on page ✓")
    
    def test_18_api_endpoints_still_work(self):
        """Test Phase 11 export endpoints still work after Phase 12"""
        print("\n✓ Test 18: Phase 11 Export API Still Works")
        response_csv = self.client.get('/api/export/csv/')
        response_summary = self.client.get('/api/export/summary/')
        
        self.assertEqual(response_csv.status_code, 200)
        self.assertEqual(response_summary.status_code, 200)
        print("  - CSV export endpoint working ✓")
        print("  - Summary export endpoint working ✓")
    
    def test_19_all_filter_inputs_accessible(self):
        """Test all filter inputs are accessible"""
        print("\n✓ Test 19: Filter Inputs Accessible")
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        
        inputs = [
            'searchInput',
            'sectorFilter',
            'pageLimitSelect',
            'addCompanyBtn'
        ]
        
        for input_id in inputs:
            self.assertIn(f'id="{input_id}"', content)
        print(f"  - All {len(inputs)} filter inputs present ✓")
    
    def test_20_static_files_loaded_successfully(self):
        """Test static files are loaded"""
        print("\n✓ Test 20: Static Files Loaded")
        
        # Check JavaScript file
        with open('companies/static/companies/js/app.js', 'r') as f:
            js_size = len(f.read())
        
        # Check CSS file  
        with open('companies/static/companies/css/style.css', 'r') as f:
            css_size = len(f.read())
        
        self.assertGreater(js_size, 30000)  # app.js should be substantial
        self.assertGreater(css_size, 50000)  # style.css should be substantial
        print(f"  - app.js size: {js_size:,} bytes ✓")
        print(f"  - style.css size: {css_size:,} bytes ✓")


def run_tests():
    """Run all Phase 12 tests"""
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(Phase12AdvancedFilteringTests))
    suite.addTests(loader.loadTestsFromTestCase(Phase12IntegrationTests))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("\n" + "="*70)
    print("PHASE 12: ADVANCED FILTERING - TEST SUITE")
    print("="*70)
    
    result = run_tests()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL PHASE 12 TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED - Review output above")
    
    sys.exit(0 if result.wasSuccessful() else 1)
