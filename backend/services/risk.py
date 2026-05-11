"""
Геополитический риск по странам и регионам маршрута.
Источник: ACLED Conflict Index — December 2025
(данные за Dec 2024 — Nov 2025, 244 страны)

Методология нормализации:
  - Extreme  (rank 1–10):   floor 0.75 + вклад ранга до 0.25 = [0.75..1.0]
  - High     (rank 11–57):  floor 0.50 + вклад ранга до 0.25 = [0.50..0.75]
  - Turbulent(rank 58–?):   floor 0.25 + вклад ранга до 0.25 = [0.25..0.50]
  - Low/Inactive:           floor 0.00 + вклад ранга до 0.25 = [0.00..0.25]

Поиск страны по городу (вариант 3):
  1. Словарь _CITY_TO_COUNTRY (мгновенно, ~150 городов)
  2. Если не найдено — Nominatim API (OpenStreetMap, бесплатно)
  3. Если API недоступен — определение по координатам из боксов регионов
  Результат кэшируется в _geocache чтобы не дёргать API повторно.

Индекс [0..1]: 0 = безопасно, 1 = крайне высокий риск.
"""
import httpx
from services.geocoding import get_coords

# ─── ACLED Conflict Index 2025 — 244 страны ──────────────────────────────────
_ACLED_RISK: dict[str, float] = {
    "Palestine": 1.0,  # Extreme rank 1
    "Myanmar": 0.998,  # Extreme rank 2
    "Syria": 0.997,  # Extreme rank 3
    "Mexico": 0.995,  # Extreme rank 4
    "Nigeria": 0.994,  # Extreme rank 5
    "Ecuador": 0.992,  # Extreme rank 6
    "Brazil": 0.99,  # Extreme rank 7
    "Haiti": 0.989,  # Extreme rank 8
    "Sudan": 0.989,  # Extreme rank 8
    "Pakistan": 0.985,  # Extreme rank 10
    "Cameroon": 0.734,  # High rank 11
    "Democratic Republic of Congo": 0.734,  # High rank 11
    "Ukraine": 0.734,  # High rank 11
    "Colombia": 0.729,  # High rank 14
    "Yemen": 0.727,  # High rank 15
    "India": 0.726,  # High rank 16
    "Guatemala": 0.724,  # High rank 17
    "Somalia": 0.724,  # High rank 17
    "Lebanon": 0.721,  # High rank 19
    "Russia": 0.721,  # High rank 19
    "Bangladesh": 0.718,  # High rank 21
    "Ethiopia": 0.716,  # High rank 22
    "Iraq": 0.716,  # High rank 22
    "Kenya": 0.713,  # High rank 24
    "South Sudan": 0.711,  # High rank 25
    "Honduras": 0.71,  # High rank 26
    "Mali": 0.708,  # High rank 27
    "Jamaica": 0.706,  # High rank 28
    "Central African Republic": 0.705,  # High rank 29
    "Burundi": 0.703,  # High rank 30
    "Philippines": 0.452,  # Turbulent rank 31
    "Afghanistan": 0.45,  # Turbulent rank 32
    "Trinidad and Tobago": 0.45,  # Turbulent rank 32
    "Venezuela": 0.447,  # Turbulent rank 34
    "Libya": 0.445,  # Turbulent rank 35
    "Niger": 0.444,  # Turbulent rank 36
    "Burkina Faso": 0.442,  # Turbulent rank 37
    "Puerto Rico": 0.44,  # Turbulent rank 38
    "Mozambique": 0.439,  # Turbulent rank 39
    "Iran": 0.437,  # Turbulent rank 40
    "Uganda": 0.435,  # Turbulent rank 41
    "Israel": 0.434,  # Turbulent rank 42
    "Peru": 0.432,  # Turbulent rank 43
    "Ghana": 0.431,  # Turbulent rank 44
    "Indonesia": 0.429,  # Turbulent rank 45
    "Chile": 0.427,  # Turbulent rank 46
    "South Africa": 0.426,  # Turbulent rank 47
    "Nepal": 0.424,  # Turbulent rank 48
    "Belize": 0.423,  # Turbulent rank 49
    "Chad": 0.421,  # Turbulent rank 50
    "United States": 0.169,  # Low/Inactive rank 51
    "Bolivia": 0.168,  # Low/Inactive rank 52
    "Tanzania": 0.166,  # Low/Inactive rank 53
    "Benin": 0.165,  # Low/Inactive rank 54
    "Greece": 0.163,  # Low/Inactive rank 55
    "Madagascar": 0.163,  # Low/Inactive rank 55
    "Angola": 0.16,  # Low/Inactive rank 57
    "Malawi": 0.158,  # Low/Inactive rank 58
    "Germany": 0.156,  # Low/Inactive rank 59
    "France": 0.155,  # Low/Inactive rank 60
    "Turkey": 0.153,  # Low/Inactive rank 61
    "Sri Lanka": 0.152,  # Low/Inactive rank 62
    "Egypt": 0.15,  # Low/Inactive rank 63
    "Guinea": 0.15,  # Low/Inactive rank 63
    "Ivory Coast": 0.147,  # Low/Inactive rank 65
    "Papua New Guinea": 0.145,  # Low/Inactive rank 66
    "Morocco": 0.144,  # Low/Inactive rank 67
    "Zambia": 0.142,  # Low/Inactive rank 68
    "Dominican Republic": 0.14,  # Low/Inactive rank 69
    "Thailand": 0.139,  # Low/Inactive rank 70
    "Algeria": 0.137,  # Low/Inactive rank 71
    "Serbia": 0.135,  # Low/Inactive rank 72
    "Cyprus": 0.134,  # Low/Inactive rank 73
    "Liberia": 0.134,  # Low/Inactive rank 73
    "El Salvador": 0.131,  # Low/Inactive rank 75
    "China": 0.129,  # Low/Inactive rank 76
    "Zimbabwe": 0.127,  # Low/Inactive rank 77
    "Georgia": 0.126,  # Low/Inactive rank 78
    "Nicaragua": 0.124,  # Low/Inactive rank 79
    "Kyrgyzstan": 0.123,  # Low/Inactive rank 80
    "Senegal": 0.121,  # Low/Inactive rank 81
    "Togo": 0.121,  # Low/Inactive rank 81
    "Cuba": 0.118,  # Low/Inactive rank 83
    "Costa Rica": 0.116,  # Low/Inactive rank 84
    "Kazakhstan": 0.115,  # Low/Inactive rank 85
    "Rwanda": 0.113,  # Low/Inactive rank 86
    "Guyana": 0.111,  # Low/Inactive rank 87
    "Sierra Leone": 0.11,  # Low/Inactive rank 88
    "Bosnia and Herzegovina": 0.108,  # Low/Inactive rank 89
    "Spain": 0.106,  # Low/Inactive rank 90
    "United Kingdom": 0.105,  # Low/Inactive rank 91
    "Argentina": 0.103,  # Low/Inactive rank 92
    "Uzbekistan": 0.102,  # Low/Inactive rank 93
    "Azerbaijan": 0.1,  # Low/Inactive rank 94
    "eSwatini": 0.098,  # Low/Inactive rank 95
    "Hungary": 0.097,  # Low/Inactive rank 96
    "Republic of Congo": 0.097,  # Low/Inactive rank 96
    "Montenegro": 0.094,  # Low/Inactive rank 98
    "Mauritania": 0.092,  # Low/Inactive rank 99
    "Italy": 0.09,  # Low/Inactive rank 100
    "Moldova": 0.089,  # Low/Inactive rank 101
    "Belarus": 0.087,  # Low/Inactive rank 102
    "Poland": 0.085,  # Low/Inactive rank 103
    "Romania": 0.085,  # Low/Inactive rank 103
    "Czech Republic": 0.082,  # Low/Inactive rank 105
    "Mauritius": 0.081,  # Low/Inactive rank 106
    "Tunisia": 0.079,  # Low/Inactive rank 107
    "Botswana": 0.077,  # Low/Inactive rank 108
    "Netherlands": 0.076,  # Low/Inactive rank 109
    "North Macedonia": 0.074,  # Low/Inactive rank 110
    "Bahrain": 0.073,  # Low/Inactive rank 111
    "Jordan": 0.073,  # Low/Inactive rank 111
    "Paraguay": 0.069,  # Low/Inactive rank 113
    "Kosovo": 0.068,  # Low/Inactive rank 114
    "Armenia": 0.066,  # Low/Inactive rank 115
    "Panama": 0.065,  # Low/Inactive rank 116
    "Slovakia": 0.063,  # Low/Inactive rank 117
    "Austria": 0.061,  # Low/Inactive rank 118
    "Namibia": 0.061,  # Low/Inactive rank 118
    "Norway": 0.061,  # Low/Inactive rank 118
    "Malaysia": 0.056,  # Low/Inactive rank 121
    "Gabon": 0.055,  # Low/Inactive rank 122
    "United Arab Emirates": 0.053,  # Low/Inactive rank 123
    "Qatar": 0.052,  # Low/Inactive rank 124
    "Tajikistan": 0.05,  # Low/Inactive rank 125
    "Croatia": 0.048,  # Low/Inactive rank 126
    "Latvia": 0.048,  # Low/Inactive rank 126
    "Canada": 0.045,  # Low/Inactive rank 128
    "Comoros": 0.044,  # Low/Inactive rank 129
    "Portugal": 0.042,  # Low/Inactive rank 130
    "Suriname": 0.042,  # Low/Inactive rank 130
    "Sweden": 0.039,  # Low/Inactive rank 132
    "Belgium": 0.037,  # Low/Inactive rank 133
    "Malta": 0.035,  # Low/Inactive rank 134
    "Slovenia": 0.034,  # Low/Inactive rank 135
    "Bulgaria": 0.032,  # Low/Inactive rank 136
    "Saudi Arabia": 0.032,  # Low/Inactive rank 136
    "Laos": 0.029,  # Low/Inactive rank 138
    "Mayotte": 0.027,  # Low/Inactive rank 139
    "Albania": 0.026,  # Low/Inactive rank 140
    "East Timor": 0.026,  # Low/Inactive rank 140
    "Gambia": 0.026,  # Low/Inactive rank 140
    "Guinea-Bissau": 0.026,  # Low/Inactive rank 140
    "Ireland": 0.026,  # Low/Inactive rank 140
    "Antigua and Barbuda": 0.018,  # Low/Inactive rank 145
    "Aruba": 0.018,  # Low/Inactive rank 145
    "North Korea": 0.018,  # Low/Inactive rank 145
    "Australia": 0.013,  # Low/Inactive rank 148
    "Cambodia": 0.013,  # Low/Inactive rank 148
    "Turkmenistan": 0.013,  # Low/Inactive rank 148
    "Bahamas": 0.008,  # Low/Inactive rank 151
    "Lithuania": 0.008,  # Low/Inactive rank 151
    "Martinique": 0.008,  # Low/Inactive rank 151
    "South Korea": 0.008,  # Low/Inactive rank 151
    "Switzerland": 0.008,  # Low/Inactive rank 151
    "Akrotiri and Dhekelia": 0.0,  # Low/Inactive rank 156
    "American Samoa": 0.0,  # Low/Inactive rank 156
    "Andorra": 0.0,  # Low/Inactive rank 156
    "Anguilla": 0.0,  # Low/Inactive rank 156
    "Antarctica": 0.0,  # Low/Inactive rank 156
    "Bailiwick of Guernsey": 0.0,  # Low/Inactive rank 156
    "Bailiwick of Jersey": 0.0,  # Low/Inactive rank 156
    "Barbados": 0.0,  # Low/Inactive rank 156
    "Bermuda": 0.0,  # Low/Inactive rank 156
    "Bhutan": 0.0,  # Low/Inactive rank 156
    "British Indian Ocean Territory": 0.0,  # Low/Inactive rank 156
    "British Virgin Islands": 0.0,  # Low/Inactive rank 156
    "Brunei": 0.0,  # Low/Inactive rank 156
    "Cape Verde": 0.0,  # Low/Inactive rank 156
    "Caribbean Netherlands": 0.0,  # Low/Inactive rank 156
    "Cayman Islands": 0.0,  # Low/Inactive rank 156
    "Christmas Island": 0.0,  # Low/Inactive rank 156
    "Cocos (Keeling) Islands": 0.0,  # Low/Inactive rank 156
    "Cook Islands": 0.0,  # Low/Inactive rank 156
    "Curacao": 0.0,  # Low/Inactive rank 156
    "Denmark": 0.0,  # Low/Inactive rank 156
    "Djibouti": 0.0,  # Low/Inactive rank 156
    "Dominica": 0.0,  # Low/Inactive rank 156
    "Equatorial Guinea": 0.0,  # Low/Inactive rank 156
    "Eritrea": 0.0,  # Low/Inactive rank 156
    "Estonia": 0.0,  # Low/Inactive rank 156
    "Falkland Islands": 0.0,  # Low/Inactive rank 156
    "Faroe Islands": 0.0,  # Low/Inactive rank 156
    "Fiji": 0.0,  # Low/Inactive rank 156
    "Finland": 0.0,  # Low/Inactive rank 156
    "French Guiana": 0.0,  # Low/Inactive rank 156
    "French Polynesia": 0.0,  # Low/Inactive rank 156
    "French Southern and Antarctic Lands": 0.0,  # Low/Inactive rank 156
    "Gibraltar": 0.0,  # Low/Inactive rank 156
    "Greenland": 0.0,  # Low/Inactive rank 156
    "Grenada": 0.0,  # Low/Inactive rank 156
    "Guadeloupe": 0.0,  # Low/Inactive rank 156
    "Guam": 0.0,  # Low/Inactive rank 156
    "Heard Island and McDonald Islands": 0.0,  # Low/Inactive rank 156
    "Iceland": 0.0,  # Low/Inactive rank 156
    "Isle of Man": 0.0,  # Low/Inactive rank 156
    "Japan": 0.0,  # Low/Inactive rank 156
    "Kiribati": 0.0,  # Low/Inactive rank 156
    "Kuwait": 0.0,  # Low/Inactive rank 156
    "Lesotho": 0.0,  # Low/Inactive rank 156
    "Liechtenstein": 0.0,  # Low/Inactive rank 156
    "Luxembourg": 0.0,  # Low/Inactive rank 156
    "Maldives": 0.0,  # Low/Inactive rank 156
    "Marshall Islands": 0.0,  # Low/Inactive rank 156
    "Micronesia": 0.0,  # Low/Inactive rank 156
    "Monaco": 0.0,  # Low/Inactive rank 156
    "Mongolia": 0.0,  # Low/Inactive rank 156
    "Montserrat": 0.0,  # Low/Inactive rank 156
    "Nauru": 0.0,  # Low/Inactive rank 156
    "New Caledonia": 0.0,  # Low/Inactive rank 156
    "New Zealand": 0.0,  # Low/Inactive rank 156
    "Niue": 0.0,  # Low/Inactive rank 156
    "Norfolk Island": 0.0,  # Low/Inactive rank 156
    "Northern Mariana Islands": 0.0,  # Low/Inactive rank 156
    "Oman": 0.0,  # Low/Inactive rank 156
    "Palau": 0.0,  # Low/Inactive rank 156
    "Pitcairn": 0.0,  # Low/Inactive rank 156
    "Reunion": 0.0,  # Low/Inactive rank 156
    "Saint Helena, Ascension and Tristan da Cunha": 0.0,  # Low/Inactive rank 156
    "Saint Kitts and Nevis": 0.0,  # Low/Inactive rank 156
    "Saint Lucia": 0.0,  # Low/Inactive rank 156
    "Saint Pierre and Miquelon": 0.0,  # Low/Inactive rank 156
    "Saint Vincent and the Grenadines": 0.0,  # Low/Inactive rank 156
    "Saint-Barthelemy": 0.0,  # Low/Inactive rank 156
    "Saint-Martin": 0.0,  # Low/Inactive rank 156
    "Samoa": 0.0,  # Low/Inactive rank 156
    "San Marino": 0.0,  # Low/Inactive rank 156
    "Sao Tome and Principe": 0.0,  # Low/Inactive rank 156
    "Seychelles": 0.0,  # Low/Inactive rank 156
    "Singapore": 0.0,  # Low/Inactive rank 156
    "Sint Maarten": 0.0,  # Low/Inactive rank 156
    "Solomon Islands": 0.0,  # Low/Inactive rank 156
    "South Georgia and the South Sandwich Islands": 0.0,  # Low/Inactive rank 156
    "Taiwan": 0.0,  # Low/Inactive rank 156
    "Tokelau": 0.0,  # Low/Inactive rank 156
    "Tonga": 0.0,  # Low/Inactive rank 156
    "Turks and Caicos Islands": 0.0,  # Low/Inactive rank 156
    "Tuvalu": 0.0,  # Low/Inactive rank 156
    "United States Minor Outlying Islands": 0.0,  # Low/Inactive rank 156
    "Uruguay": 0.0,  # Low/Inactive rank 156
    "Vanuatu": 0.0,  # Low/Inactive rank 156
    "Vietnam": 0.0,  # Low/Inactive rank 156
    "Virgin Islands, U.S.": 0.0,  # Low/Inactive rank 156
    "Wallis and Futuna": 0.0,  # Low/Inactive rank 156
}

