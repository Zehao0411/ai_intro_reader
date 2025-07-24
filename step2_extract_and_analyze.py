"""
Step 2: Extract introduction sections and analyze with Tongyi Qwen Plus
This script reads the annotated JSON file, extracts introduction sections
from PDFs, and uses Tongyi Qwen Plus to analyze and structure the information.
"""

import os
import json
import pdfplumber
from pathlib import Path
from tqdm import tqdm
import dashscope
from dashscope import Generation
import time
import re
from dotenv import load_dotenv
import difflib

# Load environment variables from .env file
load_dotenv()

def load_config(config_file="config.json"):
    """
    Load configuration settings from JSON file.
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file {config_file} not found. Using default settings.")
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
            }
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}. Using default settings.")
        return load_config.__defaults__[0] if hasattr(load_config, '__defaults__') else {}

def load_annotation_file(filename="papers_annotation.json"):
    """
    Load the manually annotated JSON file.
    """
    if not Path(filename).exists():
        print(f"Error: {filename} not found!")
        print("Please run step1_generate_json.py first and fill in the start/end markers.")
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_flexible_marker(text, marker, config, search_type="start"):
    """
    Find marker in text with flexible matching strategies.
    """
    if not marker:
        return -1
    
    # Strategy 1: Exact match (case-sensitive or not)
    if config["extraction_settings"]["case_sensitive"]:
        pos = text.find(marker)
    else:
        pos = text.lower().find(marker.lower())
    
    if pos != -1:
        return pos
    
    if not config["extraction_settings"]["search_flexibility"]:
        return -1
    
    # Strategy 2: Fuzzy matching with difflib
    if config["extraction_settings"]["fuzzy_matching"]:
        lines = text.split('\n')
        best_match_pos = -1
        best_ratio = 0.6  # Minimum similarity threshold
        
        for i, line in enumerate(lines):
            line_clean = re.sub(r'\s+', ' ', line.strip())
            marker_clean = re.sub(r'\s+', ' ', marker.strip())
            
            if not config["extraction_settings"]["case_sensitive"]:
                line_clean = line_clean.lower()
                marker_clean = marker_clean.lower()
            
            ratio = difflib.SequenceMatcher(None, line_clean, marker_clean).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                # Find position of this line in original text
                best_match_pos = text.find(lines[i])
        
        if best_match_pos != -1:
            print(f"Found {search_type} marker using fuzzy matching (similarity: {best_ratio:.2f})")
            return best_match_pos
    
    # Strategy 3: Pattern-based matching
    patterns = []
    marker_lower = marker.lower() if not config["extraction_settings"]["case_sensitive"] else marker
    
    # Common introduction patterns
    if "introduction" in marker_lower:
        patterns.extend([
            r'\b\d+\.\s*introduction\b',
            r'\bintroduction\b',
            r'\bintro\b',
            r'\b1\s+introduction\b',
            r'\bsection\s+\d+.*introduction\b'
        ])
    
    # Try regex patterns
    flags = re.IGNORECASE if not config["extraction_settings"]["case_sensitive"] else 0
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            print(f"Found {search_type} marker using pattern: {pattern}")
            return match.start()
    
    return -1

def extract_introduction_from_pdf(pdf_path, start_marker, end_marker, config):
    """
    Extract introduction section from PDF with flexible matching.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        
        if not full_text.strip():
            print(f"Warning: No extractable text found in {pdf_path}")
            return None
        
        # Find start position with flexible matching
        start_pos = find_flexible_marker(full_text, start_marker, config, "start")
        if start_pos == -1:
            print(f"Warning: Start marker '{start_marker}' not found in {pdf_path}")
            print("Trying alternative strategies...")
            
            # Fallback: Look for common introduction patterns
            intro_patterns = [
                r'\b1\.\s*introduction\b',
                r'\bintroduction\b',
                r'\b1\s+introduction\b'
            ]
            flags = re.IGNORECASE if not config["extraction_settings"]["case_sensitive"] else 0
            
            for pattern in intro_patterns:
                match = re.search(pattern, full_text, flags)
                if match:
                    start_pos = match.start()
                    print(f"Found introduction using fallback pattern: {pattern}")
                    break
            
            if start_pos == -1:
                print("Could not find introduction section.")
                return None
        
        # Find end position with flexible matching
        end_pos = find_flexible_marker(full_text[start_pos + len(start_marker):], end_marker, config, "end")
        
        if end_pos == -1:
            print(f"Warning: End marker '{end_marker}' not found, using fallback length")
            # Use fallback length from config
            fallback_length = config["extraction_settings"]["fallback_intro_length"]
            introduction = full_text[start_pos:start_pos + fallback_length]
        else:
            # Adjust end_pos to be relative to full_text
            end_pos = start_pos + len(start_marker) + end_pos
            introduction = full_text[start_pos:end_pos]
        
        # Limit maximum introduction length
        max_length = config["extraction_settings"]["max_intro_length"]
        if len(introduction) > max_length:
            introduction = introduction[:max_length]
            print(f"Truncated introduction to {max_length} characters")
        
        # Clean up the text
        introduction = re.sub(r'\s+', ' ', introduction)  # Normalize whitespace
        introduction = introduction.strip()
        
        if len(introduction) < 100:
            print(f"Warning: Extracted introduction is very short ({len(introduction)} chars)")
        
        return introduction
        
    except Exception as e:
        print(f"Error extracting introduction from {pdf_path}: {e}")
        return None

