
import requests
import sys
import json
from datetime import datetime

class RelocateMeAPITester:
    def __init__(self, base_url="https://2cdbcfb0-eea9-4326-9b19-b06d91ee205b.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        print(f"🚀 Testing RelocateMe API at: {self.base_url}")
        print("=" * 50)

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            result = {
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    result["response"] = response.json()
                except:
                    result["response"] = "No JSON response"
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    result["error"] = response.json()
                except:
                    result["error"] = response.text

            self.test_results.append(result)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "success": False,
                "error": str(e)
            })
            return False, {}

    def test_login(self, username, password):
        """Test login and get token"""
        print(f"\n🔐 Attempting login with username: {username}")
        success, response = self.run_test(
            "Login",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"✅ Login successful, token received")
            return True
        print(f"❌ Login failed")
        return False

    def test_auth_me(self):
        """Test getting current user info"""
        return self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )

    def test_timeline_full(self):
        """Test getting full timeline"""
        return self.run_test(
            "Get Full Timeline",
            "GET",
            "timeline/full",
            200
        )

    def test_timeline_by_category(self):
        """Test getting timeline by category"""
        return self.run_test(
            "Get Timeline By Category",
            "GET",
            "timeline/by-category",
            200
        )

    def test_update_timeline_progress(self, step_id, completed):
        """Test updating timeline progress"""
        return self.run_test(
            "Update Timeline Progress",
            "POST",
            "timeline/update-progress",
            200,
            data={"step_id": step_id, "completed": completed}
        )

    def test_jobs_listings(self):
        """Test getting job listings"""
        return self.run_test(
            "Get Job Listings",
            "GET",
            "jobs/listings",
            200
        )

    def test_jobs_featured(self):
        """Test getting featured jobs"""
        return self.run_test(
            "Get Featured Jobs",
            "GET",
            "jobs/featured",
            200
        )

    def test_jobs_categories(self):
        """Test getting job categories"""
        return self.run_test(
            "Get Job Categories",
            "GET",
            "jobs/categories",
            200
        )

    def test_visa_requirements(self):
        """Test getting visa requirements"""
        return self.run_test(
            "Get Visa Requirements",
            "GET",
            "visa/requirements",
            200
        )

    def test_visa_checklist(self):
        """Test getting visa checklist"""
        return self.run_test(
            "Get Visa Checklist",
            "GET",
            "visa/checklist",
            200
        )
        
    def test_visa_requirement_details(self, visa_type):
        """Test getting visa requirement details"""
        return self.run_test(
            "Get Visa Requirement Details",
            "GET",
            f"visa/requirements/{visa_type}",
            200
        )

    def test_resources_all(self):
        """Test getting all resources"""
        return self.run_test(
            "Get All Resources",
            "GET",
            "resources/all",
            200
        )

    def test_logistics_providers(self):
        """Test getting logistics providers"""
        return self.run_test(
            "Get Logistics Providers",
            "GET",
            "logistics/providers",
            200
        )

    def test_dashboard_overview(self):
        """Test getting dashboard overview"""
        return self.run_test(
            "Get Dashboard Overview",
            "GET",
            "dashboard/overview",
            200
        )

    def test_password_reset_request(self, username):
        """Test requesting a password reset"""
        return self.run_test(
            "Request Password Reset",
            "POST",
            "auth/reset-password",
            200,
            data={"username": username}
        )
        
    def test_analytics_budget(self):
        """Test getting budget analytics"""
        return self.run_test(
            "Get Budget Analytics",
            "GET",
            "analytics/budget",
            200
        )

    def test_analytics_overview(self):
        """Test getting analytics overview"""
        return self.run_test(
            "Get Analytics Overview",
            "GET",
            "analytics/overview",
            200
        )

    def test_progress_items(self):
        """Test getting progress items"""
        return self.run_test(
            "Get Progress Items",
            "GET",
            "progress/items",
            200
        )

    def test_complete_password_reset(self, username, reset_code, new_password):
        """Test completing a password reset"""
        return self.run_test(
            "Complete Password Reset",
            "POST",
            "auth/complete-password-reset",
            200,
            data={
                "username": username,
                "reset_code": reset_code,
                "new_password": new_password
            }
        )
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print(f"📊 TEST SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        print("="*50)
        
        if self.tests_passed < self.tests_run:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"- {result['name']} ({result['method']} {result['endpoint']})")
                    print(f"  Expected: {result['expected_status']}, Got: {result.get('actual_status', 'Error')}")
                    if "error" in result:
                        print(f"  Error: {result['error']}")
                    print()
        
        return self.tests_passed == self.tests_run

def main():
    # Setup
    tester = RelocateMeAPITester()
    
    # Test login with default credentials
    if not tester.test_login("relocate_user", "SecurePass2025!"):
        print("❌ Login failed, stopping tests")
        return 1

    # Test authenticated endpoints
    tester.test_auth_me()
    tester.test_timeline_full()
    tester.test_timeline_by_category()
    
    # Test job-related endpoints
    tester.test_jobs_listings()
    tester.test_jobs_featured()
    tester.test_jobs_categories()
    
    # Test visa-related endpoints
    tester.test_visa_requirements()
    tester.test_visa_checklist()
    
    # Test resources
    tester.test_resources_all()
    
    # Test logistics
    tester.test_logistics_providers()
    
    # Test dashboard and analytics
    tester.test_dashboard_overview()
    tester.test_analytics_budget()
    tester.test_analytics_overview()
    
    # Test progress items
    tester.test_progress_items()
    
    # Try updating timeline progress
    success, timeline_data = tester.test_timeline_full()
    if success and timeline_data and "timeline" in timeline_data:
        # Find a step that's not completed
        for step in timeline_data["timeline"]:
            if not step.get("is_completed", False):
                tester.test_update_timeline_progress(step["id"], True)
                break
    
    # Test password reset functionality
    success, reset_response = tester.test_password_reset_request("relocate_user")
    if success and reset_response and "reset_code" in reset_response:
        reset_code = reset_response["reset_code"]
        # Test complete password reset with a temporary password
        tester.test_complete_password_reset("relocate_user", reset_code, "SecurePass2025!")
        # Log back in with the same password (since we're resetting to the same password)
        tester.test_login("relocate_user", "SecurePass2025!")
    
    # Test visa requirement details
    success, visa_data = tester.test_visa_requirements()
    if success and visa_data and "visa_types" in visa_data and len(visa_data["visa_types"]) > 0:
        visa_type = visa_data["visa_types"][0]["visa_type"].lower().replace(" ", "-")
        tester.test_visa_requirement_details(visa_type)
    
    # Print summary
    success = tester.print_summary()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
