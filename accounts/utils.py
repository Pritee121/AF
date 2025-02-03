from googletrans import Translator

def translate_text(text, target_language="ne"):
    """
    Translate text using Google Translate API.
    """
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text
