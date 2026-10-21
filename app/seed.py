"""Sample data for the prototype.

IMPORTANT: services, documents, fees and timelines below are representative SAMPLE DATA prepared for
the demo. They are not official MeeSeva figures. A production version would load the catalogue from
the ESD/MeeSeva service master.
"""
from sqlalchemy.orm import Session

from app.database import Base, engine as default_engine
import random
from datetime import datetime, timedelta, timezone

from app.models import (Application, ApplicationDocument, Centre, District, Document, Feedback, Notification, Query,
                        Service, ServiceDocument, User)

DISTRICTS = [
    ("Hyderabad", "హైదరాబాద్"), ("Rangareddy", "రంగారెడ్డి"), ("Medchal-Malkajgiri", "మేడ్చల్-మల్కాజ్‌గిరి"),
    ("Sangareddy", "సంగారెడ్డి"), ("Warangal", "వరంగల్"), ("Karimnagar", "కరీంనగర్"), ("Khammam", "ఖమ్మం"),
    ("Nizamabad", "నిజామాబాద్"), ("Mahabubnagar", "మహబూబ్‌నగర్"), ("Nalgonda", "నల్గొండ"),
]

# code: (en, te, hi, ur)
DOCUMENTS = {
    "AADHAAR": ("Aadhaar card", "ఆధార్ కార్డు", "आधार कार्ड", "آدھار کارڈ"),
    "PHOTO": ("Passport-size photograph", "పాస్‌పోర్ట్ సైజు ఫోటో", "पासपोर्ट साइज़ फ़ोटो", "پاسپورٹ سائز تصویر"),
    "ADDRESS": ("Address proof (ration card, electricity bill or rent agreement)",
                "చిరునామా రుజువు (రేషన్ కార్డు, కరెంట్ బిల్లు లేదా అద్దె ఒప్పందం)",
                "पते का प्रमाण (राशन कार्ड, बिजली बिल या किराया अनुबंध)",
                "پتے کا ثبوت (راشن کارڈ، بجلی کا بل یا کرایہ نامہ)"),
    "INCOME": ("Income proof (salary slip or self-declaration)", "ఆదాయ రుజువు (జీతం స్లిప్ లేదా స్వీయ ప్రకటన)",
               "आय का प्रमाण (वेतन पर्ची या स्व-घोषणा)", "آمدنی کا ثبوت (تنخواہ پرچی یا خود اقرار نامہ)"),
    "SSC": ("SSC / school study certificate", "ఎస్ఎస్‌సి / పాఠశాల చదువు ధృవీకరణ పత్రం",
            "एसएससी / स्कूल अध्ययन प्रमाण पत्र", "ایس ایس سی / اسکول سرٹیفکیٹ"),
    "PARENT_CASTE": ("Parent's caste certificate (if available)", "తల్లిదండ్రుల కుల ధృవీకరణ పత్రం (ఉంటే)",
                     "माता-पिता का जाति प्रमाण पत्र (यदि हो)", "والدین کا ذات سرٹیفکیٹ (اگر ہو)"),
    "BIRTH_REPORT": ("Hospital birth report or discharge summary", "ఆసుపత్రి జనన నివేదిక లేదా డిశ్చార్జ్ సారాంశం",
                     "अस्पताल की जन्म रिपोर्ट या डिस्चार्ज सारांश", "ہسپتال کی پیدائش رپورٹ یا ڈسچارج خلاصہ"),
    "PARENT_AADHAAR": ("Parents' Aadhaar cards", "తల్లిదండ్రుల ఆధార్ కార్డులు", "माता-पिता के आधार कार्ड",
                       "والدین کے آدھار کارڈ"),
    "DEATH_REPORT": ("Hospital or village death report", "ఆసుపత్రి లేదా గ్రామ మరణ నివేదిక",
                     "अस्पताल या ग्राम की मृत्यु रिपोर्ट", "ہسپتال یا گاؤں کی وفات رپورٹ"),
    "DECEASED_ID": ("Aadhaar of the deceased", "మరణించిన వ్యక్తి ఆధార్", "मृतक का आधार", "مرحوم کا آدھار"),
    "PROPERTY": ("Property document or sale deed number", "ఆస్తి పత్రం లేదా సేల్ డీడ్ నంబర్",
                 "संपत्ति दस्तावेज़ या बिक्री विलेख संख्या", "جائیداد کی دستاویز یا بیع نامہ نمبر"),
    "PASSBOOK": ("Land passbook or survey number", "భూమి పాస్‌బుక్ లేదా సర్వే నంబర్",
                 "भूमि पासबुक या सर्वे नंबर", "زمین کی پاس بک یا سروے نمبر"),
    "MARRIAGE_PROOF": ("Wedding invitation and photograph", "పెళ్లి పత్రిక మరియు ఫోటో",
                       "शादी का निमंत्रण पत्र और फ़ोटो", "شادی کا دعوت نامہ اور تصویر"),
    "WITNESS_ID": ("ID proof of two witnesses", "ఇద్దరు సాక్షుల గుర్తింపు రుజువు", "दो गवाहों के पहचान प्रमाण",
                   "دو گواہوں کے شناختی ثبوت"),
    "EMPLOYER": ("Letter from employer stating the purpose", "ప్రయోజనం తెలిపే యజమాని లేఖ",
                 "उद्देश्य बताने वाला नियोक्ता का पत्र", "مقصد بتانے والا آجر کا خط"),
    "CONSUMER_NO": ("Electricity consumer (service) number", "విద్యుత్ వినియోగదారు (సర్వీస్) నంబర్",
                    "बिजली उपभोक्ता (सर्विस) नंबर", "بجلی صارف (سروس) نمبر"),
    "FAMILY_LIST": ("List of family members with Aadhaar", "ఆధార్‌తో కుటుంబ సభ్యుల జాబితా",
                    "आधार सहित परिवार के सदस्यों की सूची", "آدھار کے ساتھ خاندان کے افراد کی فہرست"),
    "RATION": ("Existing ration card (for changes)", "ప్రస్తుత రేషన్ కార్డు (మార్పుల కోసం)", "मौजूदा राशन कार्ड (बदलाव के लिए)", "موجودہ راشن کارڈ (تبدیلی کے لیے)"),
    "GAS": ("LPG gas connection details", "ఎల్‌పీజీ గ్యాస్ కనెక్షన్ వివరాలు", "एलपीजी गैस कनेक्शन विवरण", "ایل پی جی گیس کنکشن کی تفصیلات"),
    "PTIN": ("Property tax identification number (PTIN)", "ఆస్తి పన్ను గుర్తింపు నంబర్ (PTIN)", "संपत्ति कर पहचान संख्या (PTIN)", "پراپرٹی ٹیکس شناختی نمبر (PTIN)"),
    "CAN": ("Water connection (CAN) number", "నీటి కనెక్షన్ (CAN) నంబర్", "जल कनेक्शन (CAN) नंबर", "پانی کنکشن (CAN) نمبر"),
    "CHALLAN": ("Vehicle number or challan number", "వాహన నంబర్ లేదా చలాన్ నంబర్", "वाहन नंबर या चालान नंबर", "گاڑی نمبر یا چالان نمبر"),
    "DOC_NO": ("Registered document number and year", "నమోదిత పత్రం నంబర్ మరియు సంవత్సరం", "पंजीकृत दस्तावेज़ संख्या और वर्ष", "رجسٹرڈ دستاویز نمبر اور سال"),
    "STUDY": ("Study certificates (classes 1 to 7 or 4 to 10)", "చదువు ధృవీకరణ పత్రాలు (1–7 లేదా 4–10 తరగతులు)", "अध्ययन प्रमाण पत्र (कक्षा 1–7 या 4–10)", "تعلیمی سرٹیفکیٹ (جماعت 1–7 یا 4–10)"),
}