# ─── ISO alpha-2 → ACLED страна ──────────────────────────────────────────────
_ISO2_TO_ACLED: dict[str, str] = {
    "af": "Afghanistan", "al": "Albania", "dz": "Algeria", "ao": "Angola",
    "ar": "Argentina", "am": "Armenia", "au": "Australia", "at": "Austria",
    "az": "Azerbaijan", "bd": "Bangladesh", "by": "Belarus", "be": "Belgium",
    "bj": "Benin", "bo": "Bolivia", "ba": "Bosnia-Herzegovina", "br": "Brazil",
    "bf": "Burkina Faso", "bi": "Burundi", "kh": "Cambodia", "cm": "Cameroon",
    "ca": "Canada", "cf": "Central African Republic", "td": "Chad", "cl": "Chile",
    "cn": "China", "co": "Colombia", "cd": "Democratic Republic of Congo",
    "cg": "Republic of Congo", "cr": "Costa Rica", "hr": "Croatia", "cu": "Cuba",
    "cz": "Czechia", "dk": "Denmark", "do": "Dominican Republic", "ec": "Ecuador",
    "eg": "Egypt", "sv": "El Salvador", "er": "Eritrea", "et": "Ethiopia",
    "fi": "Finland", "fr": "France", "ga": "Gabon", "ge": "Georgia",
    "de": "Germany", "gh": "Ghana", "gr": "Greece", "gt": "Guatemala",
    "gn": "Guinea", "gw": "Guinea-Bissau", "ht": "Haiti", "hn": "Honduras",
    "hu": "Hungary", "in": "India", "id": "Indonesia", "ir": "Iran",
    "iq": "Iraq", "il": "Israel", "it": "Italy", "jm": "Jamaica",
    "jp": "Japan", "jo": "Jordan", "kz": "Kazakhstan", "ke": "Kenya",
    "kp": "North Korea", "kr": "South Korea", "kw": "Kuwait", "kg": "Kyrgyzstan",
    "la": "Laos", "lb": "Lebanon", "lr": "Liberia", "ly": "Libya",
    "lt": "Lithuania", "lv": "Latvia", "mk": "North Macedonia", "mg": "Madagascar",
    "mw": "Malawi", "my": "Malaysia", "ml": "Mali", "mr": "Mauritania",
    "mx": "Mexico", "md": "Moldova", "mn": "Mongolia", "ma": "Morocco",
    "mz": "Mozambique", "mm": "Myanmar", "na": "Namibia", "np": "Nepal",
    "nl": "Netherlands", "nz": "New Zealand", "ni": "Nicaragua", "ne": "Niger",
    "ng": "Nigeria", "no": "Norway", "om": "Oman", "pk": "Pakistan",
    "ps": "Palestine", "pa": "Panama", "pg": "Papua New Guinea", "py": "Paraguay",
    "pe": "Peru", "ph": "Philippines", "pl": "Poland", "pt": "Portugal",
    "qa": "Qatar", "ro": "Romania", "ru": "Russia", "rw": "Rwanda",
    "sa": "Saudi Arabia", "sn": "Senegal", "rs": "Serbia", "sl": "Sierra Leone",
    "sg": "Singapore", "sk": "Slovakia", "so": "Somalia", "za": "South Africa",
    "ss": "South Sudan", "es": "Spain", "lk": "Sri Lanka", "sd": "Sudan",
    "se": "Sweden", "ch": "Switzerland", "sy": "Syria", "tw": "Taiwan",
    "tj": "Tajikistan", "tz": "Tanzania", "th": "Thailand", "tl": "Timor-Leste",
    "tg": "Togo", "tn": "Tunisia", "tr": "Turkey", "tm": "Turkmenistan",
    "ug": "Uganda", "ua": "Ukraine", "ae": "United Arab Emirates",
    "gb": "United Kingdom", "us": "United States", "uy": "Uruguay",
    "uz": "Uzbekistan", "ve": "Venezuela", "vn": "Vietnam", "ye": "Yemen",
    "zm": "Zambia", "zw": "Zimbabwe",
}