def analyze_with_qwen(introduction_text, paper_title, paper_type, config):
    """
    Send introduction text to Tongyi Qwen Plus for analysis using config settings.
    Uses different prompt templates based on paper type (theoretical vs empirical).
    """
    
    # Validate paper type
    if paper_type not in ["theoretical", "empirical"]:
        print(f"Warning: Unknown paper type '{paper_type}'. Using theoretical template as fallback.")
        paper_type = "theoretical"
    
    # Get type-specific prompt template
    prompt_templates = config.get("prompt_template", {})
    type_template = prompt_templates.get(paper_type, {})
    
    if not type_template:
        print(f"Warning: No template found for paper type '{paper_type}'. Using fallback.")
        # Fallback to basic template
        sections = ["Research Problem", "Methodology", "Findings", "Implications"]
        system_instruction = "You are an expert economist analyzing research papers. Focus on economic insights and contributions rather than technical details."
    else:
        sections = type_template.get("analysis_sections", ["Analysis"])
        system_instruction = type_template.get("system_instruction", 
            "You are an expert economist analyzing research papers. Focus on economic insights and contributions rather than technical details.")
    
    # Build sections for prompt
    sections_text = ""
    for section in sections:
        # Theoretical paper sections
        if section == "Research Problem":
            sections_text += f"### {section}\n- What specific question does this paper address?\n\n"
        elif section == "Significance & Motivation":
            sections_text += f"### {section}\n- Why is this problem important or interesting?\n- How is it connected to existing work?\n- How does it differ from existing work?\n\n"
        elif section == "Main Findings & Intuition":
            sections_text += f"### {section}\n- What is the paper's answer to the research question?\n- What's the key intuition or mechanism?\n\n"
        elif section == "Model Setup & Assumptions":
            sections_text += f"### {section}\n- What is the basic model structure?\n- What are the key assumptions?\n- How do these assumptions relate to the research question?\n\n"
        elif section == "Methodological Contributions":
            sections_text += f"### {section}\n- Does this paper have any methodological contributions?\n- If yes, what are the key methodological innovations?\n\n"
        elif section == "Policy Implications":
            sections_text += f"### {section}\n- What are the policy recommendations or implications?\n\n"
        elif section == "Key Insights":
            sections_text += f"### {section}\n- Additional important takeaways\n\n"
        
        # Empirical paper sections
        elif section == "Research Question":
            sections_text += f"### {section}\n- What empirical question does this paper investigate?\n- What is the main hypothesis being tested?\n\n"
        elif section == "Significance & Motivation":
            sections_text += f"### {section}\n- Why is this problem important or interesting?\n- How is it connected to existing work?\n- How does it differ from existing work?\n\n"
        elif section == "Main Findings":
            sections_text += f"### {section}\n- What are the main empirical results?\n\n"
        elif section == "Data":
            sections_text += f"### {section}\n- What data sources are used?\n- What is the sample period and coverage?\n- What are the key variables?\n\n"
        elif section == "Identification Strategy":
            sections_text += f"### {section}\n- How does the paper establish causal identification?\n- What is the source of exogenous variation?\n- What are potential threats to identification?\n\n"
        elif section == "Robustness & Limitations":
            sections_text += f"### {section}\n- What robustness checks are mentioned?\n- What are the main limitations of the approach?\n\n"
        elif section == "Policy Implications":
            sections_text += f"### {section}\n- What are the policy recommendations or implications?\n\n"
        # Generic fallback
        else:
            sections_text += f"### {section}\n[Analyze this aspect of the paper]\n\n"
    
    prompt = f"""{system_instruction}

Please analyze the following introduction section from an economic research paper and extract key information in a structured format.

Paper Title: {paper_title}

Introduction Text:
{introduction_text}

Please provide a structured analysis in the following format:

{sections_text}Focus on economic intuitions, insights and contributions rather than technical details. Please be concise, clear and accurate."""

    # Get LLM settings from config
    llm_settings = config.get("llm_settings", {})
    
    try:
        response = Generation.call(
            model=llm_settings.get("model", "qwen-plus"),
            prompt=prompt,
            temperature=llm_settings.get("temperature", 0),
            max_tokens=llm_settings.get("max_tokens", 32000),
            top_p=llm_settings.get("top_p", 0.8)
        )
        
        if response.status_code == 200:
            return response.output.text
        else:
            print(f"Error from Qwen API: {response.message}")
            return None
            
    except Exception as e:
        print(f"Error calling Qwen API: {e}")
        return None

