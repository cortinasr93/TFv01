# test_metering.py

import pytest
import requests
import time
import redis
from core.config import get_settings
from typing import Optional

settings = get_settings()

class TestMetering:
    """Test suite for token metering functionality"""
    
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(cls):
        """Setup fixture that runs before tests"""
        cls.base_url = "http://localhost:8000"
        cls.session = requests.Session()
        cls.company_id: Optional[str] = None
        cls.publisher_id: Optional[str] = None
        cls.access_token: Optional[str] = None
        cls.ai_company_email = None
        cls.ai_company_password = "testpassword123"
        cls.session_id = None
        
        # Clear Redis cache
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Clear IP reputation data
        for key in redis_client.scan_iter("ip_reputation:*"):
            redis_client.delete(key)
        
        # Do the setup
        print("\nSetting up test environment...")
        cls.register_and_setup()
        
        # Provide the fixture
        yield
        
        # Cleanup
        cls.session.close()
        print("\nTest cleanup completed")

    def register_and_setup(self):
        """Complete setup flow for testing"""
        try:
            print("1. Registering AI Company...")
            company_data = self.register_ai_company()
            self.company_id = company_data['company_id']
            self.access_token = company_data['access_token']  # Get token from registration
            if 'session_id' in company_data:
                self.session_id = company_data['session_id']
                self.session.cookies.set('session_id', self.session_id)
            print(f"✓ AI Company registered with ID: {self.company_id}")
            print(f"✓ Access token received: {self.access_token[:10]}...")

            print("\n2. Logging in as AI Company...")
            login_data = self.login_ai_company()
            if 'session_id' in login_data:
                self.session_id = login_data['session_id']
                self.session.cookies.set('session_id', self.session_id)
            print("✓ Successfully logged in as AI Company")

        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            raise

    def register_ai_company(self):
        """Register a test AI company"""
        url = f"{self.base_url}/api/onboarding/ai-company"
        self.ai_company_email = f"test_{int(time.time())}@testai.com"
        data = {
            "company_name": "Test AI Corp",
            "email": self.ai_company_email,
            "password": self.ai_company_password,
            "website": "https://testai.com"
        }
        print(f"Sending registration request to: {url}")
        print(f"Registration data: {data}")
        response = self.session.post(url, json=data)
        print(f"Registration response status: {response.status_code}")
        print(f"Registration response: {response.text}")
        assert response.status_code == 200, f"AI Company registration failed: {response.text}"
        return response.json()

    def login_ai_company(self):
        """Login as AI company"""
        url = f"{self.base_url}/api/auth/login"
        data = {
            "email": self.ai_company_email,
            "password": self.ai_company_password,
            "user_type": "ai-company"
        }
        response = self.session.post(url, json=data)
        assert response.status_code == 200, f"AI Company login failed: {response.text}"
        
        # Print response headers and cookies for debugging
        print("Login Response Headers:", dict(response.headers))
        print("Login Response Cookies:", dict(response.cookies))
        return response.json()

    def register_publisher(self):
        """Helper to register a test publisher"""
        url = f"{self.base_url}/api/onboarding/publisher"
        data = {
            "name": "Test Publisher",
            "email": f"test_publisher_{int(time.time())}@test.com",
            "password": "testpassword123",
            "website": "https://testpublisher.com",
            "content_type": "news"
        }
        response = self.session.post(url, json=data)
        assert response.status_code == 200
        return response.json()
    
    def test_token_validation(self):
        """Test that created token is valid"""
        
        # Register publisher
        publisher_data = self.register_publisher()
        publisher_id = publisher_data['publisher_id']
        
        # Add token to publisher's whitelist
        add_url = f"{self.base_url}/api/access-tokens/publisher/{publisher_id}/add"
        response = self.session.post(
            add_url,
            json={"token": self.access_token}
        )
        assert response.status_code == 200
        
        # Validate tokoen        
        url = f"{self.base_url}/api/access-tokens/validate"
        response = self.session.post(
            f"{url}?publisher_id=test-publisher&token={self.access_token}"
        )
        assert response.status_code == 200, f"Token validation failed: {response.text}"
        result = response.json()
        assert result.get('valid') is True, "Token should be valid"
        print("\nToken validated successfully")

    def test_bot_detection(self):
        """Test bot detection with various user agents"""
        test_cases = [
            {
                "user_agent": "anthropic-ai/claude",
                "expected_bot": True,
                "headers": {"User-Agent": "anthropic-ai/claude"}
            },
            {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "expected_bot": False,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1"
                }
            },
            {
                "user_agent": "gptbot/1.0",
                "expected_bot": True,
                "headers": {"User-Agent": "gptbot/1.0"}
            }
        ]

        for test_case in test_cases:
            print(f"\nTesting user agent: {test_case['user_agent']}")
            url = f"{self.base_url}/api/detection"
            
            response = self.session.post(
                url,
                headers=test_case["headers"],
                json={"publisher_id": "test-publisher"}
            )
            assert response.status_code == 200, f"Bot detection request failed: {response.text}"
            
            result = response.json()
            print(f"Detection result: {result}")
            assert 'results' in result, "Response should contain detection results"
            assert 'is_bot' in result['results'], "Results should include bot status"
            
            assert result['results']['is_bot'] == test_case['expected_bot'], \
                f"Bot detection for {test_case['user_agent']} did not match expected result"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])