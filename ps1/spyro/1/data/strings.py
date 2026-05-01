"""
Spyro the Dragon (PS1 PAL) - Irish Language Translation Data
Encoding: fada characters use two-byte encoding: Xa where X is the base letter
  Á = Aa, É = Ea, Í = Ia, Ó = Oa, Ú = Ua
"""

# Accent encoding helper
def encode_fada(s):
    """Convert Irish text with fadas to ROM encoding."""
    replacements = {
        'Á': 'Aa', 'É': 'Ea', 'Í': 'Ia', 'Ó': 'Oa', 'Ú': 'Ua',
        'á': 'aa', 'é': 'ea', 'í': 'ia', 'ó': 'oa', 'ú': 'ua',
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s

# Translation table
# Format: offset -> (english, irish_display, irish_encoded, budget)
TRANSLATIONS = {
    # Game state
    0x834:  ('COMPLETED',           'DÉANTA',               'DEaANTA',              11),
    0x880:  ('TIME IS UP',          'AM CAITE',             'AM CAITE',             11),
    0x904:  ('ALL IN ONE',          'GACH RUD',             'GACH RUD',             11),
    0x9a8:  ('TRY AGAIN?',          'ARÍS É?',              'ARIaS Ea?',            11),
    0x9fc:  ('TIME ATTACK',         'CATH AMA',             'CATH AMA',             11),
    0xa44:  ('BEST TIME',           'BUAIC AMA',            'BUAIC AMA',            11),
    0xa84:  ('YOUR TIME',           'DO AM',                'DO AM',                11),
    0xad0:  ('NEW RECORD',          'RECORD NUA',           'RECORD NUA',           11),

    # Intro / navigation
    0xb88:  ('PRESS START',         'BRÚTH START',          'BRUTH START',          11),
    0xc00:  ('IN THE WORLD OF DRAGONS...', 'I NDOMHAN NA NDRAGAN...', 'I NDOMHAN NA NDRAGAN...', 27),
    0xc80:  ('THE ADVENTURE BEGINS...', 'TOSAÍONN EACHTRA...', 'TOaSAaIONN EACHTRA...', 23),
    0xd04:  ('THE ADVENTURE CONTINUES...', 'LEANANN AN EACHTRA...', 'LEANAaNN AN EACHTRA...', 27),
    0xd8c:  ('ENTERING DEMO MODE...', 'MÓD DEMO AG TOSÚ...', 'MOaD DEMO AG TOaSUa...', 23),
    0xdc8:  ('DEMO MODE',           'MÓD DEMO',             'MOaD DEMO',            11),
    0xe18:  ('RETURNING HOME...',   'AG FILLEADH...',       'AG FILLEADH...',       19),
    0xe58:  ('CONFRONTING',         'AG IONSAÍ',            'AG IONSAaI',           11),
    0xea0:  ('ENTERING',            'AG DUL -',             'AG DUL -',             11),

    # Homeworld transition screens (French slots repurposed)
    0xed0:  ('MONDE DES TISSEURS DE REVES', 'DOMHAN NA FÍTHEOIRÍ', 'DOMHAN NA FIaTHEOIRIa', 31),
    0xef0:  ('MONDE DES CREATEURS D ANIMAUX', 'DOMHAN NA FIADHAITHE', 'DOMHAN NA FIADHAITHE', 31),
    0xf10:  ('MONDE DES OUVRIERS MAGIQUES', 'DOMHAN NA CEARDAÍOCHTA', 'DOMHAN NA CEARDAaIOCHTA', 27),
    0xf2c:  ('MONDE DES PACIFIQUES', 'DOMHAN NA CAOMHNÓIRÍ', 'DOMHAN NA CAOMHNOaIRIa', 23),
    0xf44:  ('MONDE DES ARTISANS',  'DOMHAN CEARDAITHE',    'DOMHAN CEARDAITHE',    19),

    # HUD / treasure
    0x1020: ('TREASURE FOUND',      'STÓR FAIGHTE',         'STOaR FAIGHTE',        15),
    0x1070: ('TOTAL TREASURE',      'STÓR IOMLÁN',          'STOaR IOMLAaN',        15),

    # Pause menu
    0x10b0: ('CONTINUE',            'AR AGHAIDH',           'AR AGHAIDH',           11),
    0x10ec: ('INVENTORY',           'LIOSTA',               'LIOSTA',               11),
    0x1140: ('EXIT LEVEL',          'IMIGH AS',             'IMIGH AS',             11),
    0x118c: ('QUIT GAME',           'ÉIRIGH AS',            'EaIRIGH AS',           11),
    0x11d8: ('SOUND EFFECTS',       'FUAIMEANNA',           'FUAIMEANNA',           15),
    0x1218: ('MUSIC VOLUME',        'TOIRT CEOIL',          'TOIRT CEOIL',          15),
    0x125c: ('VIBRATION',           'CRITH',                'CRITH',                11),
    0x1234: ('SPEAKER SETUP',       'CALLAIRE',             'CALLAIRE',             15),
    0x12cc: ('SCREEN ADJUST',       'SCAILEÁN',             'SCAILEAaN',            15),
    0x130c: ('VERTICAL',            'INGEARACH',            'INGEARACH',            11),

    # Save/load
    0x13ac: ('SAVE GAME',           'SÁBHÁIL',              'SAaBHAaIL',            11),
    0x1404: ('REPLAY DRAGON',       'ATHSHEINM',            'ATHSHEINM',            15),
    0x1470: ('NO SAVE FILE',        'GÁN COMHAD',           'GAaN COMHAD',          15),
    0x14d8: ('PLEASE RESTART WITH', 'ATHOSÓIL LE',          'ATHOSOaIL LE',         19),
    0x1548: ('A MEMORY CARD TO',    'CAIRT CHUIMHNE',       'CAIRT CHUIMHNE',       19),
    0x15b4: ('ENABLE SAVE GAMES',   'LE HAGHAIDH SABH',     'LE HAGHAaIDH SABH',    19),
    0x1614: ('SAVING...',           'AG SABH...',           'AG SABH...',           11),
    0x1680: ('NO MEMORY CARD',      'GÁN CAIRT',            'GAaN CAIRT',           15),
    0x16cc: ('PLEASE REPLACE',      'CUIR ISTEACH',         'CUIR ISTEACH',         15),
    0x1750: ('MEMORY CARD.',        'CAIRT CUIMHNE.',       'CAIRT CUIMHNE.',       15),
    0x17b4: ('SAVE ERROR',          'EARRAID',              'EARRAID',              11),
    0x1808: ('PLEASE CHECK THAT',   'SEICEÁIL',             'SEICEaAIL',            19),
    0x1868: ('THE MEMORY CARD',     'AN CAIRT',             'AN CAIRT',             15),
    0x18c4: ('IS STILL IN PLACE',   'TÁ SÉ I GCEART',       'TAa SEa I GCEART',     19),
    0x1934: ('SAVE FAILED',         'SABH THEIP',           'SABH THEIP',           11),
    0x19b8: ('SAVE SUCCESSFUL',     'SÁBHÁILTE',            'SAaBHAaILTE',          15),
    0x19f4: ('MEMORY CARD 1',       'CAIRT CUIMHNE 1',      'CAIRT CUIMHNE 1',      15),
    0x1a30: ('MEMORY CARD 2',       'CAIRT CUIMHNE 2',      'CAIRT CUIMHNE 2',      15),

    # Balloonist
    0x1a80: ('THE BALLOONIST',      'AN BALLÓNAÍ',          'AN BALLONAaI',         15),
    0x1adc: ('WHERE TO, SPYRO?',    'CÁ DTRIALL, SPYRO?',  'CAa DTRIALL, SPYRO?', 19),
    0x1b3c: ('NEED A LIFT?',        'ARDAIGH TÉ?',          'ARDAaIGH TEa?',        15),
    0x1b9c: ('ARE YOU READY TO GO?', 'AN BHFUIL TÚ ULLAMH?', 'AN BHFUIL TUa ULLAMH?', 23),
    0x1c00: ('WOULD YOU LIKE TO GO?', 'AR MHAITH LEAT IMEACHT?', 'AR MHAITH LEAT IMEACHT?', 23),
    0x1c4c: ('STAY HERE',           'FAN ANSEO',            'FAN ANSEO',            11),

    # Homeworld short labels (minimap/inventory)
    0x1da0: ("GNASTY'S WORLD",      'DOMHAN GNASTY',        'DOMHAN GNASTY',        15),
    0x1db0: ('DREAM WEAVERS',       'FÍTHEOIRÍ',            'FIaTHEOIRIa',          15),
    0x1dc0: ('BEAST MAKERS',        'FIADHAITHE',           'FIADHAITHE',           15),
    0x1dd0: ('MAGIC CRAFTERS',      'CEARDAÍOCHT',          'CEARDAaIOCHT',         15),
    0x1de0: ('PEACE KEEPERS',       'CAOMHNÓIRÍ',           'CAOMHNOaIRIa',         15),
    0x1df0: ('ARTISANS',            'CEARDAITHE',           'CEARDAITHE',           11),

    # Navigation
    0x22a8: ('RETURN HOME',         'ABHAILE',              'ABHAILE',              11),

    # Level names - Gnasty's World
    0x22b4: ("GNASTY'S LOOT",       'CREACH GNASTY',        'CREACH GNASTY',        15),
    0x22c4: ('GNASTY GNORC',        'GNASTY GNORC',         'GNASTY GNORC',         15),
    0x22d4: ('TWILIGHT HARBOUR',    'CUAN CLAPSHOLAS',      'CUAN CLAPSHOLAS',      19),
    0x22e8: ('GNORC COVE',          'CUAS GNORC',           'CUAS GNORC',           11),
    0x22f4: ('GNORC GNEXUS',        'NEAS GNORC',           'NEAS GNORC',           15),

    # Level names - Peace Keepers
    0x2304: ('ICY FLIGHT',          'AN tSIOC',             'AN tSIOC',             11),
    0x2310: ('HAUNTED TOWERS',      'TÚIR TAIBHSÍ',         'TUaIR TAIBHSIa',       15),
    0x2320: ('LOFTY CASTLE',        'CAISLEÁN ARD',         'CASILEAaN ARD',        15),
    0x2330: ('DARK PASSAGE',        'BEALACH DORCHA',       'BEALACH DORCHA',       15),

    # Level names - Beast Makers
    0x2340: ('WILD FLIGHT',         'STOIRM',               'STOIRM',               11),
    0x234c: ('METALHEAD',           'CLOIGEANN',            'CLOIGEANN',            11),
    0x2358: ('TREE TOPS',           'BARR CRANN',           'BARR CRANN',           11),
    0x2364: ('MISTY BOG',           'BOGACH CEO',           'BOGACH CEO',           11),
    0x2370: ('TERRACE VILLAGE',     'BAILE LÉIBHINN',       'BAILE LEaIBHINN',      15),
    0x2380: ('CRYSTAL FLIGHT',      'EITILT GLOINE',        'EITILT GLOINE',        15),

    # Level names - Magic Crafters
    0x2390: ('BLOWHARD',            'SÉIDIRE',              'SEaIDIRE',             11),
    0x239c: ('WIZARD PEAK',         'BUAIC DRAOI',          'BUAIC DRAOI',          11),
    0x23a8: ('HIGH CAVES',          'UAIMHEANNA',           'UAIMHEANNA',           11),
    0x23b4: ('ALPINE RIDGE',        'DROIM SLÉIBHE',        'DROIM SLEaIBHE',       15),
    0x23c4: ('NIGHT FLIGHT',        'OÍCHE',                'OaICHE',               15),
    0x23d4: ('DOCTOR SHEMP',        'DOCHTÚIR SHEMP',       'DOCHTUaIR SHEMP',      15),

    # Level names - Gnasty's World continued
    0x23e4: ('ICE CAVERN',          'UAIMH ÓÍ',             'UAIMH OaIa',           11),
    0x23f0: ('CLIFF TOWN',          'BAILE AILL',           'BAILE AILL',           11),
    0x23fc: ('DRY CANYON',          'LOG TÍR',              'LOG TIaR',             11),
    0x2408: ('SUNNY FLIGHT',        'LÁ GEAL',              'LAa GEAL',             15),

    # Level names - Artisans
    0x2418: ('TOWN SQUARE',         'CEARNÓG',              'CEARNOaG',             11),
    0x2424: ('DARK HOLLOW',         'LOG DORCHA',           'LOG DORCHA',           11),
    0x2430: ('STONE HILL',          'CNOC CLOICH',          'CNOC CLOICH',          11),

    # Balloonist dialogue - first visit
    0x4a70: ('WORLD IF YOU LIKE.',  'MÁ SÁILL LEAT.',       'MAa SAaILL LEAT.',     19),
    0x4a84: ('THE PEACE KEEPERS',   'NA CAOMHNÓIRÍ',        'NA CAOMHNOaIRIa',      19),
    0x4a98: ('YOU MAY TRAVEL TO',   'IS FÉIDIR LEAT DUL',   'IS FEaDIaR LEAT DUL',  19),
    0x4bac: ('COULD DO IT.',        'DÉANFAÍ É.',          'DEaANFAIa Ea.',        15),
    0x4bbc: ("I DIDN'T THINK YOU",  'NÍOR CHEAP ME GO',     'NIaOR CHEAP ME GO',    19),
    0x4bd0: ('WELL DONE SPYRO!',    'MAITH THÚ, SPYRO!',    'MAITH THUa, SPYRO!',   19),

    # Balloonist dialogue - second visit
    0x4e24: ('RESCUED 10 DRAGONS.', '10 NDRAGAN SAORTHA.',  '10 NDRAGAN SAORTHA.',  19),
    0x4e38: ('AFTER YOU HAVE',      'TAR ÉIS DUIT',         'TAR EaIS DUIT',        15),
    0x4e48: ('COME BACK TO SEE ME', 'TAR AR AIS CHUGAM',    'TAR AR AaIS CHUGAM',   19),

    # Balloonist dialogue - prove your worth
    0x4f64: ('TO A NEW WORLD.',     'GO DOMHAN NUA.',        'GO DOMHAN NUA.',       15),
    0x4f74: ('THIS BALLOON TO FLY', 'AN BALLON SEO',        'AN BALLON SEO',        19),
    0x4f88: ('THEN YOU MAY USE',    'IS FÉIDIR LEAT',       'IS FEaDIaR LEAT',      19),
    0x5080: ('10 DRAGONS...',       '10 NDRAGAN...',        '10 NDRAGAN...',        15),
    0x5090: ('WORTH BY RESCUING',   'DO FHIÚNTAS AGUS',     'DO FHIUaNTAS AGUS',    19),
    0x50a4: ('IF YOU PROVE YOUR',   'MÁ CRUTHAÍONN',        'MAa CRUTHAaIONN',      17),

    # Flight level HUD (0x6c*** region - 8-byte slots)
    0x6bfa0: ('QUIT',               'FÁG',                  'FAaG',                 4),
    0x6bfa8: ('CRASHED',            'TITIM',                'TITIM',                7),
    0x6bfc0: ('TOTAL',              'IOML.',                'IOML.',                5),
    0x6bfe0: ('YES',                'SÉ',                   'SEa',                  3),
    0x6bff0: ('NO',                 'NÍ',                   'NIa',                  2),
    0x6bff4: ('COPTERS',            'ROTAR',                'ROTAR',                7),
    0x6c01c: ('BOATS',              'BÁD',                  'BAaD',                 5),
    0x6c05c: ('LIGHTS',             'SOILSE',               'SOILSE',               6),
    0x6c064: ('RINGS',              'ROTHA',                'ROTHA',                5),
    0x6c0cc: ('CHESTS',             'CÓFRA',                'COaFRA',               6),
    0x6c0d4: ('PLANES',             'EITILT',               'EITILT',               6),
    0x6c0dc: ('ARCHES',             'ÁIRSE',                'AaIRSE',               6),
    0x6c0e4: ('BARRELS',            'BAIRLA',               'BAIRLA',               7),
    0x6c17c: ('WORLD',              'DOMH.',                'DOMH.',                5),

    # Pause/options menu (0x6c*** region)
    0x6c1a4: ('PAUSED',             'SOSADH',               'SOSADH',               6),
    0x6c1cc: ('OPTIONS',            'SOCRÚ',                'SOCRUa',               7),
    0x6c264: ('CAMERA',             'CEAMARA',              'CEAMARA',              6),
    0x6c2a4: ('DONE',               'DÉANTA',               'DEaANTA',              4),
    0x6c2ec: ('ACTIVE',             'BEO',                  'BEO',                  6),
    0x6c30c: ('PASSIVE',            'STAD',                 'STAD',                 7),
    0x6c38c: ('RETRY',              'ARÍS',                 'AaRIS',                5),
    0x6c3e4: ('GO TO',              'GO DTÍ',               'GO DTI',               5),
    0x6c3f4: ('RESCUED',            'SAORTHA',              'SAORTHA',              7),

    # Dragon names section
    0x6c6a8: ('HOME',               'BAILE',                'BAILE',                7),

    # Flight level continue prompt
    0x968:   ('PRESS   BUTTON',     'BRÚTH   CNAIPE',       'BRUTH   CNAIPE',       14),
}

if __name__ == '__main__':
    print(f'Translation table: {len(TRANSLATIONS)} entries')
    translated = sum(1 for v in TRANSLATIONS.values() if v[1])
    print(f'Translated: {translated}')
    print(f'Remaining: {len(TRANSLATIONS) - translated}')
