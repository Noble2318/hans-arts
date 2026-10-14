# Paste at the bottom of translations.py, next to the earlier NEW_KEYS block.
# Same assumption: TRANSLATIONS = {"en": {...}, "es": {...}, ...}

ABOUT_KEYS = {
    "en": {
        "about_materials": "Materials & technique",
        "about_inspiration": "Inspiration",
        "about_cta_title": "Interested in a painting?",
        "about_cta_text": "Browse the gallery or message the artist directly to ask about a piece, a commission or availability.",
    },
    "es": {
        "about_materials": "Materiales y técnica",
        "about_inspiration": "Inspiración",
        "about_cta_title": "¿Te interesa una pintura?",
        "about_cta_text": "Explora la galería o escribe directamente al artista para preguntar por una obra, un encargo o su disponibilidad.",
    },
    "fr": {
        "about_materials": "Matériaux et technique",
        "about_inspiration": "Inspiration",
        "about_cta_title": "Une peinture vous intéresse ?",
        "about_cta_text": "Parcourez la galerie ou écrivez directement à l'artiste pour vous renseigner sur une œuvre, une commande ou sa disponibilité.",
    },
    "sw": {
        "about_materials": "Vifaa na mbinu",
        "about_inspiration": "Chanzo cha msukumo",
        "about_cta_title": "Unavutiwa na mchoro?",
        "about_cta_text": "Tazama jumba la sanaa au mwandikie msanii moja kwa moja kuuliza kuhusu mchoro, kazi maalum au upatikanaji.",
    },
    "de": {
        "about_materials": "Materialien und Technik",
        "about_inspiration": "Inspiration",
        "about_cta_title": "Interesse an einem Gemälde?",
        "about_cta_text": "Stöbern Sie in der Galerie oder schreiben Sie dem Künstler direkt, um nach einem Werk, einer Auftragsarbeit oder der Verfügbarkeit zu fragen.",
    },
    "it": {
        "about_materials": "Materiali e tecnica",
        "about_inspiration": "Ispirazione",
        "about_cta_title": "Ti interessa un dipinto?",
        "about_cta_text": "Esplora la galleria o scrivi direttamente all'artista per informazioni su un'opera, una commissione o la disponibilità.",
    },
    "zh": {
        "about_materials": "材料与技法",
        "about_inspiration": "灵感来源",
        "about_cta_title": "对某幅画作感兴趣？",
        "about_cta_text": "浏览画廊，或直接联系艺术家，咨询作品、定制或是否有现货。",
    },
    "ar": {
        "about_materials": "الخامات والأسلوب",
        "about_inspiration": "مصدر الإلهام",
        "about_cta_title": "هل أعجبتك لوحة؟",
        "about_cta_text": "تصفّح المعرض أو راسل الفنان مباشرة للاستفسار عن لوحة أو طلب خاص أو مدى التوفر.",
    },
}

for lang, extra in ABOUT_KEYS.items():
    class TRANSLATIONS:
        ...

    TRANSLATIONS.setdefault(lang, {}).update(extra)