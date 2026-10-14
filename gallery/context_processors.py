from .translations import get_text

AVAILABLE_LANGUAGES = (
    ('en', 'English'),
    ('es', 'Español'),
    ('fr', 'Français'),
    ('sw', 'Kiswahili'),
    ('de', 'Deutsch'),
    ('it', 'Italiano'),
    ('zh', '中文'),
    ('ar', 'العربية'),
)


def language_context(request):
    lang = request.session.get('language', 'en')
    if lang not in {code for code, _ in AVAILABLE_LANGUAGES}:
        lang = 'en'

    class T:
        def __getitem__(self, key):
            return get_text(lang, key)

    return {
        't': T(),
        'current_lang': lang,
        'available_languages': AVAILABLE_LANGUAGES,
    }
