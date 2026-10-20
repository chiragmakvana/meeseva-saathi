"""Citizen-facing sentences the server writes, in English, Telugu, Hindi and Urdu.

Translations are first drafts for the prototype and should be reviewed by native speakers
before any production use.
"""

APPLY_INTRO = {
    "en": "You can apply for {name} at any MeeSeva centre or on the MeeSeva portal. Keep these documents ready:",
    "te": "{name} కోసం మీరు ఏదైనా మీసేవ కేంద్రంలో లేదా మీసేవ పోర్టల్‌లో దరఖాస్తు చేయవచ్చు. ఈ పత్రాలను సిద్ధంగా ఉంచుకోండి:",
    "hi": "आप {name} के लिए किसी भी मीसेवा केंद्र पर या मीसेवा पोर्टल पर आवेदन कर सकते हैं। ये दस्तावेज़ तैयार रखें:",
    "ur": "آپ {name} کے لیے کسی بھی می سیوا مرکز پر یا می سیوا پورٹل پر درخواست دے سکتے ہیں۔ یہ دستاویزات تیار رکھیں:",
}

FEE_TIME = {
    "en": "Fee: ₹{fee} · Usually ready in {days} working days (sample data, confirm at the centre).",
    "te": "రుసుము: ₹{fee} · సాధారణంగా {days} పని దినాల్లో సిద్ధమవుతుంది (నమూనా సమాచారం, కేంద్రంలో నిర్ధారించుకోండి).",
    "hi": "शुल्क: ₹{fee} · आमतौर पर {days} कार्य दिवसों में तैयार (नमूना जानकारी, केंद्र पर पुष्टि करें)।",
    "ur": "فیس: ₹{fee} · عام طور پر {days} کام کے دنوں میں تیار (نمونہ معلومات، مرکز پر تصدیق کریں)۔",
}

NOT_FOUND = {
    "en": "Sorry, I could not find the right service. Tell me what you need, for example 'income certificate', or choose one below.",
    "te": "క్షమించండి, సరైన సేవ దొరకలేదు. మీకు ఏమి కావాలో చెప్పండి, ఉదాహరణకు 'ఆదాయ ధృవీకరణ పత్రం', లేదా క్రింద ఒకటి ఎంచుకోండి.",
    "hi": "क्षमा करें, सही सेवा नहीं मिली। बताइए आपको क्या चाहिए, जैसे 'आय प्रमाण पत्र', या नीचे से कोई सेवा चुनें।",
    "ur": "معاف کیجیے، درست سروس نہیں ملی۔ بتائیے آپ کو کیا چاہیے، جیسے 'آمدنی سرٹیفکیٹ'، یا نیچے سے کوئی سروس منتخب کریں۔",
}

NEXT_STEP = {
    "en": "Press 'Start application' to save a checklist, or 'Nearest centre' to find a MeeSeva centre.",
    "te": "చెక్‌లిస్ట్ సేవ్ చేయడానికి 'దరఖాస్తు ప్రారంభించండి' నొక్కండి, లేదా మీసేవ కేంద్రం కోసం 'సమీప కేంద్రం' నొక్కండి.",
    "hi": "चेकलिस्ट सहेजने के लिए 'आवेदन शुरू करें' दबाएँ, या मीसेवा केंद्र खोजने के लिए 'नज़दीकी केंद्र' दबाएँ।",
    "ur": "چیک لسٹ محفوظ کرنے کے لیے 'درخواست شروع کریں' دبائیں، یا می سیوا مرکز کے لیے 'قریبی مرکز' دبائیں۔",
}

