from .translations import get_text

def language_context(request):
    lang = request.session.get('language', 'en')

    class T:
        def __getitem__(self, key):
            return get_text(lang, key)

    return {
        't': T(),
        'current_lang': lang,
        'available_languages': [('en', 'English'), ('es', 'Español'), ('fr', 'Français')],
    }