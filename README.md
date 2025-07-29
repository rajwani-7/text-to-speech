# Text-to-Speech Converter

A modern web application that converts text to speech using Google's gTTS service. Features multiple voice types, languages, and a beautiful responsive UI.

## Features

- **Multi-language Support**: English, Hindi, Gujarati, Marathi
- **Multiple Voice Types**: Neural, Premium, Expressive, Calm
- **Speed Control**: Slow, Normal, Fast
- **File Upload**: Support for .txt files
- **Real-time Audio**: Play generated speech in browser
- **Download**: Save audio as MP3 files
- **Responsive Design**: Works on mobile and desktop

## Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Access the app**: Open http://localhost:5000

## Deployment on Vercel

### Prerequisites
- Vercel account
- Git repository with your code

### Steps

1. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

2. **Deploy using Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your Git repository
   - Vercel will automatically detect it's a Python project

3. **Or deploy using CLI**:
   ```bash
   vercel
   ```

### Configuration Files

The project includes:
- `vercel.json`: Vercel configuration
- `requirements.txt`: Python dependencies
- `app.py`: Main Flask application

### Important Notes for Vercel

- **Serverless Environment**: The app has been modified to work without file system storage
- **Audio Handling**: Audio is converted to base64 and sent to the frontend
- **No Background Tasks**: File cleanup is not needed in serverless environment
- **Function Timeout**: Set to 30 seconds (configurable in vercel.json)

## API Endpoints

- `GET /`: Main application page
- `POST /convert`: Convert text to speech
- `POST /download`: Download audio file

## Technologies Used

- **Backend**: Flask (Python)
- **TTS Engine**: Google gTTS
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Deployment**: Vercel

## Limitations

- **Translation**: Currently simplified (no external translation service)
- **File Storage**: No persistent file storage (serverless)
- **Audio Size**: Limited by Vercel's function timeout

## Contributing

Feel free to submit issues and enhancement requests!

## License

Developed by Harsh Rajwani • All Rights Reserved 2025 