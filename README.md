# StudyMate AI - PDF Analysis Tool

An intelligent PDF analysis application that helps students and researchers extract valuable insights from their documents using AI.

## Features

- 📄 Extract text from PDF documents
- ✨ Generate summaries of PDF content
- 🌍 Translate text to multiple languages
- 🔍 Extract key topics and concepts
- ❓ Interactive Q&A about document content
- 📝 Generate practice tests from study material

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Hugging Face API key (free account required)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd replit
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Add your Hugging Face API key to the `.env` file
   ```
   HUGGINGFACE_API_KEY=your_api_key_here
   ```
   Get your API key from [Hugging Face](https://huggingface.co/settings/tokens)

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`

3. Upload a PDF file and choose from the available analysis options

## Project Structure

- `app.py` - Main Streamlit application
- `ai_services.py` - AI model integration and processing
- `pdf_processor.py` - PDF text extraction and processing
- `animations.py` - UI animations and styling
- `config.toml` - Application configuration

## Troubleshooting

- **API Key Issues**: Ensure your Hugging Face API key is correctly set in the `.env` file
- **PDF Extraction Problems**: Try with a different PDF file if text extraction fails
- **Performance Issues**: For large documents, processing may take some time

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Hugging Face](https://huggingface.co/) models
- Icons by [Material Icons](https://fonts.google.com/icons)
