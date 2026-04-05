import os
import tempfile
from databricks.sdk import WorkspaceClient

def download_volume_files():
    """
    Download FAISS files from UC volume using Databricks SDK.
    Uses correct SDK API: response.contents.read()
    """
    print("=" * 80)
    print("📥 Downloading FAISS files from Unity Catalog volume...")
    print("=" * 80)
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="nyaya_data_")
    print(f"📂 Temp directory: {temp_dir}")
    
    # Files to download
    volume_path = "/Volumes/workspace_7474652263326815/default/nyaya_volumes"
    files_to_download = {
        "legal_index.faiss": os.path.join(temp_dir, "legal_index.faiss"),
        "legal_metadata.pkl": os.path.join(temp_dir, "legal_metadata.pkl")
    }
    
    try:
        # Initialize Workspace Client
        w = WorkspaceClient()
        print("✅ Initialized Databricks SDK client")
        
        # Download each file
        for filename, local_path in files_to_download.items():
            volume_file_path = f"{volume_path}/{filename}"
            print(f"\n📥 Downloading: {filename}")
            print(f"   From: {volume_file_path}")
            print(f"   To: {local_path}")
            
            try:
                # Correct Databricks SDK syntax for downloading files
                response = w.files.download(volume_file_path)
                
                # Write the contents safely to the local temporary path
                with open(local_path, "wb") as f:
                    f.write(response.contents.read())
                
                # Verify
                if os.path.exists(local_path):
                    size = os.path.getsize(local_path)
                    print(f"   ✅ Downloaded successfully ({size:,} bytes)")
                else:
                    raise FileNotFoundError(f"File not found after download: {local_path}")
                    
            except Exception as e:
                print(f"   ❌ Failed to download {filename}: {e}")
                print(f"   Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                raise
        
        print("\n" + "=" * 80)
        print("✅ All files downloaded successfully!")
        print(f"📂 Files location: {temp_dir}")
        print("=" * 80)
        
        return temp_dir
        
    except Exception as e:
        print(f"\n❌ Error downloading files: {e}")
        print("\n💡 Possible issues:")
        print("   1. Service principal lacks READ permissions on volume")
        print("   2. Volume path is incorrect or inaccessible")
        print("   3. SDK version incompatibility")
        print("=" * 80)
        raise