# ─── Маппинг русских/альтернативных названий стран → ACLED ключ ───────────────
_COUNTRY_ALIASES: dict[str, str] = {
    "россия": "Russia", "украина": "Ukraine", "беларусь": "Belarus",
    "казахстан": "Kazakhstan", "узбекистан": "Uzbekistan",
    "туркменистан": "Turkmenistan", "кыргызстан": "Kyrgyzstan",
    "таджикистан": "Tajikistan", "азербайджан": "Azerbaijan",
    "грузия": "Georgia", "армения": "Armenia", "молдова": "Moldova",
    "китай": "China", "япония": "Japan", "южная корея": "South Korea",
    "северная корея": "North Korea", "сингапур": "Singapore",
    "таиланд": "Thailand", "вьетнам": "Vietnam", "индия": "India",
    "пакистан": "Pakistan", "бангладеш": "Bangladesh", "иран": "Iran",
    "ирак": "Iraq", "сирия": "Syria", "йемен": "Yemen",
    "германия": "Germany", "нидерланды": "Netherlands", "польша": "Poland",
    "франция": "France", "великобритания": "United Kingdom",
    "бельгия": "Belgium", "австрия": "Austria", "чехия": "Czechia",
    "венгрия": "Hungary", "румыния": "Romania", "финляндия": "Finland",
    "швеция": "Sweden", "норвегия": "Norway", "дания": "Denmark",
    "швейцария": "Switzerland", "латвия": "Latvia", "литва": "Lithuania",
    "эстония": "Estonia", "турция": "Turkey", "египет": "Egypt",
    "саудовская аравия": "Saudi Arabia", "оаэ": "United Arab Emirates",
    "сша": "United States", "канада": "Canada", "мексика": "Mexico",
    "бразилия": "Brazil", "аргентина": "Argentina", "чили": "Chile",
    "нигерия": "Nigeria", "кения": "Kenya", "эфиопия": "Ethiopia",
    "судан": "Sudan", "ливия": "Libya", "марокко": "Morocco",
    "алжир": "Algeria", "тунис": "Tunisia",
}

