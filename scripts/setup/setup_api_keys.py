"""
Interactive script to help set up API keys
This script will guide you through adding API keys to your .env file
"""
import os
from pathlib import Path

def setup_env_file():
    """Interactive setup for API keys"""
    env_path = Path('.env')
    env_template_path = Path('env_template.txt')
    
    print("=" * 60)
    print("API Key Setup for NBA Chatbot")
    print("=" * 60)
    print("\nThis script will help you add API keys to your .env file.")
    print("\nNote: Your chatbot works WITHOUT API keys using free ESPN API!")
    print("API keys are only needed for optional features:\n")
    print("  • Pinecone: Article search feature")
    print("  • RapidAPI: Alternative data source (backup)")
    print("\n" + "=" * 60 + "\n")
    
    # Check if .env exists
    if not env_path.exists():
        if env_template_path.exists():
            print("Creating .env file from template...")
            # Read template
            with open(env_template_path, 'r') as f:
                content = f.read()
            # Write to .env
            with open(env_path, 'w') as f:
                f.write(content)
            print("✓ Created .env file\n")
        else:
            print("Error: env_template.txt not found!")
            return
    else:
        print("✓ .env file already exists\n")
    
    # Read current .env
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Pinecone Key
    print("1. Pinecone API Key (for article search)")
    print("   Get it from: https://www.pinecone.io/")
    current_pinecone = env_vars.get('PINECONE_API_KEY', '')
    if current_pinecone and current_pinecone != 'your_pinecone_api_key_here':
        print(f"   Current: {current_pinecone[:10]}... (already set)")
        update = input("   Update? (y/n): ").lower() == 'y'
    else:
        update = True
    
    if update:
        pinecone_key = input("   Enter Pinecone API Key (or press Enter to skip): ").strip()
        if pinecone_key:
            env_vars['PINECONE_API_KEY'] = pinecone_key
            print("   ✓ Pinecone key updated")
        else:
            print("   ⚠ Skipped")
    
    print()
    
    # RapidAPI Key
    print("2. RapidAPI Key (for alternative NBA data)")
    print("   Get it from: https://rapidapi.com/")
    current_rapid = env_vars.get('RAPIDAPI_KEY', '')
    if current_rapid and current_rapid != 'your_rapidapi_key_here':
        print(f"   Current: {current_rapid[:10]}... (already set)")
        update = input("   Update? (y/n): ").lower() == 'y'
    else:
        update = True
    
    if update:
        rapidapi_key = input("   Enter RapidAPI Key (or press Enter to skip): ").strip()
        if rapidapi_key:
            env_vars['RAPIDAPI_KEY'] = rapidapi_key
            print("   ✓ RapidAPI key updated")
        else:
            print("   ⚠ Skipped")
    
    print()
    
    # Write updated .env file
    print("Updating .env file...")
    
    # Read template to preserve comments and structure
    lines = []
    with open(env_template_path, 'r') as f:
        template_lines = f.readlines()
    
    # Update .env file
    with open(env_path, 'w') as f:
        for line in template_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and '=' in stripped:
                key = stripped.split('=', 1)[0].strip()
                if key in env_vars:
                    # Update with new value
                    f.write(f"{key}={env_vars[key]}\n")
                else:
                    # Keep template value
                    f.write(line)
            else:
                # Keep comments and empty lines
                f.write(line)
    
    print("✓ .env file updated!")
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart your server to load new API keys")
    print("2. Test the chatbot to verify everything works")
    print("\nRemember: API keys are OPTIONAL - your chatbot works without them!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        setup_env_file()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\nError: {e}")