# code, category, department, (en, te, hi, ur), description, eligibility, fee, days, keywords, documents
SERVICES = [
    ("INC", "Certificates", "Revenue Department",
     ("Income Certificate", "ఆదాయ ధృవీకరణ పత్రం", "आय प्रमाण पत्र", "آمدنی سرٹیفکیٹ"),
     "Certifies the annual family income, needed for scholarships, fee reimbursement and welfare schemes.",
     "Residents of Telangana; issued for the applicant's family.", 45, 7,
     "income,salary,annual income,scholarship,fee reimbursement,ఆదాయ,ఆదాయం,జీతం,आय,आमदनी,वेतन,آمدنی,تنخواہ",
     ["AADHAAR", "ADDRESS", "INCOME", "PHOTO"]),
    ("CST", "Certificates", "Revenue Department",
     ("Caste Certificate", "కుల ధృవీకరణ పత్రం", "जाति प्रमाण पत्र", "ذات سرٹیفکیٹ"),
     "Certifies the community (SC/ST/BC) for education, jobs and reservation benefits.",
     "Residents of Telangana belonging to a notified community.", 45, 30,
     "caste,community,reservation,sc certificate,st certificate,bc certificate,కుల,కులం,జాతి,जाति,आरक्षण,ذات,برادری",
     ["AADHAAR", "SSC", "PARENT_CASTE", "PHOTO", "ADDRESS"]),
    ("RES", "Certificates", "Revenue Department",
     ("Residence Certificate", "నివాస ధృవీకరణ పత్రం", "निवास प्रमाण पत्र", "رہائشی سرٹیفکیٹ"),
     "Certifies where the applicant lives, needed for admissions, local quota and bank or gas connections.",
     "Persons living at the address for the required period.", 45, 6,
     "residence,resident,nativity,domicile,local,address certificate,నివాస,స్థానిక,निवास,मूल निवास,रहने,رہائش,رہائشی,مقامی",
     ["AADHAAR", "ADDRESS", "PHOTO"]),
    ("BIR", "Certificates", "Municipal Administration",
     ("Birth Certificate", "జనన ధృవీకరణ పత్రం", "जन्म प्रमाण पत्र", "پیدائش سرٹیفکیٹ"),
     "Official record of a child's birth, needed for school admission, Aadhaar and passport.",
     "Births registered in Telangana.", 50, 7,
     "birth,born,baby,child,date of birth,newborn,జనన,పుట్టిన,జననం,जन्म,बच्चा,पैदा,پیدائش,بچہ",
     ["BIRTH_REPORT", "PARENT_AADHAAR", "ADDRESS"]),
    ("DTH", "Certificates", "Municipal Administration",
     ("Death Certificate", "మరణ ధృవీకరణ పత్రం", "मृत्यु प्रमाण पत्र", "وفات سرٹیفکیٹ"),
     "Official record of a death, needed for pension, insurance, property and bank claims.",
     "Family members of a person whose death was registered in Telangana.", 50, 7,
     "death,died,passed away,మరణ,మరణం,చనిపోయ,मृत्यु,मौत,निधन,وفات,انتقال,موت",
     ["DEATH_REPORT", "DECEASED_ID", "AADHAAR"]),
    ("EWS", "Certificates", "Revenue Department",
     ("EWS Income and Asset Certificate", "ఈడబ్ల్యూఎస్ ఆదాయ మరియు ఆస్తి ధృవీకరణ పత్రం",
      "ईडब्ल्यूएस आय एवं संपत्ति प्रमाण पत्र", "ای ڈبلیو ایس آمدنی اور اثاثہ سرٹیفکیٹ"),
     "Certificate for the Economically Weaker Sections quota in education and jobs.",
     "Families not covered by SC/ST/BC reservation, within the income and asset limits.", 45, 7,
     "ews,economically weaker,10% quota,ఈడబ్ల్యూఎస్,ఆర్థికంగా బలహీన,ईडब्ल्यूएस,आर्थिक रूप से कमजोर,ای ڈبلیو ایس",
     ["AADHAAR", "INCOME", "ADDRESS", "PHOTO"]),
    ("FMC", "Certificates", "Revenue Department",
     ("Family Member Certificate", "కుటుంబ సభ్యుల ధృవీకరణ పత్రం", "परिवार सदस्य प्रमाण पत्र", "خاندانی افراد کا سرٹیفکیٹ"),
     "Lists the family members of a person, often needed after a death for claims and transfers.",
     "Family members of the person concerned.", 45, 30,
     "family member,legal heir,heir,కుటుంబ సభ్యుల,వారసుల,परिवार सदस्य,वारिस,خاندان,وارث",
     ["AADHAAR", "FAMILY_LIST", "DEATH_REPORT", "ADDRESS"]),
    ("ENC", "Land and property", "Registration and Stamps",
     ("Encumbrance Certificate", "ఎన్‌కంబరెన్స్ సర్టిఫికేట్ (ఈసీ)", "भार प्रमाण पत्र (ईसी)", "انکمبرنس سرٹیفکیٹ"),
     "Shows registered transactions on a property, needed for loans and purchases.",
     "Anyone with the property details.", 200, 3,
     "encumbrance,property loan,home loan,sale deed,ఎన్‌కంబరెన్స్,ఆస్తి,भार प्रमाण,संपत्ति,انکمبرنس,جائیداد",
     ["PROPERTY", "AADHAAR"]),
    ("PAH", "Land and property", "Revenue Department",
     ("Land Record Copy (Pahani / ROR)", "భూమి రికార్డు కాపీ (పహాణీ / ఆర్ఓఆర్)", "भूमि अभिलेख प्रति (पहाणी / आरओआर)",
      "زمین ریکارڈ کی نقل (پہانی / آر او آر)"),
     "Certified copy of land ownership and cultivation records.",
     "Land owners or anyone with the survey number.", 35, 1,
     "land record,pahani,ror,adangal,survey number,passbook,భూమి,పహాణీ,సర్వే నంబర్,भूमि,ज़मीन,पहाणी,زمین,پہانی",
     ["PASSBOOK", "AADHAAR"]),
    ("MAR", "Registrations", "Registration and Stamps",
     ("Marriage Registration", "వివాహ నమోదు", "विवाह पंजीकरण", "شادی کا اندراج"),
     "Registers a marriage and issues the marriage certificate.",
     "Couples married in Telangana, with both partners present.", 300, 3,
     "marriage,wedding,married,spouse,వివాహ,పెళ్లి,विवाह,शादी,شادی,نکاح",
     ["AADHAAR", "MARRIAGE_PROOF", "WITNESS_ID", "PHOTO", "ADDRESS"]),
    ("PVC", "Police services", "Police Department",
     ("Police Verification Certificate", "పోలీసు ధృవీకరణ పత్రం", "पुलिस सत्यापन प्रमाण पत्र", "پولیس تصدیقی سرٹیفکیٹ"),
     "Character and antecedent verification for jobs, site access, tenancy or travel.",
     "Residents applying through their local police station jurisdiction.", 150, 15,
     "police verification,police clearance,pvc,character certificate,background check,పోలీసు,పోలీస్,पुलिस,सत्यापन,پولیس,تصدیق",
     ["AADHAAR", "ADDRESS", "EMPLOYER", "PHOTO"]),
    ("ELB", "Bill payments", "Electricity Distribution (TGSPDCL/TGNPDCL)",
     ("Electricity Bill Payment", "విద్యుత్ బిల్లు చెల్లింపు", "बिजली बिल भुगतान", "بجلی بل کی ادائیگی"),
     "Pay the household electricity bill at a centre or online.",
     "Any consumer with a service number.", 0, 0,
     "electricity,current bill,power bill,light bill,విద్యుత్,కరెంట్,కరెంటు,बिजली,बिजली बिल,بجلی",
     ["CONSUMER_NO"]),
    ("OBC", "Certificates", "Revenue Department",
     ("OBC Certificate (Central)", "ఓబీసీ ధృవీకరణ పత్రం (కేంద్రం)", "ओबीसी प्रमाण पत्र (केंद्रीय)", "او بی سی سرٹیفکیٹ (مرکزی)"),
     "Other Backward Class certificate in the central format, needed for central government jobs and institutions.",
     "Persons of a community in the central OBC list, outside the creamy layer.", 45, 30,
     "obc,central obc,non creamy layer,creamy layer,ఓబీసీ,ओबीसी,او بی سی",
     ["AADHAAR", "SSC", "PARENT_CASTE", "INCOME", "PHOTO"]),
    ("NAT", "Certificates", "Revenue Department",
     ("Nativity Certificate", "స్థానికత ధృవీకరణ పత్రం", "मूल निवासी प्रमाण पत्र", "آبائی وطن سرٹیفکیٹ"),
     "Certifies that the applicant is a native of Telangana, needed for local quota in education and jobs.",
     "Persons born in, or who studied for the required years in, Telangana.", 45, 30,
     "nativity,native,local candidate,local quota,local status,స్థానికత,స్థానిక అభ్యర్థి,मूल निवासी,स्थानीय,آبائی,مقامی امیدوار",
     ["AADHAAR", "STUDY", "ADDRESS", "PHOTO"]),
    ("RAT", "Civil supplies", "Civil Supplies Department",
     ("Ration Card – New or Changes", "రేషన్ కార్డు – కొత్తది లేదా మార్పులు", "राशन कार्ड – नया या बदलाव", "راشن کارڈ – نیا یا تبدیلی"),
     "Apply for a new food security card, or add or remove family members and change the address.",
     "Eligible families under the state food security scheme; changes by the card holder.", 0, 30,
     "ration card,food security card,add member,remove member,fsc,రేషన్,రేషన్ కార్డు,राशन,राशन कार्ड,راشن,راشن کارڈ",
     ["AADHAAR", "RATION", "FAMILY_LIST", "ADDRESS", "GAS"]),
    ("PTX", "Bill payments", "Greater Hyderabad Municipal Corporation (GHMC)",
     ("Property Tax Payment", "ఆస్తి పన్ను చెల్లింపు", "संपत्ति कर भुगतान", "پراپرٹی ٹیکس کی ادائیگی"),
     "Pay the yearly property tax for a house or shop, at a centre or online.",
     "Any property owner with a PTIN.", 0, 0,
     "property tax,house tax,ptin,ghmc tax,ఆస్తి పన్ను,ఇంటి పన్ను,संपत्ति कर,मकान कर,پراپرٹی ٹیکس,مکان ٹیکس",
     ["PTIN"]),
    ("WTR", "Bill payments", "Hyderabad Metropolitan Water Supply and Sewerage Board (HMWSSB)",
     ("Water Bill Payment", "నీటి బిల్లు చెల్లింపు", "पानी का बिल भुगतान", "پانی کے بل کی ادائیگی"),
     "Pay the household water bill at a centre or online.",
     "Any consumer with a CAN number.", 0, 0,
     "water bill,water charges,hmwssb,can number,నీటి బిల్లు,నీళ్ల బిల్లు,पानी का बिल,जल बिल,پانی کا بل",
     ["CAN"]),
    ("CHL", "Police services", "Police Department (Traffic)",
     ("Traffic Challan Payment", "ట్రాఫిక్ చలాన్ చెల్లింపు", "ट्रैफ़िक चालान भुगतान", "ٹریفک چالان کی ادائیگی"),
     "Pay pending traffic fines on a vehicle.",
     "Any vehicle owner or driver.", 0, 0,
     "challan,traffic fine,e-challan,pending challan,చలాన్,ట్రాఫిక్ జరిమానా,चालान,ट्रैफ़िक जुर्माना,چالان,ٹریفک جرمانہ",
     ["CHALLAN"]),
    ("CCD", "Land and property", "Registration and Stamps",
     ("Certified Copy of Registered Document", "నమోదిత పత్రం ధృవీకృత కాపీ", "पंजीकृत दस्तावेज़ की प्रमाणित प्रति", "رجسٹرڈ دستاویز کی مصدقہ نقل"),
     "Certified copy of a registered sale deed, gift deed or other document, for loans, disputes or lost originals.",
     "Anyone with the document number and year.", 200, 3,
     "certified copy,lost sale deed,copy of deed,registered document,ధృవీకృత కాపీ,సేల్ డీడ్ కాపీ,प्रमाणित प्रति,बिक्री विलेख की प्रति,مصدقہ نقل,بیع نامے کی نقل",
     ["DOC_NO", "AADHAAR"]),
]

