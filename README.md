# Economic Paper Introduction Analyzer

An automated system to extract and analyze key information from economic research papers using LLMs. This tool focuses on the introduction sections of papers to identify research problems, significance, findings, and methodological contributions.

## Features

- 📄 **PDF Processing**: Extracts introduction sections from economic papers
- 🤖 **AI Analysis**: Uses Tongyi Qwen Plus to analyze and structure key information
- 📁 **Organized Workflow**: Structured folder system for input, processing, and output
- 🎯 **Human-in-the-Loop**: Manual annotation of introduction boundaries for accuracy
- 📊 **Paper Type Classification**: Distinguishes between theoretical and empirical papers with tailored analysis
- 📝 **Markdown Output**: Clean, structured analysis in markdown format
- 🔧 **Flexible Configuration**: Customizable LLM parameters and extraction settings
- 🔍 **Smart Extraction**: Fuzzy matching and case-insensitive search for robust text extraction
- ⚙️ **Interactive Config Editor**: Easy-to-use configuration management

## Folder Structure

```
intro_reader/
├── papers_to_read/     # Place your PDF files here
├── raw_intros/         # Extracted introduction text (auto-generated)
├── output/             # Final markdown analyses (auto-generated)
├── step1_generate_json.py
├── step2_extract_and_analyze.py
├── requirements.txt
└── README.md
```

## Setup

### 1. Install Dependencies

Using conda (recommended):
```bash
conda create -n intro_reader python=3.9
conda activate intro_reader
pip install -r requirements.txt
```

Using pip:
```bash
pip install -r requirements.txt
```

### 2. Get Tongyi Qwen API Key

1. Visit [Alibaba Cloud Model Studio](https://dashscope.console.aliyun.com/)
2. Log in and navigate to API-KEY section
3. Create a new API key
4. Set the environment variable:

**Method 1: Using .env file (Recommended)**
```bash
# Copy the example file and edit it
cp env_example.txt .env
# Then edit .env and replace "your-tongyi-qwen-api-key-here" with your actual key
```

**Method 2: Environment variable**
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your-api-key-here"

# Linux/Mac
export DASHSCOPE_API_KEY="your-api-key-here"
```

## Usage

### Step 1: Generate Annotation File

1. Place your PDF files in the `papers_to_read/` folder
2. Run the first script:

```bash
python step1_generate_json.py
```

This creates `papers_annotation.json` with the following structure:
```json
{
  "paper1.pdf": {
    "title": "Extracted Paper Title",
    "type": "",
    "start_of_intro": "",
    "end_of_intro": "",
    "notes": ""
  }
}
```

### Step 2: Manual Annotation

Open `papers_annotation.json` and fill in the following fields for each paper:

1. **Paper Type**: Specify either `"theoretical"` or `"empirical"`
2. **Introduction Boundaries**: Set `start_of_intro` and `end_of_intro` markers

**Examples:**

**Theoretical Paper:**
```json
{
  "type": "theoretical",
  "start_of_intro": "1. Introduction",
  "end_of_intro": "2. The Model"
}
```

**Empirical Paper:**
```json
{
  "type": "empirical",
  "start_of_intro": "Introduction",
  "end_of_intro": "Data and Methodology"
}
```

**Tips:**
- **Paper Type**: Choose based on the paper's primary contribution
  - `"theoretical"`: Papers that develop models, theory, or conceptual frameworks
  - `"empirical"`: Papers that analyze data, conduct experiments, or test hypotheses
- **Boundary Markers**: Use exact text that appears in the PDF
- Include section numbers if present
- Be specific to avoid false matches

### Step 3: Extract and Analyze

Run the second script:

```bash
python step2_extract_and_analyze.py
```

This will:
1. Extract introduction sections based on your annotations (with flexible matching)
2. Save raw text to `raw_intros/` folder
3. Analyze each introduction with Tongyi Qwen Plus using your config settings
4. Generate structured markdown files in `output/` folder

## Configuration

### Customize Settings

Edit LLM parameters, extraction behavior, and output options:

Please edit `config.json` directly.

### Key Configuration Options

**Analysis Templates:**
- **theoretical**: Prompt template optimized for theoretical papers (models, theory, concepts)
- **empirical**: Prompt template optimized for empirical papers (data, identification, methodology)

**Extraction Settings:**
- **fuzzy_matching**: Enables approximate text matching when exact markers aren't found
- **case_sensitive**: Controls case sensitivity for marker detection
- **search_flexibility**: Tries multiple strategies to find introduction boundaries

**LLM Settings:**
- **temperature**: Controls AI response randomness (0 = deterministic)
- **max_tokens**: Maximum length of AI analysis
- **rate_limit_delay**: Delay between API calls to avoid limits

## Output Format

The analysis structure adapts based on paper type:

### Theoretical Papers

**Research Problem**: What specific question does this paper address?

**Significance & Motivation**: Why is this problem important? How does it connect to and differ from existing works?

**Main Findings & Intuition**: What is the paper's answer? What's the key intuition or mechanism?

**Model Setup & Assumptions**: What is the basic model structure and key assumptions?

**Methodological Contributions**: What are the key methodological innovations?

**Policy Implications**: What are the policy recommendations?

**Key Insights**: Additional important takeaways

### Empirical Papers

**Research Question**: What empirical question does this paper investigate?

**Significance & Motivation**: Why is this problem important? How does it connect to and differ from existing works?

**Main Findings**: What are the main empirical results?

**Data**: What data sources, sample period, and key variables are used?

**Identification Strategy**: How does the paper establish causal identification?

**Robustness & Limitations**: What robustness checks and limitations are mentioned?

**Policy Implications**: What are the policy recommendations?

## Example Workflow

1. **Prepare papers**: Copy 5 economic papers to `papers_to_read/`
2. **Generate template**: `python step1_generate_json.py`
3. **Annotate manually**: Edit `papers_annotation.json`
   - Set paper type (`"theoretical"` or `"empirical"`)
   - Define introduction boundaries (`start_of_intro`, `end_of_intro`)
4. **Process and analyze**: `python step2_extract_and_analyze.py`
5. **Review results**: Check `output/` folder for tailored markdown analyses

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `DASHSCOPE_API_KEY` is set correctly
   - Verify your API key is valid and has sufficient quota

2. **PDF Extraction Issues**
   - Check if PDFs are not password-protected
   - Ensure PDFs contain searchable text (not just images)

3. **Paper Type Issues**
   - Ensure each paper has `"type"` set to either `"theoretical"` or `"empirical"`
   - Check for typos in paper type values
   - Papers with missing or invalid types will be skipped

4. **Marker Not Found**
   - Double-check your start/end markers in the annotation file
   - Use exact text from the PDF, including capitalization

5. **Rate Limiting**
   - The script includes automatic delays between API calls
   - If you hit limits, wait and try again

### Getting Help

- Check the console output for detailed error messages
- Verify your PDF files are readable
- Ensure your annotation markers match the PDF text exactly

## Cost Considerations

- Tongyi Qwen Plus charges per API call
- Each paper introduction analysis costs approximately 0.01-0.05 yuan
- Monitor your usage in the Alibaba Cloud console

## License

This project is licensed under the MIT Non-Commercial License - see the [LICENSE](LICENSE) file for details.

**Key Points:**
- ✅ Free for personal, academic, and educational use
- ✅ Modify, distribute, and share freely
- ❌ Commercial use is prohibited
- ❌ Cannot be used to generate revenue or profit

For commercial licensing inquiries, please contact the project maintainers.

Please ensure you have the right to process the PDF files you're analyzing. 
