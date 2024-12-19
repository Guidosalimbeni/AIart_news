# AI Art Newsletter Generator

An automated system that generates curated newsletters about AI art, keeping you updated with the latest developments, exhibitions, and discussions in the field of artificial intelligence and creative expression.

## Features

- Automated newsletter generation
- Content curation from multiple sources
- Markdown-formatted output
- Configurable search parameters
- Environment-based configuration

## Requirements

- Python 3.x
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following API keys:
   ```
   ANTHROPIC_API_KEY=your_key_here
   BRAVE_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```

## Usage

1. Ensure all environment variables are set
2. Run the tests to verify setup:
   ```bash
   python test_setup.py
   ```
3. Generate a newsletter:
   ```bash
   python test_newsletter.py
   ```
4. Find the generated newsletter in the `outputs` directory

## Project Structure

- `app/`: Main application code
  - `core/`: Core configurations and settings
  - `services/`: Service implementations
- `outputs/`: Generated newsletter files
- `test_newsletter.py`: Newsletter generation script
- `test_setup.py`: Setup verification script

## Output Format

The newsletter is generated in Markdown format and includes:
- Latest AI art news and developments
- Exhibition information
- Industry updates
- Important dates and events

Last updated: December 19, 2024
