import requests
import time

print("Testing University RAG System...")
print("=" * 50)

# Test 1: Backend Health Check
print("\n1. Testing Backend Health Check...")
try:
    response = requests.get("http://localhost:8000/", timeout=5)
    if response.status_code == 200:
        print("✅ Backend is running")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Backend returned status {response.status_code}")
except Exception as e:
    print(f"❌ Backend connection failed: {e}")

# Test 2: Get Status
print("\n2. Testing Status Endpoint...")
try:
    response = requests.get("http://localhost:8000/status", timeout=10)
    if response.status_code == 200:
        status = response.json()
        print("✅ Status endpoint working")
        print(f"   Documents loaded: {status['documents_loaded']}")
        print(f"   Chunk count: {status['chunk_count']}")
        print(f"   Categories: {status['categories']}")
    else:
        print(f"❌ Status returned {response.status_code}")
except Exception as e:
    print(f"❌ Status request failed: {e}")

# Test 3: Load Documents
print("\n3. Testing Document Loading...")
try:
    response = requests.post("http://localhost:8000/load-documents", timeout=10)
    if response.status_code == 200:
        print("✅ Document loading initiated")
        print(f"   Response: {response.json()}")
        
        # Wait for processing
        print("   Waiting for document processing (30 seconds)...")
        time.sleep(30)
        
        # Check status again
        response = requests.get("http://localhost:8000/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"   After loading - Chunks: {status['chunk_count']}")
    else:
        print(f"❌ Load documents returned {response.status_code}")
except Exception as e:
    print(f"❌ Load documents failed: {e}")

# Test 4: Query System
print("\n4. Testing Query Endpoint...")
try:
    # Wait a bit more for processing
    time.sleep(10)
    
    response = requests.post(
        "http://localhost:8000/query",
        json={"question": "What is the attendance requirement?", "top_k": 3},
        timeout=30
    )
    if response.status_code == 200:
        result = response.json()
        print("✅ Query endpoint working")
        print(f"   Found: {result['found']}")
        print(f"   Sources: {len(result['sources'])}")
        if result['found']:
            print(f"   Answer preview: {result['answer'][:100]}...")
    else:
        print(f"❌ Query returned {response.status_code}")
except Exception as e:
    print(f"❌ Query failed: {e}")

print("\n" + "=" * 50)
print("System Test Complete!")
