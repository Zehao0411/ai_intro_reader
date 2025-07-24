"""
Interactive configuration editor for Economic Paper Introduction Analyzer
"""

import json
import os
from pathlib import Path

def load_config():
    """Load current configuration."""
    config_file = "config.json"
    if Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("Config file not found. Using defaults.")
        return create_default_config()

def create_default_config():
    """Create default configuration."""
    return {
        "llm_settings": {
            "model": "qwen-plus",
            "temperature": 0,
            "max_tokens": 16000,
            "top_p": 0.8
        },
        "extraction_settings": {
            "case_sensitive": False,
            "fuzzy_matching": True,
            "max_intro_length": 32000,
            "fallback_intro_length": 20000,
            "search_flexibility": True
        },
        "output_settings": {
            "save_raw_intros": True,
            "markdown_format": True,
            "include_metadata": True,
            "rate_limit_delay": 0.2,
        },
        "prompt_template": {
            "system_instruction": "You are an expert economist analyzing research papers. Focus on economic insights and contributions rather than technical details.",
            "analysis_sections": [
                "Research Problem",
                "Significance & Motivation",
                "Main Findings & Intuition", 
                "Methodological Contributions",
                "Key Insights"
            ]
        }
    }

def save_config(config):
    """Save configuration to file."""
    with open("config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("✓ Configuration saved to config.json")

def edit_llm_settings(config):
    """Edit LLM-related settings."""
    print("\n=== LLM Settings ===")
    settings = config["llm_settings"]
    
    print(f"Current model: {settings['model']}")
    new_model = input(f"Enter new model (or press Enter to keep '{settings['model']}'): ").strip()
    if new_model:
        settings['model'] = new_model
    
    print(f"Current temperature: {settings['temperature']}")
    new_temp = input(f"Enter new temperature 0-1 (or press Enter to keep {settings['temperature']}): ").strip()
    if new_temp:
        try:
            settings['temperature'] = float(new_temp)
        except ValueError:
            print("Invalid temperature, keeping current value")
    
    print(f"Current max_tokens: {settings['max_tokens']}")
    new_tokens = input(f"Enter new max_tokens (or press Enter to keep {settings['max_tokens']}): ").strip()
    if new_tokens:
        try:
            settings['max_tokens'] = int(new_tokens)
        except ValueError:
            print("Invalid max_tokens, keeping current value")
    
    print(f"Current top_p: {settings['top_p']}")
    new_top_p = input(f"Enter new top_p 0-1 (or press Enter to keep {settings['top_p']}): ").strip()
    if new_top_p:
        try:
            settings['top_p'] = float(new_top_p)
        except ValueError:
            print("Invalid top_p, keeping current value")

def edit_extraction_settings(config):
    """Edit text extraction settings."""
    print("\n=== Extraction Settings ===")
    settings = config["extraction_settings"]
    
    print(f"Current case_sensitive: {settings['case_sensitive']}")
    new_case = input("Case sensitive matching? (y/n or press Enter to keep current): ").strip().lower()
    if new_case in ['y', 'yes']:
        settings['case_sensitive'] = True
    elif new_case in ['n', 'no']:
        settings['case_sensitive'] = False
    
    print(f"Current fuzzy_matching: {settings['fuzzy_matching']}")
    new_fuzzy = input("Enable fuzzy matching? (y/n or press Enter to keep current): ").strip().lower()
    if new_fuzzy in ['y', 'yes']:
        settings['fuzzy_matching'] = True
    elif new_fuzzy in ['n', 'no']:
        settings['fuzzy_matching'] = False
    
    print(f"Current max_intro_length: {settings['max_intro_length']}")
    new_max = input(f"Enter max introduction length (or press Enter to keep {settings['max_intro_length']}): ").strip()
    if new_max:
        try:
            settings['max_intro_length'] = int(new_max)
        except ValueError:
            print("Invalid length, keeping current value")
    
    print(f"Current fallback_intro_length: {settings['fallback_intro_length']}")
    new_fallback = input(f"Enter fallback length (or press Enter to keep {settings['fallback_intro_length']}): ").strip()
    if new_fallback:
        try:
            settings['fallback_intro_length'] = int(new_fallback)
        except ValueError:
            print("Invalid length, keeping current value")

def edit_output_settings(config):
    """Edit output-related settings."""
    print("\n=== Output Settings ===")
    settings = config["output_settings"]
    
    print(f"Current rate_limit_delay: {settings['rate_limit_delay']} seconds")
    new_delay = input(f"Enter delay between API calls in seconds (or press Enter to keep {settings['rate_limit_delay']}): ").strip()
    if new_delay:
        try:
            settings['rate_limit_delay'] = float(new_delay)
        except ValueError:
            print("Invalid delay, keeping current value")
    
    print(f"Current save_raw_intros: {settings['save_raw_intros']}")
    new_save = input("Save raw introduction text files? (y/n or press Enter to keep current): ").strip().lower()
    if new_save in ['y', 'yes']:
        settings['save_raw_intros'] = True
    elif new_save in ['n', 'no']:
        settings['save_raw_intros'] = False

def view_config(config):
    """Display current configuration."""
    print("\n=== Current Configuration ===")
    print(json.dumps(config, indent=2, ensure_ascii=False))

def main():
    """Main configuration editor."""
    print("=== Economic Paper Analyzer - Configuration Editor ===")
    
    config = load_config()
    
    while True:
        print("\nOptions:")
        print("1. View current configuration")
        print("2. Edit LLM settings (model, temperature, etc.)")
        print("3. Edit extraction settings (fuzzy matching, etc.)")
        print("4. Edit output settings (delays, file saving)")
        print("5. Reset to defaults")
        print("6. Save and exit")
        print("7. Exit without saving")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            view_config(config)
        elif choice == '2':
            edit_llm_settings(config)
        elif choice == '3':
            edit_extraction_settings(config)
        elif choice == '4':
            edit_output_settings(config)
        elif choice == '5':
            confirm = input("Reset to defaults? This will overwrite current settings (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                config = create_default_config()
                print("✓ Configuration reset to defaults")
        elif choice == '6':
            save_config(config)
            break
        elif choice == '7':
            print("Exiting without saving changes.")
            break
        else:
            print("Invalid choice. Please enter 1-7.")

if __name__ == "__main__":
    main() 