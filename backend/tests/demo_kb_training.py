#!/usr/bin/env python3
"""
Interactive KB Training & Testing Script
=========================================
Demonstrates the complete flow from document upload to model training.
"""

import requests
import json
import time
from pathlib import Path

API_BASE = "http://localhost:8088"

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_step(step_num, title):
    """Print a step header."""
    print(f"\n📍 STEP {step_num}: {title}")
    print("-" * 70)

def demo_check_current_documents():
    """Show what documents are currently in the KB."""
    print_step(1, "Check Current Documents in KB")
    
    try:
        response = requests.get(f"{API_BASE}/api/knowledge_base/documents")
        data = response.json()
        
        print(f"✅ Total documents in knowledge base: {data['total']}\n")
        
        for doc in data['documents']:
            print(f"📄 {doc['filename']}")
            print(f"   Category: {doc['category']}")
            print(f"   Size: {doc['size_chars']} characters")
            print(f"   Uploaded: {doc['uploaded_at']}\n")
            
        return data['total']
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def demo_search_kb(query):
    """Search the knowledge base."""
    print_step(2, f"Search KB for: '{query}'")
    
    try:
        response = requests.get(f"{API_BASE}/api/knowledge_base/search", params={'query': query})
        data = response.json()
        
        print(f"✅ Found {data['results_count']} matching results\n")
        
        for result in data['results'][:3]:
            print(f"📌 {result['title']} (Relevance: {result['relevance_score']:.0%})")
            print(f"   Category: {result['category']}")
            print(f"   Preview: {result['content'][:150]}...\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_get_context():
    """Show what context is injected into LLM."""
    print_step(3, "See KB Context Injected into LLM")
    
    try:
        response = requests.get(f"{API_BASE}/api/knowledge_base/context/llm")
        data = response.json()
        
        context = data['context']
        print(f"✅ KB context retrieved: {len(context)} characters\n")
        print("Context sample (first 500 chars):")
        print("-" * 70)
        print(context[:500] + "...\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_upload_document():
    """Demonstrate uploading a document."""
    print_step(4, "Upload a Test Document")
    
    # Create a test document
    test_doc = """
    Custom Brand Guidelines Document (Example)
    
    Brand Name: My Awesome Company
    Industry: Technology / SaaS
    
    Brand Voice:
    - Friendly but professional
    - Educational
    - Empowering
    - Action-oriented
    
    Target Audience:
    - Age: 25-45
    - Tech-savvy professionals
    - Looking for productivity solutions
    - Value time-saving tools
    
    Key Messages:
    1. Save time with automation
    2. Built for teams
    3. Security-first approach
    
    Do's:
    ✓ Use clear, simple language
    ✓ Show real benefits
    ✓ Focus on customer success
    
    Don'ts:
    ✗ Use jargon without explaining
    ✗ Make unsubstantiated claims
    ✗ Sound corporate or stiff
    """
    
    # Write to temp file
    test_path = "temp_test_doc.txt"
    with open(test_path, 'w') as f:
        f.write(test_doc)
    
    try:
        # Upload via API
        with open(test_path, 'rb') as f:
            files = {'file': f}
            data = {'category': 'Brand voice'}
            
            response = requests.post(
                f"{API_BASE}/api/knowledge_base/upload",
                files=files,
                data=data
            )
        
        result = response.json()
        
        print(f"✅ Document uploaded successfully!")
        print(f"   Document ID: {result['id']}")
        print(f"   Filename: {result['filename']}")
        print(f"   Category: {result['category']}")
        print(f"   Size: {result['content_length']} characters")
        print(f"   Status: {result['status']}\n")
        
        # Clean up
        Path(test_path).unlink()
        
        return result['id']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        Path(test_path).unlink()
        return None

def demo_verify_upload():
    """Verify the uploaded document can be found."""
    print_step(5, "Verify Uploaded Document in Database")
    
    try:
        response = requests.get(f"{API_BASE}/api/knowledge_base/documents", params={'category': 'Brand voice'})
        data = response.json()
        
        brand_docs = [d for d in data['documents'] if d['category'] == 'Brand voice']
        
        print(f"✅ Brand voice documents in KB: {len(brand_docs)}\n")
        
        # Show newest
        if brand_docs:
            newest = sorted(brand_docs, key=lambda x: x['uploaded_at'], reverse=True)[0]
            print(f"📄 Latest: {newest['filename']}")
            print(f"   Uploaded: {newest['uploaded_at']}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_generate_with_kb():
    """Generate a strategy using the KB."""
    print_step(6, "Generate Strategy Using KB Context")
    
    print("Creating test brand profile...")
    
    test_state = {
        "brand_profile": {
            "brand_name": "TestTech",
            "industry": "Technology",
            "product_category": "SaaS",
            "voice_keywords": ["friendly", "professional", "empowering"]
        },
        "target_persona": {
            "age_range": "25-45",
            "interests": ["productivity", "automation", "business"],
            "challenges": ["time management", "team coordination"]
        },
        "active_platforms": ["LinkedIn", "Twitter"],
        "posting_frequency": {"LinkedIn": 3, "Twitter": 5}
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/social_manager/run",
            json={"state": test_state},
            timeout=60
        )
        
        result = response.json()
        state = result.get('state', {})
        
        print("✅ Strategy generated successfully!\n")
        
        # Show generated outputs
        outputs = {
            "Content Pillars": state.get('content_pillars', []),
            "Platform Strategies": state.get('platform_strategies', {}),
            "Engagement Plan": state.get('engagement_plan'),
            "UGC Strategy": state.get('ugc_strategy'),
        }
        
        for output_name, output_value in outputs.items():
            if output_value:
                print(f"✅ {output_name}: Generated")
            else:
                print(f"❌ {output_name}: Missing")
        
        # Show sample content pillar
        if state.get('content_pillars'):
            pillar = state['content_pillars'][0]
            print(f"\n📌 Sample Content Pillar:")
            print(f"   Name: {pillar.get('name')}")
            print(f"   Goal: {pillar.get('goal')}")
            print(f"   Post Types: {', '.join(pillar.get('post_types', []))}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_architecture():
    """Show the KB architecture."""
    print_section("ARCHITECTURE: How Documents Flow Through System")
    
    diagram = """
    USER UPLOADS DOCUMENT
              ↓
    POST /api/knowledge_base/upload
              ↓
    DocumentParser.parse_pdf/docx/txt/csv
              ↓
    Extract text content
              ↓
    KnowledgeBaseManager.add_document()
              ↓
    SQLite Database (social_manager.db)
    ┌────────────────────────────────────┐
    │ TABLE: knowledge_documents         │
    ├────────────────────────────────────┤
    │ id | filename | category | content│
    │ 1  | brand.pdf| Brand... | [text] │ ← STORED HERE
    │ 2  | audience | Target.. | [text] │   (NOT hardcoded)
    │ 3  | competitor | Compet.| [text] │
    └────────────────────────────────────┘
              ↑
    GET /api/knowledge_base/documents
    (returns list of stored docs)
              ↓
         AT RUNTIME:
    Agent nodes request context
              ↓
    kb_context_injector queries database
    SELECT * FROM knowledge_documents
    WHERE category = 'Brand voice'
              ↓
    Document content injected into prompt
              ↓
    LLM receives enriched prompt
              ↓
    Generates tailored output using YOUR data
    """
    
    print(diagram)

def main():
    """Run interactive demo."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  KNOWLEDGE BASE TRAINING - Interactive Demo".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    print("\nThis demo shows:")
    print("1. Current documents in KB (from database)")
    print("2. Searching documents")
    print("3. KB context injected into LLM")
    print("4. Uploading a new document")
    print("5. Verifying upload in database")
    print("6. Generating strategy with KB context")
    
    # Check if server is running
    try:
        requests.get(f"{API_BASE}/health", timeout=2)
    except:
        print("\n❌ ERROR: Backend server not running!")
        print("   Start it with: python main.py")
        return
    
    # Show architecture
    show_architecture()
    
    # Run demo steps
    print_section("Running Demo Steps")
    
    # Step 1: Check documents
    doc_count = demo_check_current_documents()
    
    # Step 2: Search
    demo_search_kb("brand")
    
    # Step 3: Get context
    demo_get_context()
    
    # Step 4: Upload
    doc_id = demo_upload_document()
    
    if doc_id:
        print(f"⏳ Waiting for document to be indexed...")
        time.sleep(1)
        
        # Step 5: Verify
        demo_verify_upload()
    
    # Step 6: Generate
    demo_generate_with_kb()
    
    # Summary
    print_section("Summary")
    
    print("""
✅ COMPLETE FLOW DEMONSTRATED:

1. Documents stored in SQLite database (NOT hardcoded)
2. Documents uploaded via API/UI
3. Content extracted from files
4. Stored in database table
5. Agents query database at runtime
6. KB context injected into LLM prompts
7. Model generates tailored outputs

KEY TAKEAWAYS:

📌 Documents are database records, not Python code
📌 Upload via API or frontend - instantly available
📌 Agents automatically use KB when generating strategies
📌 Different categories affect different agent decisions
📌 You control what model knows by controlling KB

NEXT STEPS:

→ Upload your actual brand documents
→ Generate strategy - see personalization
→ Add audience research - strategies personalize more
→ Add competitor data - strategies differentiate
→ Monitor KB size - keep only relevant docs

Questions? See KB_TRAINING_COMPLETE_GUIDE.md for details.
    """)

if __name__ == "__main__":
    main()