# ─── Быстрый словарь: город → ACLED страна (~150 городов) ────────────────────
_CITY_TO_COUNTRY: dict[str, str] = {
    # Россия
    "москва": "Russia", "moscow": "Russia",
    "санкт-петербург": "Russia", "saint petersburg": "Russia",
    "spb": "Russia", "питер": "Russia",
    "владивосток": "Russia", "vladivostok": "Russia",
    "новосибирск": "Russia", "novosibirsk": "Russia",
    "хабаровск": "Russia", "khabarovsk": "Russia",
    "иркутск": "Russia", "irkutsk": "Russia",
    "красноярск": "Russia", "krasnoyarsk": "Russia",
    "екатеринбург": "Russia", "yekaterinburg": "Russia",
    "казань": "Russia", "kazan": "Russia",
    "находка": "Russia", "nakhodka": "Russia",
    "омск": "Russia", "omsk": "Russia",
    "челябинск": "Russia", "chelyabinsk": "Russia",
    "калининград": "Russia", "kaliningrad": "Russia",
    # Китай
    "шанхай": "China", "shanghai": "China",
    "пекин": "China", "beijing": "China",
    "гуанчжоу": "China", "guangzhou": "China",
    "нинбо": "China", "ningbo": "China",
    "тяньцзинь": "China", "tianjin": "China",
    "чэнду": "China", "chengdu": "China",
    "иу": "China", "yiwu": "China",
    "харбин": "China", "harbin": "China",
    "урумчи": "China", "urumqi": "China",
    "далянь": "China", "dalian": "China",
    "циндао": "China", "qingdao": "China",
    "гонконг": "China", "hong kong": "China",
    "ухань": "China", "wuhan": "China",
    "сиань": "China", "xian": "China",
    "чунцин": "China", "chongqing": "China",
    "шэньчжэнь": "China", "shenzhen": "China",
    # СНГ
    "минск": "Belarus", "minsk": "Belarus",
    "алматы": "Kazakhstan", "almaty": "Kazakhstan",
    "астана": "Kazakhstan", "astana": "Kazakhstan",
    "актобе": "Kazakhstan", "aktobe": "Kazakhstan",
    "ташкент": "Uzbekistan", "tashkent": "Uzbekistan",
    "баку": "Azerbaijan", "baku": "Azerbaijan",
    "тбилиси": "Georgia", "tbilisi": "Georgia",
    "ереван": "Armenia", "yerevan": "Armenia",
    "бишкек": "Kyrgyzstan", "bishkek": "Kyrgyzstan",
    "душанбе": "Tajikistan", "dushanbe": "Tajikistan",
    "ашхабад": "Turkmenistan", "ashgabat": "Turkmenistan",
    "кишинев": "Moldova", "chisinau": "Moldova",
    "киев": "Ukraine", "kyiv": "Ukraine", "kiev": "Ukraine",
    "одесса": "Ukraine", "odessa": "Ukraine",
    # Европа
    "берлин": "Germany", "berlin": "Germany",
    "гамбург": "Germany", "hamburg": "Germany",
    "мюнхен": "Germany", "munich": "Germany",
    "варшава": "Poland", "warsaw": "Poland",
    "гданьск": "Poland", "gdansk": "Poland",
    "прага": "Czechia", "prague": "Czechia",
    "вена": "Austria", "vienna": "Austria",
    "роттердам": "Netherlands", "rotterdam": "Netherlands",
    "амстердам": "Netherlands", "amsterdam": "Netherlands",
    "антверпен": "Belgium", "antwerp": "Belgium",
    "брюссель": "Belgium", "brussels": "Belgium",
    "париж": "France", "paris": "France",
    "марсель": "France", "marseille": "France",
    "лондон": "United Kingdom", "london": "United Kingdom",
    "фелькстон": "United Kingdom", "felixstowe": "United Kingdom",
    "хельсинки": "Finland", "helsinki": "Finland",
    "рига": "Latvia", "riga": "Latvia",
    "вильнюс": "Lithuania", "vilnius": "Lithuania",
    "таллин": "Estonia", "tallinn": "Estonia",
    "стамбул": "Turkey", "istanbul": "Turkey",
    "стокгольм": "Sweden", "stockholm": "Sweden",
    "осло": "Norway", "oslo": "Norway",
    "копенгаген": "Denmark", "copenhagen": "Denmark",
    "будапешт": "Hungary", "budapest": "Hungary",
    "бухарест": "Romania", "bucharest": "Romania",
    "барселона": "Spain", "barcelona": "Spain",
    "мадрид": "Spain", "madrid": "Spain",
    "лиссабон": "Portugal", "lisbon": "Portugal",
    "милан": "Italy", "milan": "Italy",
    "генуя": "Italy", "genoa": "Italy",
    "пирей": "Greece", "piraeus": "Greece",
    "афины": "Greece", "athens": "Greece",
    "брест": "Belarus", "brest by": "Belarus",
    "малашевиче": "Poland", "malaszewicze": "Poland",
    # Азия
    "токио": "Japan", "tokyo": "Japan",
    "осака": "Japan", "osaka": "Japan",
    "сеул": "South Korea", "seoul": "South Korea",
    "пусан": "South Korea", "busan": "South Korea",
    "сингапур": "Singapore", "singapore": "Singapore",
    "бангкок": "Thailand", "bangkok": "Thailand",
    "хошимин": "Vietnam", "ho chi minh": "Vietnam",
    "ханой": "Vietnam", "hanoi": "Vietnam",
    "джакарта": "Indonesia", "jakarta": "Indonesia",
    "куала-лумпур": "Malaysia", "kuala lumpur": "Malaysia",
    "порт-кланг": "Malaysia", "port klang": "Malaysia",
    "мумбай": "India", "mumbai": "India",
    "дели": "India", "delhi": "India",
    "ченнаи": "India", "chennai": "India",
    "карачи": "Pakistan", "karachi": "Pakistan",
    "дакка": "Bangladesh", "dhaka": "Bangladesh",
    # Ближний Восток
    "дубай": "United Arab Emirates", "dubai": "United Arab Emirates",
    "абу-даби": "United Arab Emirates", "abu dhabi": "United Arab Emirates",
    "джидда": "Saudi Arabia", "jeddah": "Saudi Arabia",
    "эр-рияд": "Saudi Arabia", "riyadh": "Saudi Arabia",
    "доха": "Qatar", "doha": "Qatar",
    "бейрут": "Lebanon", "beirut": "Lebanon",
    "тегеран": "Iran", "tehran": "Iran",
    # Африка
    "каир": "Egypt", "cairo": "Egypt",
    "александрия": "Egypt", "alexandria": "Egypt",
    "момбаса": "Kenya", "mombasa": "Kenya",
    "найроби": "Kenya", "nairobi": "Kenya",
    "дар-эс-салам": "Tanzania", "dar es salaam": "Tanzania",
    "лагос": "Nigeria", "lagos": "Nigeria",
    "касабланка": "Morocco", "casablanca": "Morocco",
    "дурбан": "South Africa", "durban": "South Africa",
    "кейптаун": "South Africa", "cape town": "South Africa",
    # Америка
    "нью-йорк": "United States", "new york": "United States",
    "лос-анджелес": "United States", "los angeles": "United States",
    "long beach": "United States",
    "хьюстон": "United States", "houston": "United States",
    "сиэтл": "United States", "seattle": "United States",
    "ванкувер": "Canada", "vancouver": "Canada",
    "монреаль": "Canada", "montreal": "Canada",
    "буэнос-айрес": "Argentina", "buenos aires": "Argentina",
    "сантьяго": "Chile", "santiago": "Chile",
}

