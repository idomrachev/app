import requests
import sys
from datetime import datetime

class DjangoDamageAppTester:
    def __init__(self, base_url="https://auto-damage-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, data=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.status_code == 403:
                    print("   CSRF token issue detected")
                print(f"   Response: {response.text[:200]}")

            return success, response

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_phone_input_page_load(self):
        """Test phone input page loads correctly"""
        success, response = self.run_test(
            "Phone Input Page Load",
            "GET",
            "/",
            200
        )
        if success:
            # Check for key elements in HTML
            html = response.text
            if 'data-testid="phone-form"' in html:
                print("   ✅ Phone form found in HTML")
            if 'data-testid="phone-input"' in html:
                print("   ✅ Phone input field found in HTML")
            if 'ОЦЕНКАPRO' in html:
                print("   ✅ App title found in HTML")
        return success

    def test_contacts_page_load(self):
        """Test contacts page loads correctly"""
        success, response = self.run_test(
            "Contacts Page Load",
            "GET",
            "/contacts/",
            200
        )
        if success:
            html = response.text
            if '+7 (495) 123-45-67' in html:
                print("   ✅ Phone number found in HTML")
            if 'Автомобильная' in html:
                print("   ✅ Address found in HTML")
            if 'data-testid="contacts-title"' in html:
                print("   ✅ Contacts title found in HTML")
        return success

    def test_csrf_token_retrieval(self):
        """Test if we can get CSRF token from phone page"""
        success, response = self.run_test(
            "CSRF Token Retrieval",
            "GET",
            "/",
            200
        )
        if success:
            html = response.text
            if 'csrfmiddlewaretoken' in html:
                print("   ✅ CSRF token found in form")
                # Extract CSRF token
                import re
                csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"   ✅ CSRF token extracted: {csrf_token[:10]}...")
                    return csrf_token
            else:
                print("   ❌ CSRF token NOT found in form")
        return None

    def test_phone_submission_with_csrf(self, csrf_token):
        """Test phone submission with CSRF token"""
        if not csrf_token:
            print("❌ Cannot test phone submission without CSRF token")
            return False
            
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'phone': '+7 (999) 123-45-67'
        }
        
        success, response = self.run_test(
            "Phone Submission with CSRF",
            "POST",
            "/",
            302  # Should redirect to verify page
        )
        return success

def main():
    print("🚀 Starting Django Damage App Backend Testing\n")
    
    # Setup
    tester = DjangoDamageAppTester()
    
    # Test page loads
    print("=== TESTING PAGE LOADS ===")
    tester.test_phone_input_page_load()
    tester.test_contacts_page_load()
    
    # Test CSRF functionality
    print("\n=== TESTING CSRF FUNCTIONALITY ===")
    csrf_token = tester.test_csrf_token_retrieval()
    if csrf_token:
        tester.test_phone_submission_with_csrf(csrf_token)
    
    # Test protected pages (should redirect)
    print("\n=== TESTING PROTECTED PAGES ===")
    tester.run_test(
        "Verify Page (should redirect)",
        "GET",
        "/verify/",
        302  # Should redirect to phone input
    )
    
    tester.run_test(
        "Damage Form Page (should redirect)",
        "GET", 
        "/damage-form/",
        302  # Should redirect to phone input
    )
    
    tester.run_test(
        "Calculations Page (should redirect)",
        "GET",
        "/calculations/",
        302  # Should redirect to phone input
    )

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed - see details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())