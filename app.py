import requests
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "travel_secret_key"

WEATHER_API_KEY = "7d15c080a8db73ad404c0b052b08d419"
DB_NAME = "travel.db"

# ================= DATABASE =================
def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= FULL TRAVEL DATA (ALL YOUR CITIES) =================
travel_data = [
    ("Delhi", "Delhi", 2500, "India Gate, Red Fort, Qutub Minar, Lotus Temple, Humayun's Tomb, Jama Masjid, Chandni Chowk"),
    ("Agra", "Uttar Pradesh", 2800, "Taj Mahal, Agra Fort, Fatehpur Sikri, Itmad-ud-Daulah, Mehtab Bagh"),
    ("Jaipur", "Rajasthan", 3200, "Amber Fort, City Palace, Hawa Mahal, Jantar Mantar, Nahargarh Fort, Jaigarh Fort"),
    ("Shimla", "Himachal Pradesh", 2200, "The Ridge, Mall Road, Jakhoo Temple, Christ Church, Kufri, Viceregal Lodge"),
    ("Manali", "Himachal Pradesh", 2500, "Rohtang Pass, Solang Valley, Hadimba Temple, Old Manali, Vashisht Hot Springs, Jogini Falls"),
    ("Dharamshala", "Himachal Pradesh", 2400, "McLeod Ganj, Triund Trek, Dalai Lama Temple, Bhagsu Waterfall, Namgyal Monastery"),
    ("Amritsar", "Punjab", 2000, "Golden Temple, Jallianwala Bagh, Wagah Border, Durgiana Temple, Partition Museum"),
    ("Srinagar", "Jammu and Kashmir", 3000, "Dal Lake, Mughal Gardens, Shankaracharya Temple, Houseboats, Pari Mahal"),
    ("Leh", "Ladakh", 4000, "Pangong Lake, Nubra Valley, Magnetic Hill, Shanti Stupa, Leh Palace, Hemis Monastery"),
    ("Varanasi", "Uttar Pradesh", 1800, "Kashi Vishwanath Temple, Dashashwamedh Ghat, Manikarnika Ghat, Sarnath, Assi Ghat"),
    ("Udaipur", "Rajasthan", 3100, "City Palace, Lake Pichola, Jag Mandir, Saheliyon Ki Bari, Fateh Sagar Lake"),
    ("Jodhpur", "Rajasthan", 3000, "Mehrangarh Fort, Umaid Bhawan Palace, Jaswant Thada, Mandore Gardens, Rao Jodha Desert Park"),
    ("Ranthambore", "Rajasthan", 2900, "Ranthambore National Park, Ranthambore Fort, Trinetra Ganesh Temple"),
    ("Kullu", "Himachal Pradesh", 2300, "Great Himalayan National Park, Bijli Mahadev Temple, Raghunath Temple, Sultanpur Palace"),
    ("Dalhousie", "Himachal Pradesh", 2400, "Khajjiar, Dainkund Peak, Kalatop Wildlife Sanctuary, Chamera Lake"),
    ("Mussoorie", "Uttarakhand", 2100, "Kempty Falls, Gun Hill, Camel’s Back Road, Lal Tibba, Cloud's End"),
    ("Nainital", "Uttarakhand", 2200, "Naini Lake, Snow View Point, Naina Devi Temple, Tiffin Top, Eco Cave Gardens"),
    ("Haridwar", "Uttarakhand", 1900, "Har Ki Pauri, Mansa Devi Temple, Chandi Devi Temple, Ganga Aarti"),
    ("Rishikesh", "Uttarakhand", 2000, "Laxman Jhula, Ram Jhula, Triveni Ghat, Beatles Ashram, Rafting Spots"),
    ("Gulmarg", "Jammu and Kashmir", 3200, "Gondola Ride, Apharwat Peak, Alpather Lake, Golf Course"),
    ("Pahalgam", "Jammu and Kashmir", 2800, "Betaab Valley, Aru Valley, Lidder River, Baisaran Valley"),
    ("Sonmarg", "Jammu and Kashmir", 3000, "Thajiwas Glacier, Vishansar Lake, Zoji La Pass"),
    ("Jammu", "Jammu and Kashmir", 1700, "Vaishno Devi Temple, Bahu Fort, Mubarak Mandi Palace, Raghunath Temple"),
    ("Pushkar", "Rajasthan", 2600, "Pushkar Lake, Brahma Temple, Savitri Temple, Camel Fair"),
    ("Ajmer", "Rajasthan", 2700, "Ajmer Sharif Dargah, Ana Sagar Lake, Taragarh Fort"),
    ("Mount Abu", "Rajasthan", 2800, "Dilwara Jain Temples, Nakki Lake, Guru Shikhar, Sunset Point"),
    ("Chandigarh", "Chandigarh", 1800, "Rock Garden, Sukhna Lake, Rose Garden, Capitol Complex"),
    ("Kasol", "Himachal Pradesh", 2500, "Parvati Valley, Kheerganga Trek, Tosh Village, Malana"),
    ("Khajjiar", "Himachal Pradesh", 2400, "Khajjiar Lake, Kalatop Wildlife Sanctuary, Golden Devi Temple"),
    ("Spiti Valley", "Himachal Pradesh", 3800, "Key Monastery, Tabo Monastery, Chandratal Lake, Pin Valley National Park"),
    ("Kasauli", "Himachal Pradesh", 2200, "Monkey Point, Christ Church, Sunset Point, Brewery"),
    ("Almora", "Uttarakhand", 2100, "Bright End Corner, Kasar Devi Temple, Jageshwar Temple"),
    ("Auli", "Uttarakhand", 3000, "Auli Ski Resort, Gorson Bugyal, Trishul Peak"),
    ("Jim Corbett", "Uttarakhand", 1700, "Jim Corbett National Park, Corbett Falls, Garjia Temple"),
    ("Mathura", "Uttar Pradesh", 1600, "Krishna Janmabhoomi Temple, Vishram Ghat, Dwarkadhish Temple"),
    ("Vrindavan", "Uttar Pradesh", 1600, "Banke Bihari Temple, ISKCON Temple, Prem Mandir"),
    ("Chamba", "Himachal Pradesh", 2300, "Laxmi Narayan Temple, Bhuri Singh Museum, Chamera Lake"),
    ("Bir Billing", "Himachal Pradesh", 2600, "Paragliding Site, Billing Valley, Tibetan Monasteries"),
    ("Patnitop", "Jammu and Kashmir", 2200, "Nathatop, Sanasar Lake, Naag Mandir"),
    ("Dhanaulti", "Uttarakhand", 2300, "Eco Park, Surkanda Devi Temple, Potato Farm"),
    ("Lansdowne", "Uttarakhand", 2000, "Bhulla Lake, Tip N Top, St. Mary's Church"),
    ("Badrinath", "Uttarakhand", 3200, "Badrinath Temple, Mana Village, Tapt Kund"),
    ("Kedarnath", "Uttarakhand", 3500, "Kedarnath Temple, Vasuki Tal, Gandhi Sarovar"),
    ("Gangotri", "Uttarakhand", 3100, "Gangotri Temple, Gaumukh Glacier"),
    ("Yamunotri", "Uttarakhand", 3200, "Yamunotri Temple, Surya Kund"),
    ("Vaishno Devi", "Jammu and Kashmir", 2000, "Vaishno Devi Temple, Bhairo Baba Temple, Ardh Kuwari"),
    ("McLeod Ganj", "Himachal Pradesh", 2400, "Tsuglagkhang Complex, Namgyal Monastery, Triund Trek"),
    ("Palampur", "Himachal Pradesh", 2200, "Tea Gardens, Neugal Khad, Saurabh Van Vihar"),
    ("Kangra", "Himachal Pradesh", 2100, "Kangra Fort, Bajreshwari Temple, Masroor Rock Temples"),
    ("Narkanda", "Himachal Pradesh", 2700, "Hatu Peak, Tannu Jubbar Lake, Skiing Slopes"),
    ("Tirthan Valley", "Himachal Pradesh", 2400, "Great Himalayan National Park, Serolsar Lake, Chhoie Waterfall"),
    ("Jibhi", "Himachal Pradesh", 2300, "Jibhi Waterfall, Chaini Fort, Chehni Kothi"),
    ("Barot", "Himachal Pradesh", 2200, "Uhl River, Trout Fishing, Nargu Wildlife Sanctuary"),
    ("Prashar Lake", "Himachal Pradesh", 2800, "Prashar Lake Trek, Prashar Rishi Temple"),
    ("Triund", "Himachal Pradesh", 2800, "Triund Trek, Snowline Trek, Indrahar Pass"),
    ("Kufri", "Himachal Pradesh", 2500, "Kufri Fun World, Mahasu Peak, Himalayan Nature Park"),
    ("Chail", "Himachal Pradesh", 2400, "Chail Palace, Cricket Ground, Kali Tibba Temple"),
    ("Solan", "Himachal Pradesh", 2100, "Shoolini Mata Temple, Mohan Shakti National Park"),
    ("Ranikhet", "Uttarakhand", 2200, "Jhula Devi Temple, Chaubatia Gardens, Golf Course"),
    ("Kausani", "Uttarakhand", 2300, "Baijnath Temple, Anashakti Ashram, Tea Estates"),
    ("Binsar", "Uttarakhand", 2400, "Binsar Wildlife Sanctuary, Zero Point, Bineshwar Temple"),
    ("Mukteshwar", "Uttarakhand", 2400, "Mukteshwar Temple, Chauli Ki Jali, Rock Climbing"),
    ("Pithoragarh", "Uttarakhand", 2000, "Pithoragarh Fort, Kapileshwar Mahadev Temple"),
    ("Chamoli", "Uttarakhand", 2800, "Valley of Flowers, Hemkund Sahib, Auli"),
    ("Rudraprayag", "Uttarakhand", 2200, "Koteshwar Temple, Rudranath Temple"),
    ("Pauri", "Uttarakhand", 2100, "Kandoliya Temple, Kyunkaleshwar Temple"),
    ("Tehri", "Uttarakhand", 1900, "Tehri Lake, Surkanda Devi Temple"),
    ("Bageshwar", "Uttarakhand", 2100, "Bagnath Temple, Baijnath Group of Temples"),
    ("Bhimtal", "Uttarakhand", 2000, "Bhimtal Lake, Bhimtal Aquarium, Naukuchiatal"),
    ("Sattal", "Uttarakhand", 2000, "Seven Lakes, Butterfly Museum"),
    ("Kausani", "Uttarakhand", 2300, "Rudradhari Falls, Someshwar Temple"),
    ("Chakrata", "Uttarakhand", 2400, "Tiger Falls, Deoban, Chilmil Viewpoint"),
    ("Harsil", "Uttarakhand", 2800, "Gangotri National Park, Mukhba Village"),
    ("Nelong Valley", "Uttarakhand", 3200, "Restricted Area, Tibetan Influence"),
    ("Sariska", "Rajasthan", 2600, "Sariska Tiger Reserve, Kankwari Fort"),
    ("Bharatpur", "Rajasthan", 2400, "Keoladeo National Park, Lohagarh Fort"),
    ("Alwar", "Rajasthan", 2500, "Bala Quila, City Palace, Siliserh Lake"),
    ("Bikaner", "Rajasthan", 2900, "Junagarh Fort, Karni Mata Temple, Lalgarh Palace"),
    ("Jaisalmer", "Rajasthan", 3200, "Jaisalmer Fort, Sam Sand Dunes, Patwon Ki Haveli"),
    ("Chittorgarh", "Rajasthan", 2800, "Chittorgarh Fort, Vijay Stambh, Rana Kumbha Palace"),
    ("Kumbhalgarh", "Rajasthan", 3000, "Kumbhalgarh Fort, Badal Mahal, Wildlife Sanctuary"),
    ("Bundelkhand", "Uttar Pradesh", 1700, "Orchha Fort, Jahangir Mahal, Chaturbhuj Temple"),
    ("Lucknow", "Uttar Pradesh", 1600, "Bara Imambara, Chota Imambara, Rumi Darwaza"),
    ("Ayodhya", "Uttar Pradesh", 1500, "Ram Janmabhoomi, Hanuman Garhi, Kanak Bhawan"),
    ("Prayagraj", "Uttar Pradesh", 1500, "Triveni Sangam, Allahabad Fort, Anand Bhawan"),
    ("Fatehpur Sikri", "Uttar Pradesh", 2700, "Buland Darwaza, Jama Masjid, Panch Mahal"),
    ("Jhansi", "Uttar Pradesh", 1600, "Jhansi Fort, Rani Mahal, Maharaja Gangadhar Rao Ki Chhatri"),
    ("Kurukshetra", "Haryana", 1500, "Brahma Sarovar, Sannihit Sarovar, Jyotisar"),
    ("Pinjore", "Haryana", 1700, "Yadavindra Gardens, Bhima Devi Temple"),
    ("Morni Hills", "Haryana", 1800, "Morni Fort, Tikkar Taal, Adventure Park"),
    ("Sultanpur Bird Sanctuary", "Haryana", 1600, "Bird Watching, Lake Trails"),
    ("Nahan", "Himachal Pradesh", 2100, "Ranzor Palace, Trilokpur Temple, Renuka Lake"),
    ("Paonta Sahib", "Himachal Pradesh", 1700, "Gurudwara Paonta Sahib, Yamuna Temple"),
    ("Nurpur", "Himachal Pradesh", 2000, "Nurpur Fort, Brij Raj Swami Temple"),
    ("Hamirpur", "Himachal Pradesh", 1800, "Sujanpur Tira, Deotsidh Temple"),
    ("Una", "Himachal Pradesh", 1700, "Dera Baba Barbhag Singh, Chintpurni Temple"),
    ("Bilaspur", "Himachal Pradesh", 1900, "Gobind Sagar Lake, Vyas Cave, Kahlur Fort"),
    ("Mandi", "Himachal Pradesh", 2000, "Bhutnath Temple, Rewalsar Lake, Prashar Lake"),
    ("Sundernagar", "Himachal Pradesh", 1900, "Sundernagar Lake, Mahunag Temple"),
    ("Rewalsar", "Himachal Pradesh", 2100, "Rewalsar Lake, Naina Devi Temple, Guru Padmasambhava Cave"),
    ("Tabo", "Himachal Pradesh", 3800, "Tabo Monastery, Tabo Caves"),
    ("Kaza", "Himachal Pradesh", 3800, "Key Monastery, Kibber Village, Comic Village"),
    ("Kalpa", "Himachal Pradesh", 2900, "Narayan-Nagini Temple, Suicide Point, Roghi Village"),
    ("Sangla", "Himachal Pradesh", 2800, "Sangla Valley, Kamru Fort, Bering Nag Temple"),
    ("Chitkul", "Himachal Pradesh", 3400, "Last Village, Baspa River, Mathi Temple"),
    ("Nubra Valley", "Ladakh", 3500, "Diskit Monastery, Hunder Sand Dunes, Bactrian Camels"),
    ("Tsomoriri Lake", "Ladakh", 4500, "Tsomoriri Wetland, Korzok Monastery"),
    ("Hanle", "Ladakh", 4300, "Indian Astronomical Observatory, Hanle Monastery"),
    ("Turtuk", "Ladakh", 3200, "Balti Culture, Turtuk Waterfall, Royal House"),
    ("Dras", "Ladakh", 3200, "Dras War Memorial, Mushkoh Valley"),
    ("Kargil", "Ladakh", 3000, "Mulbekh Monastery, Kargil War Memorial"),
    ("Zanskar", "Ladakh", 4000, "Phugtal Monastery, Padum, Karsha Monastery"),
    ("Kolkata", "West Bengal", 2800, "Victoria Memorial, Howrah Bridge, Dakshineswar Kali Temple, Indian Museum, Marble Palace"),
    ("Darjeeling", "West Bengal", 3200, "Tiger Hill, Darjeeling Himalayan Railway, Tea Gardens, Peace Pagoda, Batasia Loop"),
    ("Sundarbans", "West Bengal", 2900, "Royal Bengal Tiger, Mangrove Forests, Sajnekhali Watch Tower, Bhagabatpur Crocodile Project"),
    ("Puri", "Odisha", 3000, "Jagannath Temple, Puri Beach, Konark Sun Temple, Chilika Lake, Raghurajpur Artist Village"),
    ("Bhubaneswar", "Odisha", 2800, "Lingaraj Temple, Udayagiri and Khandagiri Caves, Nandankanan Zoo, Dhauli Peace Pagoda"),
    ("Konark", "Odisha", 3100, "Sun Temple, Chandrabhaga Beach, Konark Dance Festival"),
    ("Patna", "Bihar", 2200, "Mahavir Mandir, Golghar, Patna Museum, Kumhrar, Takht Sri Harmandir Sahib"),
    ("Bodh Gaya", "Bihar", 2400, "Mahabodhi Temple, Great Buddha Statue, Bodhi Tree, Thai Monastery"),
    ("Nalanda", "Bihar", 2300, "Nalanda University Ruins, Nalanda Archaeological Museum, Xuan Zang Memorial"),
    ("Ranchi", "Jharkhand", 2500, "Tagore Hill, Hundru Falls, Dassam Falls, Rock Garden, Jonha Falls"),
    ("Guwahati", "Assam", 2500, "Kamakhya Temple, Umananda Temple, Assam State Museum, Brahmaputra River Cruise"),
    ("Kaziranga", "Assam", 2800, "One-Horned Rhinoceros, Jeep Safari, Elephant Safari, Orchid Park"),
    ("Majuli", "Assam", 2700, "Satras, Vaishnavite Culture, Mask Making, River Island Life"),
    ("Shillong", "Meghalaya", 3000, "Umiam Lake, Shillong Peak, Elephant Falls, Ward's Lake, Don Bosco Museum"),
    ("Cherrapunji", "Meghalaya", 3200, "Living Root Bridges, Nohkalikai Falls, Mawsmai Cave, Seven Sisters Falls"),
    ("Mawlynnong", "Meghalaya", 3100, "Cleanest Village in Asia, Living Root Bridge, Sky Walk, Balancing Rock"),
    ("Gangtok", "Sikkim", 3500, "Rumtek Monastery, Tsomgo Lake, Nathula Pass, MG Marg, Enchey Monastery"),
    ("Pelling", "Sikkim", 3600, "Pemayangtse Monastery, Khecheopalri Lake, Rabdentse Ruins, Singshore Bridge"),
    ("Tawang", "Arunachal Pradesh", 4000, "Tawang Monastery, Sela Pass, Madhuri Lake, Gorichen Peak"),
    ("Ziro", "Arunachal Pradesh", 3800, "Apatani Tribal Culture, Pine Hills, Ziro Music Festival, Talley Valley"),
    ("Kohima", "Nagaland", 3200, "Kohima War Cemetery, Dzukou Valley, Naga Heritage Village, Hornbill Festival"),
    ("Imphal", "Manipur", 2800, "Kangla Fort, Loktak Lake, Ima Keithel, Shri Govindajee Temple"),
    ("Aizawl", "Mizoram", 3000, "Durtlang Hills, Solomon's Temple, Reiek Heritage Village, Falkawn Village"),
    ("Agartala", "Tripura", 2700, "Ujjayanta Palace, Neermahal Palace, Tripura Sundari Temple, Unakoti Rock Carvings"),
    ("Digha", "West Bengal", 2900, "Digha Beach, Marine Aquarium, Amarabati Park, Chandaneswar Temple"),
    ("Chilika Lake", "Odisha", 2900, "Irrawaddy Dolphins, Bird Sanctuary, Satapada, Kalijai Temple"),
    ("Manas National Park", "Assam", 2600, "Wildlife Safari, Bengal Tiger, Golden Langur, Rafting on Manas River"),
    ("Living Root Bridges", "Meghalaya", 3100, "Double Decker Root Bridge, Nongriat Village, Rainbow Falls, Trekking"),
    ("Nathula Pass", "Sikkim", 3800, "Indo-China Border, High Altitude Views, Baba Harbhajan Singh Mandir"),
    ("Loktak Lake", "Manipur", 2700, "Floating Phumdis, Keibul Lamjao National Park, Sendra Island"),
    ("Phawngpui Peak", "Mizoram", 3200, "Blue Mountain, Trekking, Rhododendron Blooms, Cliff Views"),
    ("Unakoti", "Tripura", 2800, "Rock Carvings, Shiva Head, Ancient Sculptures"),
    ("Nameri National Park", "Assam", 2700, "Tiger Reserve, River Rafting, Bird Watching, Trekking"),
    ("Dzukou Valley", "Nagaland", 3300, "Lily Valley, Trekking, Rhododendrons, Camping"),
    ("Gorichen Peak", "Arunachal Pradesh", 4100, "Trekking, Snow Views, Tribal Villages"),
    ("Keibul Lamjao", "Manipur", 2600, "Floating National Park, Sangai Deer, Phumdis"),
    ("Balpakram National Park", "Meghalaya", 2900, "Canyon Views, Wildlife, Perpetual Winds Legend"),
    ("Pobitora Wildlife Sanctuary", "Assam", 2500, "Dense Rhino Population, Bird Watching, Jeep Safari"),
    ("Namdapha National Park", "Arunachal Pradesh", 3900, "Tiger Reserve, Biodiversity Hotspot, Trekking"),
    ("Sundarbans National Park", "West Bengal", 2800, "Mangrove Safari, Tiger Spotting, Bird Watching"),
    ("Simlipal National Park", "Odisha", 3000, "Tiger Reserve, Waterfalls, Tribal Villages"),
    ("Bhitarkanika", "Odisha", 2900, "Mangroves, Crocodiles, Bird Sanctuary, Boat Safari"),
    ("Jaldapara National Park", "West Bengal", 2700, "Rhino Safari, Elephant Ride, Totopara Tribal Village"),
    ("Gorumara National Park", "West Bengal", 2800, "Elephant Safari, Rhino, Watch Towers"),
    ("Nokrek National Park", "Meghalaya", 3000, "Red Panda, Biosphere Reserve, Citrus Orchards"),
    ("Intanki Wildlife Sanctuary", "Nagaland", 3100, "Elephant Reserve, Hoolock Gibbon, Bird Watching"),
    ("Khangchendzonga National Park", "Sikkim", 4000, "Glaciers, High Altitude Trekking, Red Panda"),
    ("Mouling National Park", "Arunachal Pradesh", 3800, "Trekking, Waterfalls, Tribal Culture"),
    ("Sirohi National Park", "Manipur", 2700, "Sangai Deer Habitat, Wetlands"),
    ("Murlen National Park", "Mizoram", 3200, "Clouded Leopard, Dense Forests, Caves"),
    ("Sipahijola Wildlife Sanctuary", "Tripura", 2800, "Clouded Leopard, Spectacled Monkey, Bird Watching"),
    ("Dampa Tiger Reserve", "Mizoram", 3100, "Tiger Project, Primates, Butterfly Diversity"),
    ("Orang National Park", "Assam", 2600, "Mini Kaziranga, Rhino, Tiger Safari"),
    ("Haflong", "Assam", 2800, "Hill Station, Lake, Tribal Culture"),
    ("Tura", "Meghalaya", 2900, "Garo Hills, Nokrek Peak, Pelga Falls"),
    ("Pasighat", "Arunachal Pradesh", 3600, "Siang River, Hanging Bridge, Daying Ering Sanctuary"),
    ("Bomdila", "Arunachal Pradesh", 3700, "Monasteries, Apple Orchards, Eaglenest Sanctuary"),
    ("Moirang", "Manipur", 2600, "INA Museum, Loktak Lake Views, Folk Dance"),
    ("Lunglei", "Mizoram", 3000, "Hill Views, Caves, Tribal Villages"),
    ("Jampui Hills", "Tripura", 2900, "Orange Orchards, Sunset Views, Tribal Culture"),
    ("Kalimpong", "West Bengal", 3100, "Deolo Hill, Cactus Nursery, Durpin Monastery"),
    ("Cuttack", "Odisha", 2800, "Barabati Fort, Dhabaleswar Temple, Silver Filigree Work"),
    ("Rajgir", "Bihar", 2300, "Hot Springs, Vishwa Shanti Stupa, Cyclopean Wall"),
    ("Deoghar", "Jharkhand", 2600, "Baidyanath Temple, Nandan Pahar, Trikut Hills"),
    ("Tezpur", "Assam", 2700, "Agnigarh Hill, Cole Park, Bamuni Hills"),
    ("Dawki", "Meghalaya", 3000, "Umngot River Boating, Bangladesh Border Views"),
    ("Lachung", "Sikkim", 3700, "Yumthang Valley, Zero Point, Hot Springs"),
    ("Dirang", "Arunachal Pradesh", 3800, "Hot Springs, Sangti Valley, Kiwi Orchards"),
    ("Mokokchung", "Nagaland", 3200, "Ao Tribe Culture, Longkhum Village, Caves"),
    ("Ukhrul", "Manipur", 2900, "Shirui Lily Festival, Khayang Peak, Phangrei Picnic Spot"),
    ("Champhai", "Mizoram", 3100, "Vineyards, Rih Dil Lake, Murlen National Park"),
    ("Udaipur (Tripura)", "Tripura", 2800, "Tripura Sundari Temple, Bhuvaneswari Temple, Lake"),
    ("Mandarmani", "West Bengal", 2900, "Beach Drive, Red Crabs, Sea Resort"),
    ("Gopalpur", "Odisha", 3000, "Beach, Lighthouse, Backwaters"),
    ("Vaishali", "Bihar", 2200, "Ashokan Pillar, Relic Stupa, Japanese Temple"),
    ("Betla National Park", "Jharkhand", 2700, "Palamu Tiger Reserve, Forts, Waterfalls"),
    ("Jorhat", "Assam", 2600, "Tea Gardens, Majuli Access, Hoollongapar Gibbon Sanctuary"),
    ("Tura Peak", "Meghalaya", 2900, "Trekking, Views of Bangladesh Plains"),
    ("Yumthang Valley", "Sikkim", 3800, "Hot Springs, Rhododendrons, Snow Views"),
    ("Mechuka", "Arunachal Pradesh", 4000, "Remote Valley, Siyom River, Gurudwara"),
    ("Pfutsero", "Nagaland", 3300, "Highest Town, Glory Peak, Trekking"),
    ("Thoubal", "Manipur", 2700, "Khongjom War Memorial, River Views"),
    ("Serchhip", "Mizoram", 3000, "Vantawng Falls, Thenzawl Deer Park"),
    ("Sepahijala", "Tripura", 2800, "Wildlife Sanctuary, Clouded Leopard, Botanical Garden"),
    ("Bishnupur", "West Bengal", 2700, "Terracotta Temples, Rash Mancha, Baluchari Sarees"),
    ("Berhampore", "West Bengal", 2800, "Silk Weaving, Hazarduari Palace Access"),
    ("Sambalpur", "Odisha", 2900, "Hirakud Dam, Samaleswari Temple, Lean Tower of Tantra"),
    ("Gaya", "Bihar", 2300, "Vishnupad Temple, Pind Daan, Mahabodhi Access"),
    ("Hazaribagh", "Jharkhand", 2600, "Wildlife Sanctuary, Canary Hills, Lakes"),
    ("Dibrugarh", "Assam", 2700, "Tea City, Dehing Patkai, Raidongia Dol"),
    ("Nongpoh", "Meghalaya", 2900, "Umiam Lake Access, Orchid Farms"),
    ("Ravangla", "Sikkim", 3600, "Buddha Park, Maenam Hill, Temi Tea Garden"),
    ("Along", "Arunachal Pradesh", 3700, "Hanging Bridges, Mithun Farms, Darka Village"),
    ("Tuensang", "Nagaland", 3200, "Chang Tribe, Living Museum, Tsadang"),
    ("Churachandpur", "Manipur", 2800, "Tribal Culture, Waterfalls, Caves"),
    ("Saiha", "Mizoram", 3100, "Palak Lake, River Views"),
    ("Dharmanagar", "Tripura", 2800, "Unakoti Access, Temples, Markets"),
    ("Siliguri", "West Bengal", 2900, "Gateway to Northeast, Coronation Bridge, Tea Gardens"),
    ("Rourkela", "Odisha", 3000, "Steel City, Hanuman Vatika, Vedvyas Temple"),
    ("Bhagalpur", "Bihar", 2200, "Silk City, Vikramshila Ruins, Gangetic Dolphins"),
    ("Jamshedpur", "Jharkhand", 2500, "Tata Steel City, Jubilee Park, Dimna Lake"),
    ("Silchar", "Assam", 2600, "Barak Valley, Khaspur Ruins, Bhuvan Hill"),
    ("Nongstoin", "Meghalaya", 3000, "Nongkhnum River Island, Langshiang Falls"),
    ("Namchi", "Sikkim", 3500, "Char Dham, Samdruptse Statue, Rock Garden"),
    ("Itanagar", "Arunachal Pradesh", 3600, "Ita Fort, Ganga Lake, Jawaharlal Nehru Museum"),
    ("Wokha", "Nagaland", 3200, "Lotha Tribe, Doyang River, Mount Tiyi"),
    ("Tamenglong", "Manipur", 2800, "Tharon Cave, Zeilad Lake, Orange Orchards"),
    ("Kolasib", "Mizoram", 3000, "Tlawng River, Horticulture Farms"),
    ("Kailashahar", "Tripura", 2800, "Unakoti, Chouddo Devotar Temple, Lakes"),
    ("Mumbai", "Maharashtra", 1400, "Gateway of India, Marine Drive, Elephanta Caves, Siddhivinayak Temple, Chhatrapati Shivaji Terminus, Juhu Beach"),
    ("Pune", "Maharashtra", 1500, "Shaniwar Wada, Aga Khan Palace, Sinhagad Fort, Osho Ashram, Dagadusheth Halwai Ganpati"),
    ("Aurangabad", "Maharashtra", 1700, "Ajanta Caves, Ellora Caves, Bibi Ka Maqbara, Daulatabad Fort, Grishneshwar Temple"),
    ("Nashik", "Maharashtra", 1700, "Trimbakeshwar Temple, Panchvati, Sula Vineyards, Coin Museum, Kalaram Temple"),
    ("Nagpur", "Maharashtra", 1800, "Deekshabhoomi, Futala Lake, Sitabuldi Fort, Ambazari Lake, Maharaj Bagh Zoo"),
    ("Kolhapur", "Maharashtra", 1600, "Mahalakshmi Temple, Rankala Lake, New Palace, Panhala Fort, Jyotiba Temple"),
    ("Lonavala", "Maharashtra", 1500, "Tiger's Leap, Bhushi Dam, Karla Caves, Rajmachi Fort, Khandala"),
    ("Mahabaleshwar", "Maharashtra", 1700, "Venna Lake, Mapro Garden, Pratapgad Fort, Lingmala Waterfall, Elephant's Head Point"),
    ("Alibaug", "Maharashtra", 1400, "Alibaug Beach, Kolaba Fort, Nagaon Beach, Murud Janjira Fort, Kashid Beach"),
    ("Goa (Panaji)", "Goa", 1900, "Old Goa Churches, Fort Aguada, Basilica of Bom Jesus, Dona Paula, Miramar Beach"),
    ("North Goa (Calangute)", "Goa", 1900, "Calangute Beach, Baga Beach, Anjuna Beach, Fort Aguada, Vagator Beach, Tito's Lane"),
    ("South Goa (Palolem)", "Goa", 2000, "Palolem Beach, Colva Beach, Agonda Beach, Cabo de Rama Fort, Butterfly Beach"),
    ("Amboli", "Maharashtra", 1800, "Amboli Waterfall, Shirgaonkar Point, Sunset Point, Nangarta Falls"),
    ("Matheran", "Maharashtra", 1450, "Charlotte Lake, Panorama Point, Echo Point, Louisa Point, Monkey Point"),
    ("Shirdi", "Maharashtra", 1650, "Sai Baba Temple, Shani Shingnapur, Dwarkamai, Chavadi"),
    ("Ajanta", "Maharashtra", 1700, "Ajanta Caves, View Points, Jain Caves"),
    ("Ellora", "Maharashtra", 1700, "Ellora Caves, Kailasa Temple, Grishneshwar Jyotirlinga"),
    ("Tarkarli", "Maharashtra", 1900, "Tarkarli Beach, Devbag Beach, Scuba Diving, Sindhudurg Fort, Tsunami Island"),
    ("Ganpatipule", "Maharashtra", 1800, "Ganpatipule Temple, Ganpatipule Beach, Malgund Beach, Jaigad Fort"),
    ("Ratnagiri", "Maharashtra", 1800, "Thibaw Palace, Ganpatipule Access, Ratnadurg Fort, Bhagwati Temple"),
    ("Chiplun", "Maharashtra", 1700, "Parshuram Temple, Vashishti River, Guhagar Beach Access"),
    ("Panchgani", "Maharashtra", 1700, "Table Land, Sydney Point, Parsi Point, Kate's Point, Mapro Garden"),
    ("Lavasa", "Maharashtra", 1550, "Lakeside Promenade, Temghar Dam, Watersports, Bamboosa"),
    ("Bhimashankar", "Maharashtra", 1500, "Bhimashankar Temple, Bhimashankar Wildlife Sanctuary, Trekking"),
    ("Trimbakeshwar", "Maharashtra", 1700, "Trimbakeshwar Jyotirlinga, Brahmagiri Hill, Anjaneri Fort"),
    ("Igatpuri", "Maharashtra", 1500, "Vipassana Centre, Bhandardara Lake, Tringalwadi Fort, Vaitarna Dam"),
    ("Bhandardara", "Maharashtra", 1600, "Arthur Lake, Wilson Dam, Randha Falls, Umbrella Falls, Ratangad Fort"),
    ("Saputara", "Gujarat", 1700, "Saputara Lake, Sunset Point, Gira Falls, Artist Village, Ropeway"),
    ("Ahmednagar", "Maharashtra", 1600, "Cavalry Tank Museum, Salabat Khan Tomb, Ahmednagar Fort"),
    ("Satara", "Maharashtra", 1650, "Ajinkyatara Fort, Thoseghar Waterfalls, Kaas Plateau, Natraj Mandir"),
    ("Sangli", "Maharashtra", 1700, "Ganapati Temple, Sangameshwar Temple, Sagareshwar Wildlife Sanctuary"),
    ("Solapur", "Maharashtra", 1800, "Siddheshwar Temple, Bhuikot Fort, Tuljapur Bhavani Temple Access"),
    ("Pandharpur", "Maharashtra", 1800, "Vitthal Temple, Chandrabhaga River, Pundalik Temple"),
    ("Tuljapur", "Maharashtra", 1800, "Tulja Bhavani Temple, Kallol Tirth"),
    ("Akkalkot", "Maharashtra", 1850, "Swami Samarth Temple, Vatavriksha Temple"),
    ("Shegaon", "Maharashtra", 1900, "Anand Sagar, Gajanan Maharaj Temple"),
    ("Wardha", "Maharashtra", 1800, "Sevagram Ashram, Gandhi Ashram, Vishwa Shanti Stupa"),
    ("Amravati", "Maharashtra", 1850, "Ambadevi Temple, Melghat Tiger Reserve Access, Chikhaldara Hill Station"),
    ("Chikhaldara", "Maharashtra", 1900, "Bhimkund, Hurricane Point, Gawilgad Fort, Coffee Plantations"),
    ("Yavatmal", "Maharashtra", 1850, "Tipeshwar Wildlife Sanctuary, Waghadi River"),
    ("Akola", "Maharashtra", 1800, "Narnala Fort, Rajeshwar Temple, Akola Fort"),
    ("Goa Velha", "Goa", 1900, "Basilica of Bom Jesus, Se Cathedral, Archaeological Museum"),
    ("Margao", "Goa", 2000, "Margao Municipal Market, Colva Beach Access, Holy Spirit Church"),
    ("Mapusa", "Goa", 1900, "Mapusa Friday Market, St. Jerome Church, Bodgeshwar Temple"),
    ("Vasco da Gama", "Goa", 1900, "Bogmalo Beach, Naval Aviation Museum, Mormugao Port"),
    ("Old Goa", "Goa", 1900, "UNESCO Churches, Viceroy's Arch, Fontainhas Latin Quarter Access"),
    ("Dudhsagar Falls", "Goa", 2000, "Dudhsagar Waterfall, Jeep Safari, Bhagwan Mahavir Wildlife Sanctuary"),
    ("Mollem National Park", "Goa", 2000, "Wildlife Safari, Tambdi Surla Temple, Spice Plantations"),
    ("Spice Plantations (Ponda)", "Goa", 1950, "Sahakari Spice Farm, Tropical Spice Plantation, Savoi Verem"),
    ("Arvalem Waterfall", "Goa", 1900, "Arvalem Caves, Rudreshwar Temple, Harvalem Waterfall"),
    ("Netravali Wildlife Sanctuary", "Goa", 2000, "Bubbling Lake, Mainapi Waterfall, Trekking"),
    ("Cotigao Wildlife Sanctuary", "Goa", 2050, "Tree Top Watch Towers, Trekking, Nature Trails"),
    ("Bhimgad Wildlife Sanctuary", "Maharashtra", 1850, "Belgaum Fort Access, Trekking, Wildlife"),
    ("Raigad Fort", "Maharashtra", 1500, "Raigad Ropeway, Shivaji Maharaj Coronation Site, Hirkani Point"),
    ("Pratapgad Fort", "Maharashtra", 1700, "Bhavani Temple, Afzal Khan Tomb, Trekking"),
    ("Vijaydurg Fort", "Maharashtra", 1900, "Sea Fort, Underwater Ruins, Beach"),
    ("Sindhudurg Fort", "Maharashtra", 1900, "Island Fort, Snorkeling, Shivaji Statue"),
    ("Murud Janjira", "Maharashtra", 1450, "Sea Fort, Boat Ride, Palace Ruins"),
    ("Harihareshwar", "Maharashtra", 1600, "Harihareshwar Temple, Kalbhairav Temple, Rocky Beach"),
    ("Diveagar", "Maharashtra", 1550, "Suvarna Ganesh Temple, Diveagar Beach, Phansad Wildlife Sanctuary"),
    ("Shrivardhan", "Maharashtra", 1550, "Shrivardhan Beach, Peshwa Smarak, Konkani Culture"),
    ("Harnai", "Maharashtra", 1600, "Fish Auction, Harnai Beach, Suvarnadurg Fort"),
    ("Dapoli", "Maharashtra", 1600, "Murud Beach, Kadyavarcha Ganpati, Panhalakaji Caves"),
    ("Guhagar", "Maharashtra", 1700, "Velneshwar Temple, Guhagar Beach, Vyadeshwar Temple"),
    ("Anjanvel", "Maharashtra", 1700, "Gopalgad Fort, Lighthouse, Enron Project Ruins"),
    ("Hedvi", "Maharashtra", 1700, "Dashabhuja Ganesh Temple, Brahman Ghal, Beach"),
    ("Velas", "Maharashtra", 1600, "Olive Ridley Turtle Conservation, Velas Beach"),
    ("Kelshi", "Maharashtra", 1600, "Kelshi Beach, Yakub Baba Dargah, Mahalaxmi Temple"),
    ("Ladghar", "Maharashtra", 1600, "Ladghar Beach, Tamas Teertha, Dolphin Spotting"),
    ("Kashid", "Maharashtra", 1450, "Kashid Beach, Phansad Bird Sanctuary, Revdanda Fort"),
    ("Nagaon", "Maharashtra", 1400, "Nagaon Beach, Water Sports, Birla Temple"),
    ("Revanda Beach", "Maharashtra", 1450, "Revdanda Fort, Portuguese Church, Beach"),
    ("Korlai Fort", "Maharashtra", 1450, "Sea Fort, Lighthouse, Korlai Village"),
    ("Mandwa", "Maharashtra", 1400, "Mandwa Beach, Ferry to Mumbai, Kihim Beach Access"),
    ("Kihim", "Maharashtra", 1400, "Kihim Beach, Bird Watching, Water Sports"),
    ("Saswane", "Maharashtra", 1450, "Quiet Beach, Fishing Village"),
    ("Awas", "Maharashtra", 1400, "Awas Beach, Homestays"),
    ("Chaundi", "Goa", 1900, "Chapora Fort Access, Vagator Beach"),
    ("Arambol", "Goa", 1900, "Arambol Beach, Sweet Water Lake, Paragliding"),
    ("Morjim", "Goa", 1900, "Morjim Beach, Olive Ridley Turtles, Ashwem Beach"),
    ("Ashwem", "Goa", 1900, "Ashwem Beach, Quiet Vibes, Rock Formations"),
    ("Mandrem", "Goa", 1900, "Mandrem Beach, Yoga Retreats, Junas Beach"),
    ("Querim", "Goa", 1900, "Querim Beach, Terekhol Fort, Quiet North"),
    ("Candolim", "Goa", 1900, "Candolim Beach, Sinquerim Fort, Aguada Lighthouse"),
    ("Sinquerim", "Goa", 1900, "Lower Aguada Fort, Water Sports"),
    ("Nerul", "Goa", 1900, "Coco Beach, Reis Magos Fort"),
    ("Reis Magos", "Goa", 1900, "Reis Magos Fort, Church, Views"),
    ("Benaulim", "Goa", 2000, "Benaulim Beach, Dolphin Trips, Church"),
    ("Varca", "Goa", 2000, "Varca Beach, Luxury Resorts, Flea Market"),
    ("Cavelossim", "Goa", 2000, "Cavelossim Beach, Mobor Beach, River Sal"),
    ("Mobor", "Goa", 2000, "Mobor Beach, Water Sports, River Cruises"),
    ("Betul", "Goa", 2000, "Betul Fort, Beach, Fishing Village"),
    ("Cansaulim", "Goa", 2000, "Cansaulim Beach, Three Kings Church"),
    ("Majorda", "Goa", 1950, "Majorda Beach, Bakery Trail"),
    ("Utorda", "Goa", 1950, "Utorda Beach, Quiet Stretch"),
    ("Arossim", "Goa", 1950, "Arossim Beach, Cansaulim Access"),
    ("Velsao", "Goa", 1950, "Velsao Beach, Pale Beach"),
    ("Hyderabad", "Telangana", 1700, "Charminar, Golconda Fort, Qutb Shahi Tombs, Hussain Sagar Lake, Ramoji Film City"),
    ("Bangalore", "Karnataka", 1800, "Lalbagh Botanical Garden, Bangalore Palace, Cubbon Park, Vidhana Soudha, ISKCON Temple"),
    ("Chennai", "Tamil Nadu", 2200, "Marina Beach, Kapaleeshwarar Temple, Fort St. George, Government Museum, Mahabalipuram Access"),
    ("Kochi", "Kerala", 2500, "Fort Kochi, Chinese Fishing Nets, Mattancherry Palace, Jewish Synagogue, Marine Drive"),
    ("Mysore", "Karnataka", 1900, "Mysore Palace, Chamundi Hills, Brindavan Gardens, Jaganmohan Palace, Karanji Lake"),
    ("Coorg (Madikeri)", "Karnataka", 2000, "Abbey Falls, Raja's Seat, Talacauvery, Dubare Elephant Camp, Coffee Plantations"),
    ("Ooty", "Tamil Nadu", 2100, "Nilgiri Mountain Railway, Botanical Gardens, Ooty Lake, Doddabettu Peak, Rose Garden"),
    ("Kodaikanal", "Tamil Nadu", 2200, "Kodaikanal Lake, Coaker's Walk, Bryant Park, Pillar Rocks, Pine Forest"),
    ("Munnar", "Kerala", 2400, "Tea Plantations, Eravikulam National Park, Mattupetty Dam, Echo Point, Attukal Waterfalls"),
    ("Pondicherry", "Puducherry", 2300, "Promenade Beach, Auroville, Paradise Beach, French Quarter, Sri Aurobindo Ashram"),
    ("Hampi", "Karnataka", 1800, "Virupaksha Temple, Vittala Temple, Lotus Mahal, Elephant Stables, Hemakuta Hill"),
    ("Gokarna", "Karnataka", 2100, "Om Beach, Mahabaleshwar Temple, Kudle Beach, Half Moon Beach, Paradise Beach"),
    ("Alleppey", "Kerala", 2500, "Backwaters Houseboat, Alappuzha Beach, Krishnapuram Palace, Marari Beach"),
    ("Thekkady", "Kerala", 2400, "Periyar Wildlife Sanctuary, Boat Safari, Bamboo Rafting, Spice Plantations"),
    ("Wayanad", "Kerala", 2300, "Edakkal Caves, Wayanad Wildlife Sanctuary, Banasura Sagar Dam, Pookode Lake"),
    ("Kumarakom", "Kerala", 2500, "Kumarakom Bird Sanctuary, Backwaters, Vembanad Lake, Pathiramanal Island"),
    ("Varkala", "Kerala", 2600, "Varkala Beach, Cliff, Janardhana Swamy Temple, Kappil Lake"),
    ("Kovalam", "Kerala", 2600, "Lighthouse Beach, Hawa Beach, Samudra Beach, Vizhinjam Marine Aquarium"),
    ("Thrissur", "Kerala", 2500, "Athirappilly Falls, Vadakkunnathan Temple, Thrissur Pooram Festival"),
    ("Trivandrum", "Kerala", 2600, "Padmanabhaswamy Temple, Kovalam Beach Access, Napier Museum, Poovar Beach"),
    ("Tirupati", "Andhra Pradesh", 2000, "Tirumala Venkateswara Temple, Sri Vari Museum, Talakona Waterfall"),
    ("Visakhapatnam", "Andhra Pradesh", 2100, "RK Beach, Kailasagiri Hill, Submarine Museum, Borra Caves"),
    ("Araku Valley", "Andhra Pradesh", 2200, "Borra Caves, Tribal Museum, Coffee Plantations, Padmapuram Gardens"),
    ("Madurai", "Tamil Nadu", 2200, "Meenakshi Temple, Thirumalai Nayakkar Palace, Gandhi Museum"),
    ("Rameshwaram", "Tamil Nadu", 2400, "Ramanathaswamy Temple, Dhanushkodi, Pamban Bridge"),
    ("Kanyakumari", "Tamil Nadu", 2500, "Vivekananda Rock Memorial, Thiruvalluvar Statue, Sunrise Point"),
    ("Mahabalipuram", "Tamil Nadu", 2200, "Shore Temple, Pancha Rathas, Arjuna's Penance, Krishna's Butter Ball"),
    ("Thanjavur", "Tamil Nadu", 2200, "Brihadeeswarar Temple, Thanjavur Palace, Saraswati Mahal Library"),
    ("Coimbatore", "Tamil Nadu", 2100, "Marudhamalai Temple, VOC Park, Perur Pateeswarar Temple, Siruvani Waterfalls"),
    ("Chikmagalur", "Karnataka", 2000, "Mullayanagiri Peak, Baba Budangiri, Coffee Museum, Hebbe Falls"),
    ("Badami", "Karnataka", 1700, "Badami Cave Temples, Agastya Lake, Bhutanatha Temples"),
    ("Belur", "Karnataka", 1900, "Chennakeshava Temple, Hoysaleswara Temple Access, Yagachi Dam"),
    ("Halebidu", "Karnataka", 1900, "Hoysaleswara Temple, Jain Basadi, Archaeological Museum"),
    ("Bandipur", "Karnataka", 1900, "Bandipur National Park, Tiger Safari, Gopalaswamy Hills"),
    ("Nagarhole", "Karnataka", 2000, "Nagarhole National Park, Kabini River, Wildlife Safari"),
    ("Jog Falls", "Karnataka", 2100, "Jog Falls, Linganamakki Dam, Dabbe Falls"),
    ("Udupi", "Karnataka", 2100, "Sri Krishna Temple, Malpe Beach, St. Mary's Island"),
    ("Murudeshwar", "Karnataka", 2100, "Murudeshwar Temple, Giant Shiva Statue, Beach"),
    ("Sringeri", "Karnataka", 2000, "Sharada Peetham, Vidyashankara Temple, Tunga River"),
    ("Dharmasthala", "Karnataka", 2100, "Manjunatha Temple, Bahubali Statue, Annappa Betta"),
    ("Shravanabelagola", "Karnataka", 1900, "Gommateshwara Statue, Chandragiri Hill, Vindhyagiri"),
    ("Kabini", "Karnataka", 2000, "Kabini Wildlife Sanctuary, Boat Safari, Backwaters"),
    ("Dandeli", "Karnataka", 2100, "Dandeli Wildlife Sanctuary, White Water Rafting, Kali River"),
    ("Vijayawada", "Andhra Pradesh", 2000, "Kanaka Durga Temple, Prakasam Barrage, Undavalli Caves"),
    ("Amaravathi", "Andhra Pradesh", 2000, "Amaravathi Stupa, Amareswara Temple, Dhyana Buddha"),
    ("Guntur", "Andhra Pradesh", 2000, "Uppalapadu Bird Sanctuary, Kondaveedu Fort Access"),
    ("Nellore", "Andhra Pradesh", 2100, "Ranganatha Temple, Pulicat Lake, Nelapattu Bird Sanctuary"),
    ("Kurnool", "Andhra Pradesh", 1900, "Belum Caves, Oravakallu Rock Garden, Rollapadu Sanctuary"),
    ("Anantapur", "Andhra Pradesh", 1800, "Lepakshi Temple, Puttaparthi Sai Baba Ashram"),
    ("Puttaparthi", "Andhra Pradesh", 1800, "Prasanthi Nilayam, Chaitanya Jyoti Museum, Wish Fulfilling Tree"),
    ("Srisailam", "Andhra Pradesh", 1900, "Mallikarjuna Temple, Srisailam Dam, Tiger Reserve"),
    ("Horsley Hills", "Andhra Pradesh", 1900, "Horsley Hills Viewpoint, Environmental Park, Gangotri Lake"),
    ("Lambasingi", "Andhra Pradesh", 2200, "Frosty Winters, Apple Gardens, Thajangi Reservoir"),
    ("Pondicherry (Auroville)", "Puducherry", 2300, "Matrimandir, Auroville Beach, Peace Area"),
    ("Kanchipuram", "Tamil Nadu", 2200, "Ekambareswarar Temple, Kailasanathar Temple, Silk Sarees"),
    ("Tiruchirappalli", "Tamil Nadu", 2200, "Rockfort Temple, Srirangam Temple, Jambukeswarar Temple"),
    ("Salem", "Tamil Nadu", 2100, "Yercaud Hill Station Access, Mettur Dam"),
    ("Yercaud", "Tamil Nadu", 2100, "Yercaud Lake, Lady's Seat, Pagoda Point, Shevaroy Temple"),
    ("Pollachi", "Tamil Nadu", 2100, "Anamalai Tiger Reserve, Topslip, Parambikulam Access"),
    ("Valparai", "Tamil Nadu", 2100, "Tea Estates, Sholayar Dam, Grass Hills"),
    ("Courtallam", "Tamil Nadu", 2300, "Courtallam Waterfalls, Five Falls, Old Courtallam Falls"),
    ("Chettinad", "Tamil Nadu", 2200, "Chettinad Mansions, Chettinad Palace, Athangudi Tiles"),
    ("Karaikudi", "Tamil Nadu", 2200, "Chettinad Cuisine, Thousand Windows House"),
    ("Dhanushkodi", "Tamil Nadu", 2400, "Ghost Town, Ram Setu View, Beach Ruins"),
    ("Vivekananda Rock", "Tamil Nadu", 2500, "Meditation Hall, Footprint, Ferry Ride"),
    ("Bekal", "Kerala", 2400, "Bekal Fort, Bekal Beach, Chandragiri Fort"),
    ("Kasaragod", "Kerala", 2400, "Ananthapura Lake Temple, Malik Dinar Mosque"),
    ("Kannur", "Kerala", 2500, "St. Angelo Fort, Payyambalam Beach, Theyyam Rituals"),
    ("Palakkad", "Kerala", 2400, "Palakkad Fort, Malampuzha Dam, Silent Valley Access"),
    ("Athirappilly", "Kerala", 2500, "Athirappilly Waterfalls, Vazhachal Falls"),
    ("Nelliyampathy", "Kerala", 2400, "Nelliyampathy Hills, Tea Estates, Seetharkundu Viewpoint"),
    ("Silent Valley", "Kerala", 2400, "Silent Valley National Park, Biodiversity Hotspot"),
    ("Periyar", "Kerala", 2400, "Periyar Lake, Tiger Reserve, Spice Gardens"),
    ("Vagamon", "Kerala", 2400, "Pine Forests, Meadows, Paragliding"),
    ("Ponmudi", "Kerala", 2600, "Ponmudi Hill Station, Golden Valley, Peppara Sanctuary"),
    ("Idukki", "Kerala", 2400, "Idukki Arch Dam, Hill View Park, Wildlife"),
    ("Peermade", "Kerala", 2400, "Tea Plantations, Waterfalls, Trekking"),
    ("Gavi", "Kerala", 2400, "Gavi Forest, Eco-Tourism, Wildlife"),
    ("Konni", "Kerala", 2500, "Elephant Training Centre, Adavi Eco-Tourism"),
    ("Kollam", "Kerala", 2500, "Ashtamudi Lake, Thangassery Lighthouse, Adventure Park"),
    ("Thenmala", "Kerala", 2500, "Eco-Tourism, Deer Park, Leisure Zone"),
    ("Sabarimala", "Kerala", 2500, "Ayyappa Temple, Pilgrimage Trek"),
    ("Ernakulam", "Kerala", 2500, "Hill Palace Museum, Folklore Museum"),
    ("Kalady", "Kerala", 2500, "Adi Shankara Birthplace, Crocodile Ghat"),
    ("Guruvayur", "Kerala", 2500, "Guruvayur Temple, Elephant Sanctuary"),
    ("Kodungallur", "Kerala", 2500, "Kodungallur Bhagavathy Temple, Cheraman Mosque"),
    ("Mangalore", "Karnataka", 2100, "Panambur Beach, Tannirbhavi Beach, Kudroli Temple"),
    ("Manipal", "Karnataka", 2100, "End Point, Museum of Anatomy, Venugopal Temple"),
    ("Agumbe", "Karnataka", 2100, "Rainforest, Sunset View Point, Barkana Falls"),
    ("Kudremukh", "Karnataka", 2100, "Kudremukh Peak Trek, National Park"),
    ("Sakleshpur", "Karnataka", 2000, "Manjarabad Fort, Bisle View Point, Coffee Estates"),
    ("Horanadu", "Karnataka", 2000, "Annapoorneshwari Temple, Tea Estates"),
    ("Kemmangundi", "Karnataka", 2000, "Z Point, Rose Garden, Hebbe Falls"),
    ("Biligiriranga Hills", "Karnataka", 1900, "BR Hills Sanctuary, Biligiri Temple"),
    ("BR Hills", "Karnataka", 1900, "Wildlife Safari, Dodda Sampige Tree"),
    ("Talakaveri", "Karnataka", 2000, "Source of Cauvery River, Bhagamandala"),
    ("Bhagamandala", "Karnataka", 2000, "Triveni Sangam, Temple Complex"),
    ("Nisargadhama", "Karnataka", 2000, "Cauvery Island, Bamboo Grove, Deer Park"),
    ("Harangi Dam", "Karnataka", 2000, "Dam Views, Picnic Spot"),
    ("Chamarajanagar", "Karnataka", 1900, "Male Mahadeshwara Temple Access, Bandipur Access"),
    ("Gopalaswamy Betta", "Karnataka", 1900, "Himavad Gopalaswamy Temple, Foggy Hills"),
    ("Shimoga", "Karnataka", 2000, "Jog Falls Access, Sakrebailu Elephant Camp"),
    ("Kargal", "Karnataka", 2000, "Jog Falls Base, Linganamakki Dam"),
    ("Honnavar", "Karnataka", 2100, "Sharavathi Backwaters, Apsarkonda Falls"),
    ("Karwar", "Karnataka", 2100, "Rabindranath Tagore Beach, Devbagh Beach, Sadashivgad Fort"),
    ("Devbagh", "Karnataka", 2100, "Beach Resort, Water Sports, Island"),
    ("Anshi National Park", "Karnataka", 2100, "Kali Tiger Reserve, Wildlife"),
]