# ─── Координатные боксы регионов (последний фоллбэк) ─────────────────────────
_REGION_BOXES: list[tuple[str, tuple, float]] = [
    ("western_europe",  (36,  71,  -10,  20), 0.10),
    ("eastern_europe",  (44,  71,   20,  40), 0.30),
    ("central_asia",    (35,  55,   40,  90), 0.32),
    ("east_asia",       (18,  55,   90, 145), 0.18),
    ("southeast_asia",  (-10, 28,   95, 145), 0.35),
    ("south_asia",      (5,   38,   60,  95), 0.50),
    ("middle_east",     (12,  42,   25,  65), 0.55),
    ("north_africa",    (15,  38,  -18,  40), 0.40),
    ("sub_saharan",     (-35, 15,  -18,  52), 0.62),
    ("north_america",   (15,  72, -170, -52), 0.20),
    ("latin_america",   (-56, 15,  -82, -34), 0.50),
    ("oceania",         (-50,  0,  110, 180), 0.08),
]

# ─── Кэш геокодирования (город → страна, живёт всё время работы сервера) ─────
_geocache: dict[str, str] = {}

# ─── Nominatim API ────────────────────────────────────────────────────────────
_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_NOMINATIM_TIMEOUT = 6.0


async def _nominatim_lookup(city: str) -> str | None:
    """
    Запрашивает Nominatim (OpenStreetMap) для определения страны по названию города.
    Возвращает ACLED-ключ страны или None если не удалось.
    """
    try:
        async with httpx.AsyncClient(timeout=_NOMINATIM_TIMEOUT) as client:
            resp = await client.get(
                _NOMINATIM_URL,
                params={
                    "q":             city,
                    "format":        "json",
                    "limit":         1,
                    "addressdetails": 1,
                },
                headers={"User-Agent": "UTLC-ERA-logistics/2.0 (route risk analysis)"},
            )
            if resp.status_code != 200:
                return None

            results = resp.json()
            if not results:
                return None

            address      = results[0].get("address", {})
            country_code = address.get("country_code", "").lower()
            country_name = address.get("country", "")

            # 1. ISO код → ACLED
            if country_code in _ISO2_TO_ACLED:
                acled_key = _ISO2_TO_ACLED[country_code]
                if acled_key in _ACLED_RISK:
                    return acled_key

            # 2. Название страны напрямую → ACLED
            if country_name in _ACLED_RISK:
                return country_name

            # 3. Через алиасы
            alias = _COUNTRY_ALIASES.get(country_name.lower())
            if alias and alias in _ACLED_RISK:
                return alias

    except Exception:
        pass

    return None