# Sample centres (illustrative names and coordinates).
CENTRES = [
    ("MeeSeva Centre, Gachibowli", "Rangareddy", "Opp. DLF Cyber City, Gachibowli, Hyderabad", 17.4435, 78.3772),
    ("MeeSeva Centre, Kondapur", "Rangareddy", "Botanical Garden Road, Kondapur", 17.4632, 78.3647),
    ("MeeSeva Centre, Nallagandla", "Rangareddy", "Tellapur Road, Nallagandla", 17.4718, 78.3112),
    ("MeeSeva Centre, Ameerpet", "Hyderabad", "Near Metro Station, Ameerpet", 17.4375, 78.4482),
    ("MeeSeva Centre, Charminar", "Hyderabad", "Pathergatti Road, Charminar", 17.3616, 78.4747),
    ("MeeSeva Centre, Kukatpally", "Medchal-Malkajgiri", "KPHB Colony, Kukatpally", 17.4849, 78.3996),
    ("MeeSeva Centre, Sangareddy", "Sangareddy", "Collectorate Road, Sangareddy", 17.6140, 78.0816),
    ("MeeSeva Centre, Hanamkonda", "Warangal", "Bus Stand Road, Hanamkonda", 17.9969, 79.5590),
    ("MeeSeva Centre, Karimnagar", "Karimnagar", "Tower Circle, Karimnagar", 18.4386, 79.1288),
    ("MeeSeva Centre, Khammam", "Khammam", "Wyra Road, Khammam", 17.2473, 80.1514),
]


