import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file, url_for
from gtts import gTTS
from werkzeug.utils import secure_filename
import time
import re
import base64
import io

# Add googletrans import
from deep_translator import GoogleTranslator
import pyttsx3
import docx
from PyPDF2 import PdfReader


app = Flask(__name__, template_folder='../static')
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_language(text):
    """Detect the language of the input text"""
    try:
        return GoogleTranslator().detect(text)[0]
    except Exception:
        return 'en'  # Default to English if detection fails

def translate_text(text, target_language):
    """Translate text to target language"""
    try:
        if target_language == 'en' or not text.strip():
            return text  # No translation needed for English

        # Heuristic to protect proper nouns (like names) from being translated.
        # We assume capitalized words are names and should not be translated.
        words = text.split(' ')
        placeholders = {}
        processed_words = []
        
        for i, word in enumerate(words):
            # A simple check for a proper noun: is it capitalized?
            if word.istitle():
                placeholder = f"__NAME{len(placeholders)}__"
                placeholders[placeholder] = word
                processed_words.append(placeholder)
            else:
                processed_words.append(word)
        
        text_with_placeholders = ' '.join(processed_words)

        # Translate the text with placeholders
        translated_text = GoogleTranslator(source='auto', target=target_language).translate(text_with_placeholders)

        # Replace placeholders with the original names
        for placeholder, original_word in placeholders.items():
            translated_text = translated_text.replace(placeholder, original_word, 1)

        return translated_text

    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    """Convert text to speech"""
    try:
        # Get form data
        text_input = request.form.get('text_input', '').strip()
        language = request.form.get('language', 'en')
        speed = request.form.get('speed', 'normal')
        voice = request.form.get('voice', 'neural')
        file = request.files.get('file')
        
        # Language mapping for gTTS
        language_map = {
            'en': 'en',      # English
            'hi': 'hi',      # Hindi
            'gu': 'gu',      # Gujarati
            'mr': 'mr'       # Marathi
        }
        
        # Validate language
        if language not in language_map:
            return jsonify({'error': f'Unsupported language: {language}. Supported languages: English, Hindi, Gujarati, Marathi'}), 400
        
        # Get the gTTS language code
        gtts_lang = language_map[language]
        
        # Get text from file or input
        text_content = ''
        if file and file.filename != '' and allowed_file(file.filename):
            try:
                extension = file.filename.rsplit('.', 1)[1].lower()
                if extension == 'txt':
                    text_content = file.read().decode('utf-8').strip()
                elif extension == 'pdf':
                    pdf_reader = PdfReader(file)
                    text_content = ""
                    for page in pdf_reader.pages:
                        text_content += page.extract_text()
                elif extension == 'docx':
                    doc = docx.Document(file)
                    text_content = "\n".join([para.text for para in doc.paragraphs])

            except Exception as e:
                return jsonify({'error': f'Error reading file content: {str(e)}'}), 400
                
        elif text_input:
            text_content = text_input
        else:
            return jsonify({'error': 'Please provide text input or upload a valid .txt file'}), 400
        
        # Validate text content
        if not text_content:
            return jsonify({'error': 'No text content found to convert'}), 400
        
        if len(text_content) > 5000:
            return jsonify({'error': 'Text is too long. Please limit to 5000 characters.'}), 400
        
        # Translate text to target language
        original_text = text_content
        translated_text = translate_text(text_content, language)
        
        # Check if translation occurred
        translation_occurred = (original_text != translated_text and language != 'en')
        
        # Convert text to speech
        try:
            # Determine if slow speech should be used
            use_slow = False
            if speed == 'slow':
                use_slow = True
            elif speed == 'fast':
                # For fast speech, we'll use normal speed but with shorter pauses
                translated_text = translated_text.replace('...', '.').replace('..', '.')

            # Voice type affects the text preprocessing
            if voice == 'expressive':
                # Add emphasis for expressive voice
                translated_text = translated_text.replace('!', '!!').replace('?', '??')
            elif voice == 'calm':
                # Add more pauses for calm voice
                translated_text = translated_text.replace(',', ', ... ').replace(';', '; ... ')
            elif voice == 'premium':
                # Clean up text for premium voice
                translated_text = ' '.join(translated_text.split())  # Clean extra spaces
            
            tts = gTTS(
                text=translated_text, 
                lang=gtts_lang, 
                slow=use_slow,
                lang_check=True
            )
            
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)

            audio_buffer.seek(0)
            
            # Convert to base64 for sending to frontend
            audio_data = base64.b64encode(audio_buffer.read()).decode('utf-8')
            
            # Create response message based on selections
            voice_names = {
                'neural': 'Neural',
                'premium': 'Premium', 
                'expressive': 'Expressive',
                'calm': 'Calm'
            }
            
            language_names = {
                'en': 'English',
                'hi': 'Hindi', 
                'gu': 'Gujarati',
                'mr': 'Marathi'
            }
            
            speed_names = {
                'slow': 'Slow',
                'normal': 'Normal',
                'fast': 'Fast'
            }
            
            # Create detailed message
            if translation_occurred:
                message = f'Text translated to {language_names.get(language, language)} and converted to speech! Voice: {voice_names.get(voice, voice)}, Speed: {speed_names.get(speed, speed)}'
            else:
                message = f'Text converted to speech successfully! Voice: {voice_names.get(voice, voice)}, Language: {language_names.get(language, language)}, Speed: {speed_names.get(speed, speed)}'
            
        except Exception as e:
            return jsonify({'error': f'Error generating speech: {str(e)}. Please check if the selected language is supported.'}), 500
        
        # Return success response with base64 audio data
        return jsonify({
            'success': True,
            'audio_data': audio_data,
            'message': message,
            'voice': voice,
            'language': language,
            'speed': speed,
            'translation_occurred': translation_occurred,
            'original_text': original_text if translation_occurred else None,
            'translated_text': translated_text if translation_occurred else None
        })
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/download', methods=['POST'])
def download_audio():
    """Download audio file from base64 data"""
    try:
        audio_data = request.json.get('audio_data')
        if not audio_data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data)
        
        # Create a BytesIO object for the audio data
        audio_buffer = io.BytesIO(audio_bytes)
        audio_buffer.seek(0)
        
        # Generate filename
        filename = f"tts_audio_{int(time.time())}.mp3"
        
        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Error downloading audio: {str(e)}'}), 500

if __name__ == '__main__':
     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))