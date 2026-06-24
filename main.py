import pygame
import random
import re
import os
from gemini import Client

# Initialize Pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up fonts
font = pygame.font.Font(None, 24)

class ChatBot:
    def __init__(self, width, height):
        self.chat_history = []

        self.talking_mode = True
        self.annoying_mode = False
        self.listening_mode = False

        self.patterns = [
            (r'hi|hello|hey', ["hello", "hey there", "hi"]),
            (r'how are you?', ["I'm great, how are you?", "I am doing well, thanks for asking", "I'm fine, how are you?"]),
            (r'what is your name/?', ["My creator named me Dodo. What's your name?"]),
            (r'what can you do/?', ["I can chat with you", "I can help you with some Gemini API calls"]),
            (r'quit|bye|I\'m leaving', ["Goodbye!", "See you later", "bye"]),
            (r'okay|ok|got it', ["Good", "Thank you", "I appreciate it"]),
            (r'thank you|thanks|thanks a lot', ["You're welcome ;)"]),
            (r'fine|well|doing amazing', ["Happy to hear that. What can I do for you?"])
        ]
        self.banned_words = ['shit', 'bullshit', 'crap']
        self.annoying_words = ['hate you', 'annoying', 'shut up']
        self.attention_words = ['talk to you', 'listen to me', 'tell you something']

        # Text input box
        self.user_input = ""
        self.input_rect = pygame.Rect(20, height - 40, width - 40, 20)

        # Scroll offset
        self.scroll_offset = 0
        self.line_height = 30

        # Gemini API credentials (store securely outside code)
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.gemini_api_secret = os.environ.get('GEMINI_API_SECRET')

        # Initialize Gemini API Client
        self.gemini_client = Client(self.gemini_api_key, self.gemini_api_secret)

    def submit(self, user_message):
        response = self.respond(user_message)
        self.chat_history.append(("You:", user_message))
        if response is not None:
            self.chat_history.append(("Bot:", response))

    def respond(self, user_input):
        match = re.search(r'my name is (\w+)', user_input.lower())
        if match:
            name = match.group(1)
            return "Hi, " + name.capitalize() + ". How can I help you today?"

        if self.talking_mode:
            for pattern, responses in self.patterns:
                if re.search(pattern, user_input.lower()):
                    return random.choice(responses)
            for word1 in self.banned_words:
                if word1 in user_input.lower():
                    self.talking_mode = False
                    self.annoying_mode = False
                    self.listening_mode = False
                    return "I do not talk to people who use this kind of language."
            for word2 in self.annoying_words:
                if word2 in user_input.lower():
                    self.annoying_mode = True
                    self.talking_mode = False
                    self.listening_mode = False
                    return "That's no way to talk to someone"
            for word3 in self.attention_words:
                if word3 in user_input.lower():
                    self.annoying_mode = False
                    self.talking_mode = False
                    self.listening_mode = True
                    return "Sure go ahead I'm listening."
            # If no pattern matched, use Gemini API
            return self.get_ai_response(user_input)
        elif self.listening_mode:
            c = ["Mhm", "Okay"]
            q = ["Have you thought about talking to a close friend?\n"
                 "Try talking to someone you can rely on and share everything with them.\n"
                 "Maybe that would make you feel better."]
            if "what" in user_input.lower() and "do" in user_input.lower() and "?" in user_input.lower():
                return random.choice(q)
            elif "okay" in user_input.lower() or "ok" in user_input.lower() or "k" in user_input.lower():
                self.listening_mode = False
                self.talking_mode = True
                self.annoying_mode = False
                return "Happy to help"
            elif user_input.lower() != "":
                return random.choice(c)
            else:
                return ""
        else:
            if "sorry" in user_input.lower():
                self.listening_mode = False
                self.talking_mode = True
                self.annoying_mode = False
                return "It's okay"
            elif self.annoying_mode:
                return user_input
            else:
                return ""

    def get_ai_response(self, user_input):
        try:
            response = self.gemini_client.completion.create(
                engine="text-davinci-003",  # Use the appropriate engine for your API
                prompt=user_input,
                max_tokens=50
            )
            return response.choices[0].text.strip()
        except Exception as e:
            return f"I'm sorry, I couldn't get a response from the AI API. Error: {e}"

    def draw_chat(self, screen):
        y = 20 - self.scroll_offset
        for line in self.chat_history:
            text_surface = font.render(line[0] + " " + line[1], True, WHITE)
            screen.blit(text_surface, (20, y))
            y += self.line_height

        # Draw text input box
        pygame.draw.rect(screen, WHITE, self.input_rect, 1)
        text_surface = font.render(self.user_input, True, WHITE)
        screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))

    def handle_scroll(self, event):
        if event.button == 4:  # Scroll up
            self.scroll_offset = max(self.scroll_offset - self.line_height, 0)
        elif event.button == 5:  # Scroll down
            max_offset = max(0, len(self.chat_history) * self.line_height - (self.input_rect.y - 20))
            self.scroll_offset = min(self.scroll_offset + self.line_height, max_offset)

# Main function
def main():
    # Set up the screen
    screen_width, screen_height = 400, 500
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Basic Chatbot")

    # Create a ChatBot instance
    chatbot = ChatBot(screen_width, screen_height)

    # Main loop
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    chatbot.submit(chatbot.user_input)
                    chatbot.user_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    chatbot.user_input = chatbot.user_input[:-1]
                else:
                    chatbot.user_input += event.unicode
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.size
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                chatbot = ChatBot(screen_width, screen_height)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                chatbot.handle_scroll(event)

        screen.fill(BLACK)
        chatbot.draw_chat(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
