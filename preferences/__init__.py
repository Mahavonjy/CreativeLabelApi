"""

    Init all variable global in project
"""

# BEAT LICENSE
BASIC_LICENSE = "basic_lease"
SILVER_LICENSE = "silver_lease"
GOLD_LICENSE = "gold_lease"
PLATINUM_LICENSE = "platinum_lease"

# COUNTRY
all_country_allowed = ["MG"]

# ALL AUDIO TYPE ALLOWED
OTHERS = "autres"
FOLK_ALLOWED = "Folk"
METAL_ALLOWED = "Metal"
MAKOSSA_ALLOWED = "Makossa"
FUNK_ALLOWED = "Funk"
GOSPEL_ALLOWED = "Gospel"
ZOUK_LOVE_ALLOWED = "Zouk-love"
HOUSE_ALLOWED = "House"
JAZZ_ALLOWED = "Jazz"
POP_ALLOWED = "Pop"
DUBSTEP_ALLOWED = "Dubstep"
SALEGY_ALLOWED = "Salegy"
SLAM_ALLOWED = "Slam"
TECHNO_ALLOWED = "Techno"
SWING_ALLOWED = "Swing"
SOUL_ALLOWED = "Soul"
RAP_ALLOWED = "Rap"
REGGAE_ALLOWED = "Reggae"
KOMPAS_ALLOWED = "Kompas"
ROCK_ALLOWED = "Rock"
RUMBA_ALLOWED = "Rumba"
SAMBA_ALLOWED = "Samba"
MALOYA_ALLOWED = "Maloya"
SLOW_ALLOWED = "Slow"
AFRO_POP_ALLOWED = "Afropop"
ACAPELLA_ALLOWED = "Acapella"
AFROBEAT_ALLOWED = "Afrobeat"
BLUES_ALLOWED = "Blues"
BREAKBEAT_ALLOWED = "Breakbeat"
CLASSIQUE_ALLOWED = "Classique"
KIZOMBA_ALLOWED = "Kizomba"
DANCEHALL_ALLOWED = "Dancehall"
ELECTRONICA_ALLOWED = "Electronica"
VAKODRAZANA_ALLOWED = "Vakondrazana"
KILALAKY_ALLOWED = "Kilalaky"
RNB_ALLOWED = "Rnb"
NDOMBOLO_ALLOWED = "Ndombolo"
BASESA_ALLOWED = "Basesa"
HIRA_GASY_ALLOWED = "Hira gasy"
BATRELAKY_ALLOWED = "Batrelaky"
REGGAE_MUFFIN_ALLOWED = "Reggae-muffin"
REGGAETON_ALLOWED = "Reggaeton"
REMIX_ALLOWED = "Remix"
GOMA_ALLOWED = "Goma"
KUDURO_ALLOWED = "Kuduro"
AFRO_TRAP_ALLOWED = "Afro-trap"
KAWITRY_ALLOWED = "Kawitry"
MALESA_ALLOWED = "Malesa"
TSAPIKY_ALLOWED = "Tsapiky"
ZAFINDRAONA_ALLOWED = "Zafindraona"
HIP_HOP_ALLOWED = "Hip-hop"
COUPE_DECALE_ALLOWED = "Coupé-Décalé"

# CLOUD STORAGE NAME
CLOUD_BEATS = 'beats'
CLOUD_AUDIOS = 'audios'
CLOUD_INVOICE = 'invoices'
CLOUD_BEAT_STEMS = 'beats_stems'
CLOUD_TECHNICAL_SHEET = 'technical_sheets'
CLOUD_IMAGES_AUDIOS_TYPE = 'images/audios'
CLOUD_IMAGES_BEATS_TYPE = 'images/beats'
CLOUD_IMAGES_PLAYLISTS_TYPE = 'images/playlists'
CLOUD_IMAGES_SERVICES_TYPE = 'images/services'
CLOUD_IMAGES_PROFILES_TYPE = 'images/profiles'
CLOUD_IMAGES_PARTNERS_TYPE = 'images/partners'
CLOUD_IMAGES_FOLDERS = [CLOUD_TECHNICAL_SHEET, CLOUD_IMAGES_AUDIOS_TYPE, CLOUD_IMAGES_BEATS_TYPE,
                        CLOUD_IMAGES_PLAYLISTS_TYPE, CLOUD_IMAGES_SERVICES_TYPE,
                        CLOUD_IMAGES_PROFILES_TYPE, CLOUD_IMAGES_PARTNERS_TYPE]

# PRESTIGE TYPE
PRESTIGE_ALLOWED_TYPE = {"basy_mena": "Basy Mena", "cafe": "café", "prestige_money": "Prestige Money"}