def save_analysis_as_markdown(paper_filename, title, analysis, paper_type=None, output_folder="output"):
    """
    Save the analysis as a markdown file.
    """
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)
    
    # Create filename from paper filename
    base_name = Path(paper_filename).stem
    output_file = output_folder / f"{base_name}_analysis.md"
    
    # Create markdown content
    type_info = f"\n\n**Paper Type:** {paper_type.title()}" if paper_type else ""
    
    markdown_content = f"""# {title}

**Source:** {paper_filename}{type_info}

**Analysis Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}

---

{analysis}

---

*This analysis was generated automatically using Tongyi Qwen Plus.*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return output_file

def save_raw_introduction(paper_filename, introduction_text, output_folder="raw_intros"):
    """
    Save the extracted introduction text to raw_intros folder.
    """
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)
    
    base_name = Path(paper_filename).stem
    output_file = output_folder / f"{base_name}_intro.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(introduction_text)
    
    return output_file

def main():
    """
    Main function to process all papers.
    """
    # Load configuration
    config = load_config()
    
    # Check if API key is set
    if not os.getenv('DASHSCOPE_API_KEY'):
        print("Error: DASHSCOPE_API_KEY environment variable not set!")
        print("Please set your Tongyi Qwen API key:")
        print("export DASHSCOPE_API_KEY='your-api-key-here'")
        print("Or create a .env file: cp env_example.txt .env")
        return
    
    # Set up dashscope
    dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
    
    # Display configuration
    print("=== Configuration ===")
    print(f"Model: {config['llm_settings']['model']}")
    print(f"Temperature: {config['llm_settings']['temperature']}")
    print(f"Max tokens: {config['llm_settings']['max_tokens']}")
    print(f"Case sensitive matching: {config['extraction_settings']['case_sensitive']}")
    print(f"Fuzzy matching: {config['extraction_settings']['fuzzy_matching']}")
    print(f"Rate limit delay: {config['output_settings']['rate_limit_delay']}s")
    print()
    
    # Load annotation data
    annotations = load_annotation_file()
    if not annotations:
        return
    
    papers_folder = Path("papers_to_read")
    processed_count = 0
    failed_count = 0
    
    print(f"Processing {len(annotations)} papers...")
    
    for filename, data in tqdm(annotations.items(), desc="Processing papers"):
        if not data.get('start_of_intro') or not data.get('end_of_intro'):
            print(f"Skipping {filename}: start_of_intro or end_of_intro not filled")
            failed_count += 1
            continue
        
        # Validate paper type
        paper_type = data.get('type', '').lower()
        if not paper_type:
            print(f"Skipping {filename}: paper type not specified")
            failed_count += 1
            continue
        
        if paper_type not in ['theoretical', 'empirical']:
            print(f"Skipping {filename}: invalid paper type '{paper_type}'. Must be 'theoretical' or 'empirical'")
            failed_count += 1
            continue
        
        pdf_path = papers_folder / filename
        if not pdf_path.exists():
            print(f"Skipping {filename}: PDF file not found")
            failed_count += 1
            continue
        
        print(f"\nProcessing: {filename} (type: {paper_type})")
        
        # Extract introduction with config-based flexibility
        introduction = extract_introduction_from_pdf(
            pdf_path, 
            data['start_of_intro'], 
            data['end_of_intro'],
            config
        )
        
        if not introduction:
            print(f"Failed to extract introduction from {filename}")
            failed_count += 1
            continue
        
        # Save raw introduction if enabled in config
        if config['output_settings']['save_raw_intros']:
            raw_file = save_raw_introduction(filename, introduction)
            print(f"Saved raw introduction to: {raw_file}")
        
        # Analyze with Qwen using config
        print(f"Analyzing with Tongyi Qwen Plus using {paper_type} template...")
        analysis = analyze_with_qwen(introduction, data['title'], paper_type, config)
        
        if not analysis:
            print(f"Failed to analyze {filename}")
            failed_count += 1
            continue
        
        # Save analysis as markdown
        output_file = save_analysis_as_markdown(filename, data['title'], analysis, paper_type)
        print(f"Saved analysis to: {output_file}")
        
        processed_count += 1
        
        # Rate limiting from config
        rate_delay = config['output_settings']['rate_limit_delay']
        if rate_delay > 0:
            time.sleep(rate_delay)
    
    print(f"\n=== Processing Complete ===")
    print(f"Successfully processed: {processed_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(annotations)}")
    print(f"Configuration used: {config['llm_settings']['model']} (temp={config['llm_settings']['temperature']})")

if __name__ == "__main__":
    main() 