# Pakistani Traffic Laws Data
# Source: Motor Vehicles Ordinance 1965, Punjab Traffic Rules,
#         National Highway Safety Ordinance 2000
# (Extracted as-is from Phase 2 notebook, Cell 2)

TRAFFIC_LAWS = [
    {
        "section": "Section 139 - Motor Vehicles Ordinance 1965",
        "violation": "No Helmet",
        "urdu_violation": "ہیلمٹ نہ پہننا",
        "description": "Every rider of a motorcycle or scooter and every pillion rider shall wear a protective helmet of such type as may be approved by the Government. Failure to wear a helmet is a punishable offence.",
        "fine_pkr": 500,
        "fine_usd": 1.8,
        "points": 2,
        "repeat_offence": "Fine doubles to PKR 1000 for second offence",
        "authority": "Traffic Police",
        "urdu_law": "موٹر وہیکل آرڈیننس 1965 کی دفعہ 139 کے تحت ہیلمٹ پہننا لازمی ہے"
    },
    {
        "section": "Section 136-A - Motor Vehicles Ordinance 1965",
        "violation": "No Seatbelt",
        "urdu_violation": "سیٹ بیلٹ نہ لگانا",
        "description": "Every driver and front-seat passenger of a motor vehicle shall wear a seatbelt while the vehicle is in motion on a public road. Failure to wear seatbelt shall be punishable with fine.",
        "fine_pkr": 500,
        "fine_usd": 1.8,
        "points": 2,
        "repeat_offence": "Fine of PKR 1500 for subsequent offences",
        "authority": "Traffic Police",
        "urdu_law": "موٹر وہیکل آرڈیننس 1965 کی دفعہ 136-A کے مطابق سیٹ بیلٹ لگانا لازمی ہے"
    },
    {
        "section": "Section 120 - Motor Vehicles Ordinance 1965",
        "violation": "Signal Jumping",
        "urdu_violation": "سرخ بتی توڑنا",
        "description": "No driver shall disobey the instructions given by any traffic sign, signal, or marking. Jumping a red traffic signal is a serious offence endangering public safety.",
        "fine_pkr": 1000,
        "fine_usd": 3.6,
        "points": 4,
        "repeat_offence": "License suspension for 30 days on third offence",
        "authority": "Traffic Police",
        "urdu_law": "موٹر وہیکل آرڈیننس 1965 کی دفعہ 120 کے تحت ٹریفک سگنل توڑنا قابل سزا جرم ہے"
    },
    {
        "section": "Section 52 - Motor Vehicles Ordinance 1965",
        "violation": "Expired Registration",
        "urdu_violation": "گاڑی کی رجسٹریشن کی میعاد ختم",
        "description": "No person shall drive or cause to be driven in any public place any motor vehicle which is not registered or whose registration has expired under this Ordinance.",
        "fine_pkr": 2000,
        "fine_usd": 7.2,
        "points": 6,
        "repeat_offence": "Vehicle impoundment",
        "authority": "Traffic Police / Excise Department",
        "urdu_law": "موٹر وہیکل آرڈیننس 1965 کی دفعہ 52 کے تحت غیر رجسٹرڈ گاڑی چلانا ممنوع ہے"
    },
    {
        "section": "Section 115 - Motor Vehicles Ordinance 1965",
        "violation": "Overspeeding",
        "urdu_violation": "رفتار حد سے تجاوز",
        "description": "No person shall drive a motor vehicle at a speed exceeding the maximum speed limit prescribed for that class of road. Urban roads: 50 km/h, Highways: 120 km/h, School zones: 25 km/h.",
        "fine_pkr": 1500,
        "fine_usd": 5.4,
        "points": 3,
        "repeat_offence": "License suspension 15 days",
        "authority": "Traffic Police",
        "urdu_law": "موٹر وہیکل آرڈیننس 1965 کی دفعہ 115 کے تحت رفتار کی حد سے تجاوز کرنا ممنوع ہے"
    },
    {
        "section": "Section 7 - National Highway Safety Ordinance 2000",
        "violation": "Wrong Way Driving",
        "urdu_violation": "غلط سمت میں گاڑی چلانا",
        "description": "No person shall drive a vehicle in a direction contrary to the prescribed traffic flow on any national highway or urban road. This creates severe risk of head-on collision.",
        "fine_pkr": 3000,
        "fine_usd": 10.8,
        "points": 8,
        "repeat_offence": "License cancellation",
        "authority": "Traffic Police / Highway Police",
        "urdu_law": "قومی شاہراہ حفاظتی آرڈیننس 2000 کی دفعہ 7 کے تحت غلط سمت گاڑی چلانا سنگین جرم ہے"
    },
    {
        "section": "Section 117 - Motor Vehicles Ordinance 1965",
        "violation": "Mobile Phone While Driving",
        "urdu_violation": "ڈرائیونگ کے دوران موبائل فون استعمال",
        "description": "No driver shall use a hand-held mobile phone, including for calling, texting, or any other purpose, while driving a vehicle in motion. Hands-free use is permissible.",
        "fine_pkr": 1000,
        "fine_usd": 3.6,
        "points": 3,
        "repeat_offence": "Fine PKR 3000",
        "authority": "Traffic Police",
        "urdu_law": "موٹر وہیکل آرڈیننس 1965 کی دفعہ 117 کے تحت گاڑی چلاتے وقت موبائل فون استعمال ممنوع ہے"
    },
    {
        "section": "Section 43 - Motor Vehicles Ordinance 1965",
        "violation": "No Driving License",
        "urdu_violation": "ڈرائیونگ لائسنس نہ ہونا",
        "description": "No person shall drive a motor vehicle in any public place unless he holds an effective driving licence issued under this Ordinance authorising him to drive the vehicle of that class.",
        "fine_pkr": 2000,
        "fine_usd": 7.2,
        "points": 0,
        "repeat_offence": "Vehicle impoundment + court appearance",
        "authority": "Traffic Police",
        "urdu_law": "موٹر وہیکل آرڈیننس 1965 کی دفعہ 43 کے مطابق ڈرائیونگ لائسنس کے بغیر گاڑی چلانا جرم ہے"
    },
]