def _coords_fallback(city: str) -> tuple[float, str]:
    """Определение риска по координатам города (последний резерв)."""
    coords = get_coords(city)
    if coords:
        lat, lon = coords
        for region, (lat_min, lat_max, lon_min, lon_max), default_risk in _REGION_BOXES:
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return default_risk, f"region:{region}"
    return 0.30, "unknown"


def _fast_lookup(city: str) -> str | None:
    """
    Быстрый синхронный поиск: словарь городов + алиасы стран.
    Возвращает ACLED-ключ или None.
    """
    key = city.lower().strip()

    # 1. Словарь городов
    country = _CITY_TO_COUNTRY.get(key)
    if country and country in _ACLED_RISK:
        return country

    # 2. Может это сама страна?
    if city in _ACLED_RISK:
        return city

    # 3. Алиасы стран
    alias = _COUNTRY_ALIASES.get(key)
    if alias and alias in _ACLED_RISK:
        return alias

    return None


async def get_city_risk(city: str) -> tuple[float, str]:
    """
    Определяет риск города [0..1] + название страны.

    Порядок поиска:
      1. Кэш (мгновенно)
      2. Словарь ~200 городов (мгновенно)
      3. Nominatim API (OpenStreetMap, ~0.5с, бесплатно)
      4. Координаты + региональные боксы (мгновенно)
    """
    key = city.lower().strip()

    # 1. Кэш
    if key in _geocache:
        cached = _geocache[key]
        return _ACLED_RISK.get(cached, 0.30), cached

    # 2. Быстрый словарь
    acled_key = _fast_lookup(city)
    if acled_key:
        _geocache[key] = acled_key
        return _ACLED_RISK[acled_key], acled_key

    # 3. Nominatim API
    acled_key = await _nominatim_lookup(city)
    if acled_key:
        _geocache[key] = acled_key
        return _ACLED_RISK[acled_key], acled_key

    # 4. Координатный фоллбэк
    risk, region = _coords_fallback(city)
    _geocache[key] = region
    return risk, region