# Create lookup dictionary: city name (lowercase) → full data
CITY_PLACES = {}
for city, state, budget, attractions in travel_data:
    places = [p.strip() for p in attractions.split(",")]
    CITY_PLACES[city.lower()] = {
        "city": city,
        "state": state,
        "budget": budget,
        "places": places
    }

# ================= WEATHER FUNCTIONS =================
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},India&appid={WEATHER_API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        d = r.json()
        condition = d["weather"][0]["main"].lower()
        icon_map = {
            "rain": "rain.gif", "drizzle": "rain.gif",
            "thunderstorm": "storm.gif",
            "cloud": "clouds.png",
        }
        icon = icon_map.get(condition.split()[0], "sun.png") if any(k in condition for k in icon_map) else "sun.png"
        bg = "rain" if "rain" in condition else "storm" if "thunder" in condition else "cloudy" if "cloud" in condition else "sunny"

        return {
            "temp": round(d["main"]["temp"]),
            "humidity": d["main"]["humidity"],
            "condition": d["weather"][0]["description"].title(),
            "icon": icon,
            "bg": bg
        }
    except:
        return None

def get_rain_forecast(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},India&appid={WEATHER_API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return {"chance": "--", "umbrella": False}
        data = r.json()["list"][:8]
        rain_chance = round(sum(item.get("pop", 0) for item in data) / len(data) * 100)
        return {"chance": rain_chance, "umbrella": rain_chance >= 40}
    except:
        return {"chance": "--", "umbrella": False}

def clothes_dry_decision(weather, rain):
    if not weather:
        return {"status": "Unknown", "message": "Data unavailable", "good": False}
    humidity = weather["humidity"]
    rain_chance = rain["chance"] if rain["chance"] != "--" else 0
    temp = weather["temp"]
    if rain_chance >= 40:
        return {"status": "Not Ideal", "message": "High rain chance", "good": False}
    if humidity >= 80:
        return {"status": "Not Ideal", "message": "High humidity", "good": False}
    if temp < 18:
        return {"status": "Not Ideal", "message": "Too cold", "good": False}
    return {"status": "Good to Dry", "message": "Perfect conditions", "good": True}

# ================= ROUTES =================
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, name) VALUES (?, ?)", (email, name))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
        session["user"] = name
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    city = None
    city_data = None
    weather = rain = drying = None

    if request.method == "POST":
        city = request.form.get("city")
        if city:
            session["selected_city"] = city.strip()

    # Keep city if coming back from smart advice
    if not city and "selected_city" in session:
        city = session["selected_city"]

    if city:
        weather = get_weather(city)
        rain = get_rain_forecast(city)
        if weather and rain:
            drying = clothes_dry_decision(weather, rain)

        # Find places for the city (case-insensitive)
        city_lower = city.lower()
        if city_lower in CITY_PLACES:
            data = CITY_PLACES[city_lower]
            city_data = {
                "city": data["city"],
                "state": data["state"],
                "budget": data["budget"],
                "places": data["places"]
            }

    return render_template(
        "dashboard.html",
        user=session["user"],
        weather=weather,
        rain=rain,
        drying=drying,
        city_data=city_data,
        city=city
    )

@app.route("/smart-advice")
def smart_advice():
    if "user" not in session or "selected_city" not in session:
        return redirect(url_for("dashboard"))
    city = session["selected_city"]
    weather = get_weather(city)
    rain = get_rain_forecast(city)
    advice = []
    if weather and rain:
        temp = weather["temp"]
        rain_chance = rain["chance"] if rain["chance"] != "--" else 0
        if rain_chance >= 60:
            advice.append("☔ Heavy rain expected")
        elif rain_chance >= 30:
            advice.append("🌦 Possible rain — carry umbrella")
        else:
            advice.append("☀️ Clear weather")
        if temp >= 35:
            advice.append("🥵 Very hot — stay hydrated")
        elif temp <= 15:
            advice.append("🧥 Cool — wear warm clothes")
        else:
            advice.append("😊 Pleasant day , Good for outdoor activities")
    else:
        advice = ["Weather data currently unavailable"]
    return render_template("smart_advice.html", user=session["user"], city=city, advice_list=advice)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)