# Plain-language status explanations: (what it means, what to do next).
STATUS = {
    "draft": {
        "en": ("Your application is saved but not submitted yet.", "Tick each document you have, then press Submit."),
        "te": ("మీ దరఖాస్తు సేవ్ అయింది, కానీ ఇంకా సమర్పించలేదు.", "మీ దగ్గర ఉన్న ప్రతి పత్రాన్ని టిక్ చేసి, సమర్పించు నొక్కండి."),
        "hi": ("आपका आवेदन सहेजा गया है, पर अभी जमा नहीं हुआ है।", "आपके पास जो दस्तावेज़ हैं उन्हें टिक करें, फिर जमा करें दबाएँ।"),
        "ur": ("آپ کی درخواست محفوظ ہو گئی ہے، مگر ابھی جمع نہیں ہوئی۔", "جو دستاویزات آپ کے پاس ہیں انہیں ٹک کریں، پھر جمع کریں دبائیں۔"),
    },
    "submitted": {
        "en": ("Your application has reached the department.", "Nothing to do now. We will notify you when it moves forward."),
        "te": ("మీ దరఖాస్తు శాఖకు చేరింది.", "ఇప్పుడు ఏమీ చేయనవసరం లేదు. ముందుకు కదిలినప్పుడు మేము తెలియజేస్తాము."),
        "hi": ("आपका आवेदन विभाग तक पहुँच गया है।", "अभी कुछ करने की ज़रूरत नहीं। आगे बढ़ने पर हम आपको सूचित करेंगे।"),
        "ur": ("آپ کی درخواست محکمے تک پہنچ گئی ہے۔", "ابھی کچھ کرنے کی ضرورت نہیں۔ آگے بڑھنے پر ہم آپ کو مطلع کریں گے۔"),
    },
    "under_verification": {
        "en": ("An officer is checking your details and documents.", "This usually takes a few working days. Keep your phone reachable."),
        "te": ("ఒక అధికారి మీ వివరాలు మరియు పత్రాలను పరిశీలిస్తున్నారు.", "దీనికి సాధారణంగా కొన్ని పని దినాలు పడుతుంది. మీ ఫోన్ అందుబాటులో ఉంచండి."),
        "hi": ("एक अधिकारी आपके विवरण और दस्तावेज़ जाँच रहे हैं।", "इसमें आमतौर पर कुछ कार्य दिवस लगते हैं। अपना फ़ोन चालू रखें।"),
        "ur": ("ایک افسر آپ کی تفصیلات اور دستاویزات کی جانچ کر رہا ہے۔", "اس میں عام طور پر چند کام کے دن لگتے ہیں۔ اپنا فون قابلِ رسائی رکھیں۔"),
    },
    "needs_documents": {
        "en": ("The officer needs more documents from you.", "Read the remarks below and take the documents to a MeeSeva centre."),
        "te": ("అధికారికి మీ నుండి మరిన్ని పత్రాలు అవసరం.", "క్రింది వ్యాఖ్యలు చదివి, పత్రాలను మీసేవ కేంద్రానికి తీసుకెళ్లండి."),
        "hi": ("अधिकारी को आपसे और दस्तावेज़ चाहिए।", "नीचे दी गई टिप्पणी पढ़ें और दस्तावेज़ मीसेवा केंद्र ले जाएँ।"),
        "ur": ("افسر کو آپ سے مزید دستاویزات درکار ہیں۔", "نیچے دیے گئے تبصرے پڑھیں اور دستاویزات می سیوا مرکز لے جائیں۔"),
    },
    "approved": {
        "en": ("Your application is approved.", "Download the certificate or collect it from a MeeSeva centre."),
        "te": ("మీ దరఖాస్తు ఆమోదించబడింది.", "ధృవీకరణ పత్రాన్ని డౌన్‌లోడ్ చేసుకోండి లేదా మీసేవ కేంద్రం నుండి తీసుకోండి."),
        "hi": ("आपका आवेदन स्वीकृत हो गया है।", "प्रमाण पत्र डाउनलोड करें या मीसेवा केंद्र से प्राप्त करें।"),
        "ur": ("آپ کی درخواست منظور ہو گئی ہے۔", "سرٹیفکیٹ ڈاؤن لوڈ کریں یا می سیوا مرکز سے حاصل کریں۔"),
    },
    "rejected": {
        "en": ("Your application was not approved.", "Read the remarks. You can apply again with the corrected details."),
        "te": ("మీ దరఖాస్తు ఆమోదించబడలేదు.", "వ్యాఖ్యలు చదవండి. సరిచేసిన వివరాలతో మళ్లీ దరఖాస్తు చేయవచ్చు."),
        "hi": ("आपका आवेदन स्वीकृत नहीं हुआ।", "टिप्पणी पढ़ें। सही विवरण के साथ फिर से आवेदन कर सकते हैं।"),
        "ur": ("آپ کی درخواست منظور نہیں ہوئی۔", "تبصرے پڑھیں۔ درست تفصیلات کے ساتھ دوبارہ درخواست دے سکتے ہیں۔"),
    },
}

STATUS_CHANGED_TITLE = {
    "en": "Update on {ref}",
    "te": "{ref} పై అప్‌డేట్",
    "hi": "{ref} पर अपडेट",
    "ur": "{ref} پر اپ ڈیٹ",
}


def pick(table: dict, lang: str):
    return table.get(lang) or table["en"]
