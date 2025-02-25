import getpass
import sys

def main():
    print("YouTube API Key Setup")
    print("---------------------")
    print("This will securely store your API key in your system's credential manager.")
    print("The key will not be stored in any file that could be accidentally shared.")
    
    try:
        import keyring
    except ImportError:
        print("Error: The keyring module is not installed.")
        print("Please install it using: pip install keyring")
        sys.exit(1)
    
    api_key = getpass.getpass("Enter your YouTube API key: ")
    
    if api_key:
        try:
            keyring.set_password("youtube_api", "api_key", api_key)
            print("API key stored successfully!")
        except Exception as e:
            print(f"Error storing API key: {e}")
            print("You may need to set up a keyring backend for your system.")
            print("See: https://keyring.readthedocs.io/en/latest/")
    else:
        print("No API key entered. Operation cancelled.")

if __name__ == "__main__":
    main()
