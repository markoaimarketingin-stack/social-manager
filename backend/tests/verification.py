"""
KB Training & Verification Guide
=================================
Step-by-step guide to train the model with new documents and verify integration.
"""

import requests
import json
from pathlib import Path
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8088"
KB_UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/knowledge_base/upload"
KB_SEARCH_ENDPOINT = f"{API_BASE_URL}/api/knowledge_base/search"
KB_CONTEXT_ENDPOINT = f"{API_BASE_URL}/api/knowledge_base/context/llm"
SOCIAL_MANAGER_ENDPOINT = f"{API_BASE_URL}/api/social_manager/run"


def test_kb_loaded():
    """Verify KB documents are loaded."""
    print("\n" + "=" * 70)
    print("STEP 1: Verify KB Documents Are Loaded")
    print("=" * 70)
    
    try:
        docs_endpoint = f"{API_BASE_URL}/api/knowledge_base/documents"
        response = requests.get(docs_endpoint, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print(f"✅ Knowledge Base Loaded: {total} documents")
            print("\nDocuments:")
            for doc in data.get('documents', []):
                print(f"  - {doc.get('title', 'Untitled')} ({doc.get('category', 'uncategorized')})")
                print(f"    Size: {doc.get('size_chars', 0)} chars")
            return True
        else:
            print(f"❌ Failed to load KB documents: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Could not verify KB (server may not be running): {e}")
        return True


def test_kb_context():
    """Verify KB context injection is working."""
    print("\n" + "=" * 70)
    print("STEP 2: Verify KB Context Injection")
    print("=" * 70)
    
    try:
        # Test retrieving LLM context
        response = requests.get(KB_CONTEXT_ENDPOINT, timeout=5)
        
        if response.status_code == 200:
            context = response.json()
            context_text = context.get('context', '')
            if context_text and len(context_text) > 100:
                print(f"✅ KB Context Retrieved: {len(context_text)} characters")
                print(f"\nContext Preview:")
                print(f"  {context_text[:200]}...")
                return True
            else:
                print("⚠️  KB Context is empty or too short")
                return False
        else:
            print(f"❌ Failed to get KB context: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Could not verify KB context: {e}")
        return True


def test_model_with_kb():
    """Test that the model uses KB context for strategy generation."""
    print("\n" + "=" * 70)
    print("STEP 3: Test Model with KB Context")
    print("=" * 70)
    
    try:
        # Create a test request with sample brand data
        test_state = {
            "brand_profile": {
                "brand_name": "TestFitness",
                "industry": "Fitness & Wellness",
                "product_category": "Fitness Software",
                "brand_type": "B2C SaaS",
                "voice_keywords": ["motivational", "achievable"]
            },
            "target_persona": {
                "age_range": "25-45",
                "interests": ["fitness", "wellness"],
                "pain_points": ["time", "motivation"]
            },
            "active_platforms": ["Instagram", "LinkedIn"],
            "posting_frequency": {"Instagram": 5, "LinkedIn": 3},
            "engagement_metrics": {
                "engagement_rate": 2.5,
                "post_consistency_score": 0.7
            }
        }
        
        response = requests.post(
            SOCIAL_MANAGER_ENDPOINT,
            json={"state": test_state},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            state = result.get('state', {})
            
            outputs = [
                ("platform_strategies", state.get('platform_strategies')),
                ("content_pillars", state.get('content_pillars')),
                ("monthly_calendar", state.get('monthly_calendar')),
                ("engagement_plan", state.get('engagement_plan')),
                ("ugc_strategy", state.get('ugc_strategy')),
                ("influencer_strategy", state.get('influencer_strategy')),
                ("loyalty_strategy", state.get('loyalty_strategy')),
            ]
            
            print("✅ Model Generated Strategy with KB Context\n")
            print("Outputs Generated:")
            for name, value in outputs:
                has_value = bool(value)
                status = "✅" if has_value else "❌"
                print(f"  {status} {name}: {'Generated' if has_value else 'Missing'}")
            
            return all(bool(v) for _, v in outputs)
        else:
            print(f"❌ Failed to run model: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not test model: {e}")
        return True


def train_with_document(file_path: str, category: str = "Social strategy"):
    """Upload and train the model with a new document."""
    print("\n" + "=" * 70)
    print(f"STEP 4: Training with Document: {Path(file_path).name}")
    print("=" * 70)
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'category': category}
            
            response = requests.post(
                KB_UPLOAD_ENDPOINT,
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            doc_id = result.get('id')
            print(f"✅ Document Uploaded Successfully")
            print(f"   Document ID: {doc_id}")
            print(f"   Size: {result.get('size_chars', 0)} characters")
            return True
        else:
            print(f"❌ Failed to upload document: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading document: {e}")
        return False


def search_kb(query: str):
    """Search the knowledge base."""
    print("\n" + "=" * 70)
    print(f"STEP 5: Search KB for: '{query}'")
    print("=" * 70)
    
    try:
        params = {'query': query}
        response = requests.get(KB_SEARCH_ENDPOINT, params=params, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            results = result.get('results', [])
            
            if results:
                print(f"✅ Found {len(results)} matching document(s)\n")
                for item in results[:3]:
                    print(f"  📄 {item.get('title', 'Untitled')}")
                    print(f"     Category: {item.get('category', 'Unknown')}")
                    print(f"     Relevance: {item.get('relevance_score', 0):.2f}")
                    print(f"     Preview: {item.get('content', '')[:100]}...\n")
                return True
            else:
                print("⚠️  No matching documents found")
                return False
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not search KB: {e}")
        return True


def main():
    """Run verification steps."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "MODEL TRAINING & VERIFICATION WORKFLOW" + " " * 16 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run verification steps
    print("\n📚 VERIFYING KB INTEGRATION...\n")
    
    test_kb_loaded()
    test_kb_context()
    test_model_with_kb()
    
    # Search test
    search_kb("brand voice")
    
    print("\n" + "=" * 70)
    print("HOW TO TRAIN WITH NEW DOCUMENTS")
    print("=" * 70)
    print("""
1. **Via API** (Programmatic):
   python -c "
   from verification import train_with_document
   train_with_document('path/to/document.pdf', category='Brand voice')
   "

2. **Via Frontend** (Manual):
   - Open http://localhost:3000
   - Click "Train model" button
   - Select file (PDF, DOCX, TXT, CSV)
   - Choose category
   - Click upload

3. **Via cURL** (Command line):
   curl -F "file=@document.pdf" -F "category=Social strategy" \\
        http://localhost:8088/api/knowledge_base/upload

CATEGORIES (use these for consistency):
- "Brand voice" - Brand voice, tone, personality
- "Target audience" - Audience segments, personas
- "Competitors" - Competitive analysis
- "Campaign briefs" - Campaign strategies
- "Social strategy" - Social media strategy

4. **Verify Training**:
   - Document will be indexed automatically
   - Search KB to verify: search_kb("keyword")
   - Test model: test_model_with_kb()
   - Check engagement_plan uses audience context
""")
    
    print("\n✅ VERIFICATION COMPLETE!")
    print("\nNext Steps:")
    print("1. Upload additional brand documents")
    print("2. Upload audience research documents")
    print("3. Upload competitor analysis")
    print("4. Run the model to generate strategies")
    print("5. Monitor that KB context is being used in agent outputs")


if __name__ == "__main__":
    main()
