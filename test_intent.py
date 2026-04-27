import sys
from src.chat_controller import IntentRouter, ChatController, Mode

controller = ChatController()
mode = controller.router.route("analyse this text 'he is a gay'")
print("MODE IS:", mode)

bert = controller.bert_module.classify_text("he is a gay")
print("BERT:", bert)