async def get_route_geo_risk(origin: str, destination: str) -> dict:
    """
    Геополитический риск маршрута на основе ACLED Conflict Index 2025.

    Алгоритм:
      1. Определяем страны точек A и B (словарь → Nominatim → координаты)
      2. Берём риски обеих стран из ACLED
      3. Итог = max × 0.6 + min × 0.4
         (маршрут настолько опасен, насколько опасна самая опасная точка,
          но и менее опасная точка тоже вносит вклад)
    """
    risk_from, country_from = await get_city_risk(origin)
    risk_to,   country_to   = await get_city_risk(destination)

    risk_max = max(risk_from, risk_to)
    risk_min = min(risk_from, risk_to)
    geo_risk = round(risk_max * 0.6 + risk_min * 0.4, 3)

    def level(r: float) -> str:
        if r >= 0.75: return "Extreme"
        if r >= 0.50: return "High"
        if r >= 0.25: return "Turbulent"
        return "Low"

    return {
        "geopolitical_risk_index": geo_risk,
        "origin_risk":             risk_from,
        "destination_risk":        risk_to,
        "origin_country":          country_from,
        "destination_country":     country_to,
        "origin_level":            level(risk_from),
        "destination_level":       level(risk_to),
        "source":                  "ACLED Conflict Index 2025 + Nominatim",
    }
