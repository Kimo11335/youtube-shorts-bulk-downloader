import os
import getpass
import platform

def main():
    print("YouTube API Key Setup (Environment Variable)")
    print("-------------------------------------------")
    print("This will help you set up your YouTube API key as an environment variable.")
    
    api_key = getpass.getpass("Enter your YouTube API key: ")
    
    if not api_key:
        print("No API key entered. Operation cancelled.")
        return
    
    # Create or update .env file
    with open(".env", "w") as f:
        f.write(f"YOUTUBE_API_KEY={api_key}\n")
    
    print("\nAPI key saved to .env file.")
    print("Make sure to add .env to your .gitignore and .augmentignore files!")
    
    # Print instructions for setting environment variable
    system = platform.system()
    print("\nTo use this key in your current terminal session:")
    
    if system == "Windows":
        print(f'set YOUTUBE_API_KEY={api_key}')
        print("\nFor PowerShell:")
        print(f'$env:YOUTUBE_API_KEY="{api_key}"')
    else:  # Linux or macOS
        print(f'export YOUTUBE_API_KEY="{api_key}"')
    
    print("\nTo make this permanent, add the above line to your shell profile.")

if __name__ == "__main__":
    main()