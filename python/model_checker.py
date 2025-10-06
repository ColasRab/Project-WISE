# test_models.py
import pickle
import os

model_dir = "python/models"
for filename in os.listdir(model_dir):
    if filename.endswith('.pkl'):
        filepath = os.path.join(model_dir, filename)
        print(f"\nTesting {filename}...")
        print(f"  Size: {os.path.getsize(filepath)} bytes")
        
        try:
            with open(filepath, 'rb') as f:
                model = pickle.load(f)
            print(f"  ✅ OK - Can load successfully")
        except Exception as e:
            print(f"  ❌ FAILED: {e}")