def seed(db: Session, demo_users: bool = True) -> None:
    """Load the sample catalogue (idempotent: does nothing if services already exist)."""
    if db.query(Service).first():
        return
    districts = {}
    for en, te in DISTRICTS:
        d = District(name_en=en, name_te=te)
        db.add(d)
        districts[en] = d
    docs = {}
    for code, (en, te, hi, ur) in DOCUMENTS.items():
        doc = Document(code=code, name_en=en, name_te=te, name_hi=hi, name_ur=ur)
        db.add(doc)
        docs[code] = doc
    db.flush()
    for code, cat, dept, (en, te, hi, ur), desc, elig, fee, days, kw, dcodes in SERVICES:
        svc = Service(code=code, category=cat, department=dept, name_en=en, name_te=te, name_hi=hi, name_ur=ur,
                      description_en=desc, eligibility_en=elig, fee_inr=fee, sla_days=days, keywords=kw)
        svc.documents = [ServiceDocument(document=docs[c], mandatory=True) for c in dcodes]
        db.add(svc)
    for name, dist, addr, lat, lng in CENTRES:
        db.add(Centre(name=name, district=districts[dist], address=addr, lat=lat, lng=lng,
                      open_hours="Mon–Sat 8:00–20:00"))
    if demo_users:
        # Demo accounts: the official logs in to the dashboard with this number (OTP shown in demo mode).
        db.add(User(mobile="9000000001", name="ESD Officer (demo)", role="official", preferred_lang="en",
                    district=districts["Hyderabad"]))
    db.commit()


