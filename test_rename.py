import os
from pathlib import Path

def create_test_files():
    """Creates test mp4 files in C:\PythonProjects\Videos"""
    # Set the test directory
    test_root = r"C:\PythonProjects\Videos"
    
    # Create test subdirectories
    subdirs = ['test_folder1', 'test_folder2/subtest', 'test_folder3']
    for subdir in subdirs:
        os.makedirs(os.path.join(test_root, subdir), exist_ok=True)
    
    # Define test files to create
    test_files = [
        'test1.mp4',
        'test_folder1/video1.mp4',
        'test_folder1/video2.mp4',
        'test_folder2/subtest/deep_video.mp4',
        'test_folder3/test_video.mp4',
        'test_folder3/not_video.txt'  # non-mp4 file to test selective renaming
    ]
    
    # Create empty files
    for file_path in test_files:
        full_path = os.path.join(test_root, file_path)
        Path(full_path).touch()
        print(f"Created: {full_path}")
    
    return test_root

def test_rename_mp4_to_webm():
    """Test the rename_mp4_to_webm function"""
    from rename_extensions import rename_mp4_to_webm
    
    # Create test files
    test_dir = create_test_files()
    print(f"\nCreated test files in: {test_dir}")
    
    # Print initial state
    print("\nInitial directory structure:")
    for path in Path(test_dir).rglob('*'):
        if path.is_file():
            print(f"  {path.relative_to(test_dir)}")
    
    # Confirm with user
    input("\nPress Enter to proceed with renaming files...")
    
    # Run the rename function
    print("\nRunning rename operation...")
    rename_mp4_to_webm(test_dir)
    
    # Print final state
    print("\nFinal directory structure:")
    for path in Path(test_dir).rglob('*'):
        if path.is_file():
            print(f"  {path.relative_to(test_dir)}")
    
    # Verify results
    mp4_count = len(list(Path(test_dir).rglob('*.mp4')))
    webm_count = len(list(Path(test_dir).rglob('*.webm')))
    
    print(f"\nVerification results:")
    print(f"  Remaining .mp4 files: {mp4_count} (should be 0)")
    print(f"  New .webm files: {webm_count} (should be 5)")
    print(f"  Other files unchanged: {'.txt' in str(list(Path(test_dir).rglob('*.txt')))}")

if __name__ == "__main__":
    print("Starting rename_mp4_to_webm function test...")
    test_rename_mp4_to_webm()