css = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

body {
    font-family: 'Inter', sans-serif;
    background-color: #0f111a;
}

.chat-message {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    border-radius: 16px;
    margin-bottom: 1rem;
    box-shadow: 0 6px 18px rgba(0,0,0,0.2);
    transition: transform 0.2s ease, background 0.3s ease;
    max-width: 85%;
    animation: fadeIn 0.4s ease-in;
}

.chat-message:hover {
    transform: scale(1.02);
    background-color: #22263b;
}

.chat-message.bot {
    background: linear-gradient(145deg, #3a4052, #2d3445);
}

.chat-message.user {
    background: linear-gradient(145deg, #1f232e, #14171f);
    flex-direction: row-reverse;
    margin-left: auto;
}

.chat-message .avatar {
    flex-shrink: 0;
}

.chat-message .avatar img {
    width: 58px;
    height: 58px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #ccc;
}

.chat-message .message {
    color: #f1f1f1;
    font-size: 1rem;
    line-height: 1.6;
    max-width: 80%;
    position: relative;
}

/* Typing animation */
.typing {
    display: flex;
    gap: 6px;
    height: 20px;
    margin-top: 8px;
}

.typing span {
    display: block;
    width: 8px;
    height: 8px;
    background: #ccc;
    border-radius: 50%;
    animation: blink 1.5s infinite;
}

.typing span:nth-child(2) {
    animation-delay: 0.2s;
}
.typing span:nth-child(3) {
    animation-delay: 0.4s;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes blink {
    0%, 80%, 100% { opacity: 0; transform: scale(0.8); }
    40% { opacity: 1; transform: scale(1.2); }
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://img.freepik.com/premium-photo/cute-mother-character-design-generative-ai_776674-593384.jpg?w=996" alt="Bot Avatar">
    </div>
    <div class="message">
        {{MSG}}
        <div class="typing">
            <span></span><span></span><span></span>
        </div>
    </div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://img.freepik.com/premium-vector/creative-pixel-characters-elements-vector-art-style_1301270-5874.jpg?w=826" alt="User Avatar">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''
