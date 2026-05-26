#!/usr/bin/env python3
"""
Comprehensive system validation - tests all major features and workflows
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "http://localhost:8088"
FRONTEND_URL = "http://localhost:3000"

class SystemValidator:
    def __init__(self):
        self.backend_available = False
        self.frontend_available = False
        self.issues = []
        self.successes = []

    def test_backend_health(self):
        """Test if backend is responding"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                self.successes.append("✓ Backend health check passed")
                self.backend_available = True
                return True
            else:
                self.issues.append(f"✗ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.issues.append(f"✗ Backend health check error: {str(e)}")
            return False

    def test_frontend_access(self):
        """Test if frontend is accessible"""
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                self.successes.append("✓ Frontend is accessible")
                self.frontend_available = True
                return True
            else:
                self.issues.append(f"✗ Frontend access failed: {response.status_code}")
                return False
        except Exception as e:
            self.issues.append(f"✗ Frontend access error: {str(e)}")
            return False

    def test_api_endpoints(self):
        """Test core API endpoints"""
        endpoints = [
            ("/api/system/status", "GET"),
            ("/api/knowledge_base/documents", "GET"),
            ("/api/publishing/queue", "GET"),
        ]
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{BACKEND_URL}{endpoint}", timeout=5)
                
                if response.status_code < 400:
                    self.successes.append(f"✓ Endpoint {endpoint} responding")
                else:
                    self.issues.append(f"✗ Endpoint {endpoint} returned {response.status_code}")
            except Exception as e:
                self.issues.append(f"✗ Endpoint {endpoint} error: {str(e)}")

    def test_main_workflow(self):
        """Test the main strategy generation workflow"""
        try:
            # Create a minimal state with required fields
            payload = {
                "state": {
                    "brand_profile": {
                        "brand_name": "Test Brand",
                        "industry": "Technology",
                        "product_category": "SaaS",
                        "voice_keywords": ["innovative", "helpful"],
                        "brand_type": "B2B"
                    },
                    "target_persona": {
                        "age_group": "25-45",
                        "interests": ["tech", "productivity"],
                        "pain_points": ["time management"]
                    },
                    "active_platforms": ["Instagram", "LinkedIn", "Twitter"],
                    "conversation_history": [],
                    "content_pillars": [],
                    "monthly_calendar": [],
                    "platform_strategies": {},
                    "engagement_plan": None,
                    "ugc_campaign": None,
                    "influencer_plan": None,
                    "loyalty_strategy": None,
                    "suggestions_list": [],
                    "posting_frequency": {},
                    "structured_context": {}
                }
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/social_manager/run",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                state = data.get("state", {})
                
                # Validate response structure
                checks = {
                    "content_pillars": len(state.get("content_pillars", [])) > 0,
                    "monthly_calendar": len(state.get("monthly_calendar", [])) > 0,
                    "platform_strategies": len(state.get("platform_strategies", {})) > 0,
                    "suggestions_list": len(state.get("suggestions_list", [])) > 0,
                }
                
                if all(checks.values()):
                    self.successes.append("✓ Main workflow test passed - all fields populated")
                    return True
                else:
                    failed = [k for k, v in checks.items() if not v]
                    self.issues.append(f"✗ Main workflow missing: {', '.join(failed)}")
                    return False
            else:
                self.issues.append(f"✗ Main workflow failed: {response.status_code}")
                return False
        except Exception as e:
            self.issues.append(f"✗ Main workflow error: {str(e)}")
            return False

    def test_knowledge_base(self):
        """Test knowledge base endpoints"""
        try:
            # Test document listing
            response = requests.get(
                f"{BACKEND_URL}/api/knowledge_base/documents",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get("documents", [])
                if docs:
                    self.successes.append(f"✓ Knowledge base has {len(docs)} documents")
                    return True
                else:
                    self.successes.append("✓ Knowledge base endpoint working (empty)")
                    return True
            else:
                self.issues.append(f"✗ Knowledge base endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            self.issues.append(f"✗ Knowledge base error: {str(e)}")
            return False

    def test_publishing_queue(self):
        """Test publishing queue"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/publishing/queue",
                timeout=5
            )
            
            if response.status_code == 200:
                self.successes.append("✓ Publishing queue endpoint working")
                return True
            else:
                self.issues.append(f"✗ Publishing queue failed: {response.status_code}")
                return False
        except Exception as e:
            self.issues.append(f"✗ Publishing queue error: {str(e)}")
            return False

    def test_policy_check(self):
        """Test content policy checking"""
        try:
            payload = {"content": "Check this post for policy violations"}
            response = requests.post(
                f"{BACKEND_URL}/api/policy/check",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                self.successes.append("✓ Policy check endpoint working")
                return True
            else:
                self.issues.append(f"✗ Policy check failed: {response.status_code}")
                return False
        except Exception as e:
            self.issues.append(f"✗ Policy check error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all validation tests"""
        print("\n" + "=" * 60)
        print("SOCIAL MANAGER AI - SYSTEM VALIDATION")
        print("=" * 60 + "\n")
        
        print("Testing Backend Connectivity...")
        self.test_backend_health()
        
        print("Testing Frontend Connectivity...")
        self.test_frontend_access()
        
        print("Testing API Endpoints...")
        self.test_api_endpoints()
        
        print("Testing Main Workflow...")
        self.test_main_workflow()
        
        print("Testing Knowledge Base...")
        self.test_knowledge_base()
        
        print("Testing Publishing Queue...")
        self.test_publishing_queue()
        
        print("Testing Policy Engine...")
        self.test_policy_check()
        
        # Print results
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60 + "\n")
        
        print(f"Successes ({len(self.successes)}):")
        for msg in self.successes:
            print(f"  {msg}")
        
        if self.issues:
            print(f"\nIssues ({len(self.issues)}):")
            for msg in self.issues:
                print(f"  {msg}")
        else:
            print("\nNo issues found! ✓")
        
        # Overall status
        print("\n" + "=" * 60)
        if self.backend_available and self.frontend_available:
            if not self.issues:
                print("SYSTEM STATUS: FULLY OPERATIONAL ✓")
            else:
                print("SYSTEM STATUS: MOSTLY WORKING - FIX ABOVE ISSUES")
        else:
            print("SYSTEM STATUS: CRITICAL ISSUES - CHECK CONNECTIVITY")
        print("=" * 60 + "\n")
        
        return len(self.issues) == 0

if __name__ == "__main__":
    validator = SystemValidator()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)
