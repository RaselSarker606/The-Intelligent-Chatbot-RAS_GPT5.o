from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import os

# Set your API key for Google Generative AI
os.environ["GOOGLE_API_KEY"] = "AIzaSyAhhYlDosHx2ruW-I2ZRQn3tG1uI2vOdZo"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

#Initialize the model
model = genai.GenerativeModel("models/gemini-1.5-pro")

app = Flask(__name__)

#===========================================================================
# Store chats in memory
chats = [{'name': 'New Chat', 'id':1, 'messages': []}]

def Generate_Content(prompt, chat_history=None):

    if chat_history:
        context = "\n".join(
            [f"user: {msg['text']}" if msg['text'].startswith('user') else f"AI: {msg['text']}" for msg in chat_history])
        prompt = f"{context}\nuser: {prompt}\nAI:"

    response = model.generate_content(prompt)

    return response.text
#==========================================================================


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_chats', methods=['GET'])
def get_chats():
    return jsonify({'chats': chats})


@app.route("/get_chat_history", methods=['GET'])
def get_chat_history():
    chat_id = int(request.args.get('chat_id'))
    chat = next((chat for chat in chats if chat['id']==chat_id),None)
    if chat:
        return jsonify({'messages': chat['messages']})
    return jsonify({'messages':[]})


# Route to delete a chat
@app.route('/delete_chat', methods = ['POST'])
def delete_chat():
    data = request.get_json()
    chat_id = data.get('chat_id')
    global chats
    chats = [k for k in chats if k['id'] != chat_id]
    return jsonify({'status': f'Chat {chat_id} deleted successfully'})


# Route to create a new chat
@app.route('/new_chat', methods = ['POST'])
def new_chat():
    data = request.get_json()
    chat_name = data.get('chat_name')
    new_chat_id = len(chats) + 1
    new_chat = {'name': chat_name, 'id': new_chat_id, 'messages': []}
    chats.append(new_chat)
    return jsonify({'status': 'Chat created successfully', 'chat_id': new_chat_id})
#==========================================================================
@app.route('/generate', methods = ['POST'])
def generate():
    data = request.get_json()
    user_input = data.get('input')
    chat_id = data.get('chat_id')

    # Find the relevant chat and get the chat history
    chat = next((chat for chat in chats if chat['id'] == chat_id), None)
    chat_history = chat['messages'] if chat else []

    # Generate the AI response with context
    response = Generate_Content(user_input, chat_history)

    # Append user input and AI response to the chat history
    if chat:
        chat['messages'].append({'text': f'user: {user_input}'})
        chat['messages'].append({'text': f'AI: {user_input}'})

    return jsonify({'response': response})

#==========================================================================


if __name__ == '__main__':
    app.run(debug=True)