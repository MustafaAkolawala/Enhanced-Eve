from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import os
from flask_socketio import SocketIO, emit
from openai import OpenAI
from googleapiclient.discovery import build


####basic functions required

app = Flask(__name__)
socketio = SocketIO(app)
DEVELOPER_KEY = "AIzaSyDfMbEz564iDRRn-P8ZrkRHBq3MOGCvE6s"
youtube = build("youtube", "v3", developerKey=DEVELOPER_KEY)
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

#####################################################################################################################################
#                                   chatbot
history1 = [
    {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
    {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
]
@socketio.on('messages1')
def handle_message(message):
    history1.append({"role": "user", "content": message})
    
    completion = client.chat.completions.create(
        model="TheBloke/Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.Q4_K_S.gguf",
        messages=history1,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    for chunk in completion:
        if chunk.choices[0].delta.content:
            response = chunk.choices[0].delta.content
            new_message["content"] += response
            emit('response1', {'content': response})

    history1.append(new_message)



##################################################################################################################







# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Create 'uploads' folder if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path, output_text_file):
    pdf_document = fitz.open(pdf_path)
    extracted_text = ""

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        image = page.get_pixmap()
        image = Image.frombytes("RGB", [image.width, image.height], image.samples)
        image = image.convert("L")
        page_text = pytesseract.image_to_string(image)
        extracted_text += page_text + "\n\n"
    
    pdf_document.close()

    with open(output_text_file, 'w', encoding='utf-8') as f:
        f.write(extracted_text)
    history2.append({"role": "user", "content": extracted_text})         #historytrial1
    print(f'Extracted text saved to: {output_text_file}')
    return extracted_text


history2 = [
    {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers & you summerize the history appended to you."},
    {"role": "user", "content": "Hello, summerize any history appended to someone opening this program for the first time. Be concise."},
]

@socketio.on('messages2')
def handle_message(message):
    history2.append({"role": "user", "content": message})
    
    completion = client.chat.completions.create(
        model="TheBloke/Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.Q4_K_S.gguf",
        messages=history2,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    for chunk in completion:
        if chunk.choices[0].delta.content:
            response = chunk.choices[0].delta.content
            new_message["content"] += response
            emit('response2', {'content': response})

    history2.append(new_message)
    
    









@app.route('/pdfSavior/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        if filename.lower().endswith('.pdf'):
            output_text_file = os.path.splitext(file_path)[0] + '.txt'
            extracted_text = extract_text_from_pdf(file_path, output_text_file)
            return redirect(url_for('display_text', filename=output_text_file))
        else:
            # Handle image file
            # You can add image processing and text extraction here
            # For now, just redirect to the uploaded file
            return redirect(url_for('display_file', filename=filename))

@app.route('/pdfSavior/display_text/<filename>')
def display_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    return render_template('display_text.html', text=text)

@app.route('/pdfSavior/display_file/<filename>')
def display_file(filename):
    return render_template('display_file.html', filename=filename)






########################################################################################################################





history3 = [
    {"role": "system", "content": "Welcome! I'm here to help you with any questions you have."},
    {"role": "system", "content": "As an intelligent assistant, I can provide detailed explanations and even recommend YouTubers to search for specific topics."},
    {"role": "system", "content": "Feel free to ask me anything, and I'll do my best to assist you!"},
    {"role": "user", "content": "Can you explain how artificial neural networks work?"},
    {"role": "assistant", "content": "Of course! Artificial neural networks (ANNs) are computational models inspired by the structure and function of biological neural networks in the human brain."},
    {"role": "assistant", "content": "ANNs consist of interconnected nodes, called neurons, organized in layers."},
    {"role": "assistant", "content": "Each neuron receives input signals, performs a computation, and passes the result to the next layer of neurons."},
    {"role": "assistant", "content": "Through a process called training, ANNs can learn to recognize patterns and relationships in data, making them useful for tasks like image recognition, natural language processing, and more."},
    {"role": "assistant", "content": "To learn more about artificial neural networks, I recommend checking out YouTube channels like '3Blue1Brown' and 'sentdex' for informative tutorials and explanations."},
    {"role": "user", "content": "Thank you! Can you also recommend a good book on machine learning?"},
    {"role": "assistant", "content": "Absolutely! One highly recommended book on machine learning is 'Pattern Recognition and Machine Learning' by Christopher M. Bishop."},
    {"role": "assistant", "content": "This book covers a wide range of topics in machine learning, including supervised and unsupervised learning, probabilistic models, and more."},
    {"role": "assistant", "content": "It provides clear explanations and examples, making it suitable for both beginners and experienced practitioners."},
    {"role": "assistant", "content": "For more recommendations and insights on machine learning books, I suggest exploring book review channels on YouTube like 'CodeEmporium' and 'The AI Book Club'."},
    {"role": "user", "content": "Great! Thanks for the recommendations."},
    {"role": "system", "content": "You're welcome! If you have any more questions or need further assistance, feel free to ask."},
]


def get_youtube_video_links(search_query, max_results=5):
    try:
        # Set search parameters
        request = youtube.search().list(
            part="snippet",
            q=search_query,
            type="video",
            maxResults=max_results
        )

        # Execute the search request
        response = request.execute()

        # Extract video links, titles, and thumbnails from the response
        videos_info = []
        if response.get("items", []):
            for item in response["items"]:
                video_id = item["id"]["videoId"]
                video_link = f"https://www.youtube.com/watch?v={video_id}"
                thumbnail_url = item["snippet"]["thumbnails"]["medium"]["url"]  # Using medium size thumbnail
                title = item["snippet"]["title"]
                videos_info.append({"video_link": video_link, "thumbnail_url": thumbnail_url, "title": title})

        return videos_info

    except Exception as e:
        print(f"Error fetching YouTube video links: {e}")
        return []






@socketio.on('search')
def search(query):
    search_query = query['search_query']
    max_results = int(query['max_results'])

    # Retrieve YouTube video links, titles, and thumbnails based on user input
    videos_info = get_youtube_video_links(search_query, max_results)

    # Emit the search results to the client
    socketio.emit('youtube_result', {'search_query': search_query, 'videos_info': videos_info})







@socketio.on('messages3')
def handle_message(message):
    history3.append({"role": "user", "content": message})
    
    completion = client.chat.completions.create(
        model="TheBloke/Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.Q4_K_S.gguf",
        messages=history3,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    for chunk in completion:
        if chunk.choices[0].delta.content:
            response = chunk.choices[0].delta.content
            new_message["content"] += response
            emit('openai_response', {'content': response})

    history3.append(new_message)

    # print(new_message)


















################################################################################################################################
# Landing page with buttons
@app.route('/')
def index():
    return render_template('index.html')

# Page 1 - Chat Assistant
@app.route('/chatAssistant')
def chatAssistant():
    return render_template('chat_assistant.html')

# Page 2 - YouTube Aider
@app.route('/youtubeAider')
def youtubeAider():
    return render_template('youtube_aider.html')

# Page 3 - PDF Savior
@app.route('/pdfSavior')
def pdfSavior():
    return render_template('pdf_savior.html')

if __name__ == '__main__':
    app.run(debug=True)
