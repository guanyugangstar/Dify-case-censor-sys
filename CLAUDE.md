# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Flask-based document/contract review system that integrates with Dify API for AI-powered document analysis. The system allows users to upload files, select review type (document review/contract review), specify contracting party (for contracts), and get AI-generated review results displayed in real-time.

## Key Components
1. **Backend**: Flask application (app.py) handling file uploads, Dify API integration, and streaming responses
2. **Frontend**: Single HTML page (templates/index.html) with modern UI and JavaScript for handling form submission and streaming results
3. **Dify Integration**: Connects to Dify API for document processing and AI review

## Development Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python app.py
```

Or use the startup script:
```bash
startup.bat
```

### Environment Configuration
Set the Dify API token as an environment variable:
- Windows: `$env:DIFY_API_TOKEN="your-token"`
- Linux/macOS: `export DIFY_API_TOKEN="your-token"`

## Code Architecture

### Backend (app.py)
- Flask routes for serving the main page, handling uploads, and streaming chat responses
- File type detection and mapping to Dify-compatible formats
- Dify API integration for file upload and chat message processing
- Streaming response handling for real-time AI output

### Frontend (templates/index.html)
- Responsive UI with Apple-style design
- Form handling for review type and file upload
- JavaScript for streaming response processing
- Result display with truncated content and modal for full view
- Markdown rendering support

### Key Features
- Real-time streaming of AI responses
- Support for multiple file types (documents, images, audio, video)
- Separated display for primary review and secondary review results
- Responsive design for mobile compatibility
- Error handling and user feedback

## Important Implementation Details
- Files are temporarily saved during upload process and deleted after Dify processing
- Results are not persisted - stored only in memory during session
- Uses Server-Sent Events (SSE) for streaming AI responses to frontend
- Frontend processes Dify streaming responses and displays content in real-time