# MUSICAL ALLOWED TYPE
ALLOWED_MUSIC_MP3 = "mp3"
ALLOWED_MUSIC_WAVE = "wave"
ALLOWED_MUSIC_WAV = "wav"
ALLOWED_MUSIC_X_WAV = "x-wav"
ALLOWED_MUSIC_MPEG = "mpeg"

# ALL MUSICAL GENRES
MUSICAL_GENRE_BEATS = "beats"
MUSICAL_GENRE_MUSIC = "music"

# DIFFERENT TYPE OF REFUND POLICY
REFUND_POLICY_FLEXIBLE = "flexible"
REFUND_POLICY_STRICT = "strict"

# USER TYPE DEFAULT
USER_ARTIST_DJ = "dj"
USER_AUDITOR_PRO = "professional_auditor"  # DEFAULT
USER_ARTIST_BEATMAKER = "beatmaker"
USER_ARTIST_MUSICIAN = "artist_musician"
USER_ARTIST_COMEDIAN = "comedian"
USER_AUDIOVISUAL_SPECIALIST = "audiovisual_specialist"
USER_ARTIST_MAGICIAN = "magician"
USER_ARTIST_DANCERS = "dancers"
USER_STREET_ARTIST = "street_artists"

# USER TYPE FR
USER_ARTIST_DJ_FR = "Dj"
USER_ARTIST_BEATMAKER_FR = "Beatmaker"
USER_ARTIST_MUSICIAN_FR = "Chanteur/Musicien"
USER_ARTIST_COMEDIAN_FR = "Comédiens"
USER_AUDIOVISUAL_SPECIALIST_FR = "Spécialiste de l’audiovisuel"
USER_ARTIST_MAGICIAN_FR = "Magiciens"
USER_ARTIST_DANCERS_FR = "Danseurs"
USER_STREET_ARTIST_FR = "Cirque/Artistes de la Rue"

# IMAGE TYPE ALLOWED
IMAGE_ALLOWED_TYPE_UPPERCASE_JPEG = "JPEG"
IMAGE_ALLOWED_TYPE_LOWERCASE_JPEG = "jpeg"
IMAGE_ALLOWED_TYPE_PNG = "PNG"

# FILE ALLOWED
FILE_ZIPPED = "zip"

# LANG ALLOWED
FR = "fr"

# THEMATICS OPTIONS
MUSIC_VIDEO_EDITOR = 'Monteur vidéoclip'
CAMERAMAN = 'Cameraman'
PHOTOGRAPHERS = 'Photographes'
ACROBATE = 'Acrobate'
CLOWN = 'Clown'
FIRE_EATERS = 'Cracheur de feu'
BALANCE_TRAINERS = 'Dompteur Equilibriste'
JUGGLER = 'Jongleur'
PUPPETEER = 'Marionnettiste'
MIME = 'Mime'
BURLESQUE = 'Burlesque'
COMEDY = 'Comédie'
STORYTELLER = 'Conteur'
DRAMA = 'Drame'
EXPERIMENTAL = 'Expérimental'
HUMORIST = 'Humoriste'
IMITATOR = 'Imitateur'
ANIMATOR = 'Animateur'
CABARET = 'Cabaret'
MIX = 'Mix'
PRESTIDIGITATORS = 'Prestidigitateurs'
MENTALISTS = 'Mentalistes'
CLOSE_UP = 'Close-ups'
LIVE_SET = 'Live set'
DJ_SET = 'DJ Set'
STAND_UP = 'Stand up'
VIDEO_CLIP_DIRECTOR = 'Réalisateur clip vidéo'

# DANCE
BACHATA = "Bachata"
CAPOEIRA = "Capoeira"
CHACHACHA = "Chachacha"
CLASSIC = "Classique"
CONTEMPORARY = "Contemporain"
ETHNIQUE = "Ethnique"
IMPROVISATION = "Improvisation"
MODERN = "Moderne"
ORIENTAL = "Oriental"
SALSA = "Salsa"
TANGO = "Tango"

# EVENTS
MARIAGE = "Mariage"
TRADITIONAL_PARTY = "Fête traditionnelle"
BIRTHDAY_PARTY = "Anniversaire"
SHOW_CASE = "Show-case"
FESTIVAL = "Festival et défilé"
SPORT_EVENTS = "Événement sportif"
ENTERPRISE_EVENTS = "Évènement d’entreprise"
ASSOCIATION_EVENTS = "Évènement associative"
CREATE_BEATS = "Création d’instrumentale"
VIDEO_EDITOR = "Montage vidéo"

# STATUS
PENDING = "pending"
ACCEPTED = "accepted"
DECLINED = "declined"

# TRANSACTION_TYPE
KANTOBIZ = "kantobiz"
BEATMAKING = "beats"

# Profile
profile_keys_to_remove = ['address', 'age', 'city', 'region', 'social_id', 'photo', 'email', 'cover_photo', 'phone']
