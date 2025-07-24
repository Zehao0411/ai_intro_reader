"""
Environment setup helper for Economic Paper Introduction Analyzer
"""

import os

def setup_environment():
    """
    Help users set up their environment variables.
    """
    print("=== Economic Paper Introduction Analyzer - Environment Setup ===")
    print()
    
    # Check current API key
    current_key = os.getenv('DASHSCOPE_API_KEY')
    
    if current_key:
        print(f"✓ DASHSCOPE_API_KEY is already set: {current_key[:10]}...")
        choice = input("Do you want to update it? (y/n): ").lower()
        if choice != 'y':
            print("Environment setup complete!")
            return
    else:
        print("✗ DASHSCOPE_API_KEY is not set")
    
    print()
    print("To get your Tongyi Qwen API key:")
    print("1. Visit: https://dashscope.console.aliyun.com/")
    print("2. Log in to your Alibaba Cloud account")
    print("3. Navigate to API-KEY section")
    print("4. Create a new API key")
    print()
    
    api_key = input("Enter your DASHSCOPE_API_KEY: ").strip()
    
    if not api_key:
        print("No API key provided. Exiting...")
        return
    
    # Set environment variable for current session
    os.environ['DASHSCOPE_API_KEY'] = api_key
    
    print()
    print("✓ API key set for current session!")
    print()
    print("To make this permanent, add this to your system:")
    print()
    print("Windows PowerShell:")
    print(f'$env:DASHSCOPE_API_KEY="{api_key}"')
    print()
    print("Linux/Mac:")
    print(f'export DASHSCOPE_API_KEY="{api_key}"')
    print()
    print("Or create a .env file with:")
    print(f'DASHSCOPE_API_KEY={api_key}')
    print()
    print("You can also use the provided template:")
    print("cp env_example.txt .env")
    print("Then edit the .env file with your API key.")

if __name__ == "__main__":
    setup_environment() 