# ---------------------------------------------------------------------------------------------
# Demo data: realistic citizen activity so the officials' dashboard has something to show.
# ---------------------------------------------------------------------------------------------
DEMO_QUERIES = [  # (text, lang, service code or None)
    ("I need income certificate for my daughter's scholarship", "en", "INC"),
    ("నాకు ఆదాయ ధృవీకరణ పత్రం కావాలి", "te", "INC"), ("ఆదాయ సర్టిఫికేట్ ఎలా తీసుకోవాలి", "te", "INC"),
    ("आय प्रमाण पत्र के लिए क्या दस्तावेज़ चाहिए", "hi", "INC"), ("آمدنی سرٹیفکیٹ کے لیے کیا چاہیے", "ur", "INC"),
    ("caste certificate for college admission", "en", "CST"), ("కుల ధృవీకరణ పత్రం కావాలి", "te", "CST"),
    ("मुझे जाति प्रमाण पत्र चाहिए", "hi", "CST"), ("ذات سرٹیفکیٹ کیسے بنے گا", "ur", "CST"),
    ("residence certificate for school", "en", "RES"), ("నివాస ధృవీకరణ పత్రం", "te", "RES"),
    ("birth certificate for my baby", "en", "BIR"), ("పుట్టిన సర్టిఫికేట్", "te", "BIR"), ("جنم سرٹیفکیٹ", "ur", "BIR"),
    ("మా నాన్న చనిపోయారు పెన్షన్ కోసం ఏమి కావాలి", "te", "DTH"), ("death certificate", "en", "DTH"),
    ("police verification for new job", "en", "PVC"), ("పోలీసు వెరిఫికేషన్ సర్టిఫికేట్", "te", "PVC"),
    ("how to pay current bill", "en", "ELB"), ("కరెంట్ బిల్లు కట్టాలి", "te", "ELB"), ("बिजली बिल भरना है", "hi", "ELB"),
    ("ration card lo peru add cheyali", "en", None), ("రేషన్ కార్డులో పేరు చేర్చాలి", "te", "RAT"),
    ("राशन कार्ड में नाम जोड़ना है", "hi", "RAT"), ("ews certificate", "en", "EWS"),
    ("family member certificate after father's death", "en", "FMC"), ("encumbrance certificate for home loan", "en", "ENC"),
    ("pahani copy", "en", "PAH"), ("marriage registration", "en", "MAR"), ("ట్రాఫిక్ చలాన్ కట్టాలి", "te", "CHL"),
    ("property tax payment", "en", "PTX"), ("water bill", "en", "WTR"), ("obc certificate central", "en", "OBC"),
    ("nativity certificate", "en", "NAT"), ("lost my sale deed, need a copy", "en", "CCD"),
    # not in the catalogue -> service gaps the ESD wing should see
    ("driving licence renewal", "en", None), ("passport renewal", "en", None), ("aadhaar address change", "en", None),
    ("పాన్ కార్డు కొత్తది", "te", None), ("voter id correction", "en", None), ("pension status aasara", "en", None),
    ("ఇందిరమ్మ ఇళ్లు దరఖాస్తు స్థితి", "te", None), ("बिजली कनेक्शन नया", "hi", None),
]
DEMO_FEEDBACK = [  # (rating, comment, lang)
    (5, "Very easy, told me exactly which documents to carry", "en"), (5, "చాలా సులభం, ధన్యవాదాలు", "te"),
    (4, "Good but the fee shown was different at the centre", "en"), (2, "Centre staff were rude and the queue was very long", "en"),
    (3, "आवेदन 10 दिन से लंबित है", "hi"), (1, "Application rejected without any reason given", "en"),
    (5, "Finally understood what 'under verification' means", "en"), (4, "اردو میں جواب ملا، بہت اچھا", "ur"),
    (2, "Website login OTP did not come for 10 minutes", "en"), (5, "Voice input in Telugu worked for my mother", "en"),
    (3, "Needed one more document that was not in the list", "en"), (4, "Nearest centre map was helpful", "en"),
]
DEMO_CITIZENS = [("9100000001", "Ravi Kumar", "te"), ("9100000002", "Lakshmi Devi", "te"), ("9100000003", "Mohammed Irfan", "ur"),
                 ("9100000004", "Sunita Sharma", "hi"), ("9100000005", "Anand Reddy", "en"), ("9100000006", "Fatima Begum", "ur")]
