#!/usr/bin/env python3
"""
Check Weaviate Cloud Setup and Data Storage
Shows what's stored in your Weaviate cluster
"""

import sys
from pathlib import Path
sys.path.append('src')

import os
from dotenv import load_dotenv
load_dotenv()

def main():
    print("=" * 70)
    print("  Weaviate Cloud Status Check")
    print("=" * 70)
    print()

    # 1. Check environment
    print("1️⃣  Environment Configuration")
    print("-" * 70)
    url = os.getenv('WEAVIATE_URL')
    key = os.getenv('WEAVIATE_API_KEY')
    print(f"   URL: {url}")
    print(f"   API Key: {'✓ Set (' + str(len(key)) + ' chars)' if key else '✗ Not set'}")
    print()

    # 2. Connect to Weaviate
    print("2️⃣  Connecting to Weaviate Cloud")
    print("-" * 70)
    try:
        import weaviate
        from weaviate.classes.init import Auth

        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=url,
            auth_credentials=Auth.api_key(key),
            headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
        )
        print("   ✓ Connected successfully")
        print()

        # 3. Check cluster metadata
        print("3️⃣  Cluster Information")
        print("-" * 70)
        meta = client.get_meta()
        print(f"   Weaviate Version: {meta.get('version', 'Unknown')}")
        print()

        # 4. List all collections (classes)
        print("4️⃣  Collections (Classes) in Cluster")
        print("-" * 70)
        collections = client.collections.list_all()

        if collections:
            print(f"   Found {len(collections)} collection(s):")
            for name, collection in collections.items():
                print(f"   📦 {name}")
        else:
            print("   ⚠️  No collections found (index not created yet)")
        print()

        # 5. Check EssenceAI collection specifically
        print("5️⃣  EssenceAI Collection Details")
        print("-" * 70)

        if 'EssenceAI' in collections:
            essence_collection = client.collections.get("EssenceAI")

            # Get object count
            result = essence_collection.aggregate.over_all(total_count=True)
            count = result.total_count

            print(f"   Collection: EssenceAI")
            print(f"   📊 Total Objects: {count}")
            print(f"   💾 Status: {'✓ Data stored' if count > 0 else '⚠️ Empty'}")

            if count > 0:
                print()
                print(f"   🎉 SUCCESS! Weaviate is storing your data!")
                print(f"   📈 {count} vector embeddings stored in cloud")

                # Get a sample object
                print()
                print("   📄 Sample Data (first object):")
                response = essence_collection.query.fetch_objects(limit=1)
                if response.objects:
                    obj = response.objects[0]
                    print(f"      UUID: {obj.uuid}")
                    if hasattr(obj, 'properties'):
                        print(f"      Properties: {list(obj.properties.keys())[:5]}")
                    print(f"      ✓ Data is accessible from cloud")
            else:
                print()
                print("   ⚠️  Collection exists but is empty")
                print("   💡 Run migration script to populate it")
        else:
            print("   ⚠️  EssenceAI collection not found")
            print("   💡 Need to run initial setup/migration")

        print()

        # 6. Storage comparison
        print("6️⃣  Storage Comparison")
        print("-" * 70)

        # Check local storage
        local_storage = Path('.storage')
        if local_storage.exists():
            local_size = sum(f.stat().st_size for f in local_storage.rglob('*') if f.is_file())
            local_mb = local_size / (1024 * 1024)
            print(f"   Local Storage (.storage/): {local_mb:.2f} MB")
        else:
            print(f"   Local Storage (.storage/): Not found")

        if 'EssenceAI' in collections:
            essence_collection = client.collections.get("EssenceAI")
            result = essence_collection.aggregate.over_all(total_count=True)
            count = result.total_count
            # Rough estimate: ~1.5KB per vector embedding
            weaviate_mb = (count * 1.5) / 1024
            print(f"   Weaviate Cloud: ~{weaviate_mb:.2f} MB ({count} objects)")
            print()
            print("   💡 Weaviate stores only vectors (more efficient)")
            print("   💡 Local stores vectors + metadata + index")

        print()
        print("=" * 70)
        print("  Summary")
        print("=" * 70)

        if 'EssenceAI' in collections:
            essence_collection = client.collections.get("EssenceAI")
            result = essence_collection.aggregate.over_all(total_count=True)
            count = result.total_count

            if count > 0:
                print("  ✅ Weaviate is PROPERLY SET UP and STORING DATA")
                print(f"  📊 {count} embeddings stored in cloud")
                print("  ⚡ Index loads instantly (no rebuild needed)")
                print("  💰 No additional embedding costs")
            else:
                print("  ⚠️  Weaviate connected but collection is empty")
                print("  📝 Next: Run migration to upload embeddings")
        else:
            print("  ⚠️  Weaviate connected but no EssenceAI collection")
            print("  📝 Next: Run initial setup to create collection")

        print()

        client.close()

    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check WEAVIATE_URL starts with https://")
        print("  2. Verify WEAVIATE_API_KEY is correct")
        print("  3. Ensure cluster is running in console.weaviate.cloud")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