DEMO_APPS = [  # (citizen idx, service, status, remarks, documents provided)
    (0, "INC", "approved", "", True), (1, "RES", "under_verification", "", True),
    (2, "BIR", "needs_documents", "Hospital discharge summary is not legible. Please upload a clear copy.", True),
    (3, "CST", "submitted", "", True), (4, "PVC", "rejected", "Address proof does not match the current address.", True),
    (0, "DTH", "draft", "", False), (5, "RAT", "submitted", "", True), (1, "ENC", "approved", "", True),
]


def seed_demo(db: Session) -> None:
    """Add sample citizen activity (queries, feedback, applications, notifications). Idempotent."""
    if db.query(Query).first():
        return
    rng = random.Random(7)
    now = datetime.now(timezone.utc)
    svc = {s.code: s for s in db.query(Service).all()}
    citizens = []
    for mobile, name, lang in DEMO_CITIZENS:
        u = db.query(User).filter(User.mobile == mobile).first() or User(mobile=mobile, name=name, preferred_lang=lang)
        db.add(u)
        citizens.append(u)
    db.flush()
    queries = []
    for i, (text, lang, code) in enumerate(DEMO_QUERIES * 2):
        q = Query(user_id=rng.choice(citizens).id if rng.random() < 0.6 else None, text=text, lang=lang,
                  matched_service_id=svc[code].id if code else None, confidence=0.9 if code else 0.0,
                  source=rng.choice(["ai", "ai", "rules"]), created_at=now - timedelta(days=rng.randint(0, 29), hours=rng.randint(0, 23)))
        db.add(q)
        queries.append(q)
    db.flush()
    from app.assistant import classify_feedback
    for rating, comment, lang in DEMO_FEEDBACK:
        sentiment, topic = classify_feedback(comment, rating)
        db.add(Feedback(user_id=rng.choice(citizens).id, query_id=rng.choice(queries).id, rating=rating, comment=comment,
                        sentiment=sentiment, topic=topic, created_at=now - timedelta(days=rng.randint(0, 20))))
    from app.texts import STATUS, STATUS_CHANGED_TITLE, pick
    for n, (ci, code, status, remarks, provided) in enumerate(DEMO_APPS):
        user, service = citizens[ci], svc[code]
        a = Application(reference_no=f"MS2610DEMO{n:02d}", user=user, service=service, applicant_name=user.name,
                        status=status, remarks=remarks, created_at=now - timedelta(days=rng.randint(2, 25)))
        db.add(a)
        a.documents = [ApplicationDocument(document=sd.document, provided=provided) for sd in service.documents]
        if status not in ("draft", "submitted"):
            meaning, next_step = pick(STATUS[status], user.preferred_lang)
            db.add(Notification(user_id=user.id, title=pick(STATUS_CHANGED_TITLE, user.preferred_lang).format(ref=a.reference_no),
                                body=f"{meaning} {next_step}" + (f"\n{remarks}" if remarks else ""), read=rng.random() < 0.5))
    db.commit()


def reset_and_seed(bind=None, demo: bool = False) -> None:
    """Drop and recreate every table, then seed. Used by `python -m app.seed` and tests."""
    from sqlalchemy.orm import Session as S
    bind = bind or default_engine
    Base.metadata.drop_all(bind)
    Base.metadata.create_all(bind)
    with S(bind) as db:
        seed(db)
        if demo:
            seed_demo(db)


if __name__ == "__main__":
    import sys
    demo = "--demo" in sys.argv
    reset_and_seed(demo=demo)
    print("Database created and sample data loaded." + (" Demo activity added." if demo else ""))
