# -*- coding: utf-8 -*-
STORES_CONFIG = {
    'falabella': {
        'base_url': 'https://www.falabella.com/cl',
        'categories': [
            'https://www.falabella.com/cl/category/cat7690599/liquidacion',
            'https://www.falabella.com/cl/category/cat4093/Tecnologia'
        ]
    },
    'paris': {
        'base_url': 'https://www.paris.cl',
        'categories': [
            'https://www.paris.cl/liquidacion/',
            'https://www.paris.cl/tecnologia/'
        ]
    },
    'ripley': {
        'base_url': 'https://simple.ripley.cl',
        'categories': [
            'https://webcache.googleusercontent.com/search?q=cache:https://simple.ripley.cl/tecno/computacion'
        ]
    },
    'hites': {
        'base_url': 'https://www.hites.com',
        'categories': [
            'https://www.hites.com/outlet/'
        ]
    },
    'sodimac': {
        'base_url': 'https://www.sodimac.cl/sodimac-cl/',
        'categories': [
            'https://webcache.googleusercontent.com/search?q=cache:https://www.sodimac.cl/sodimac-cl/category/scat111816/ofertas-y-liquidaciones'
        ]
    }
}

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

MIN_DELAY = 1
MAX_DELAY = 3
REQUEST_TIMEOUT = 10

RETRY_CONFIG = {
    'max_attempts': 3,
    'delay_between_attempts': 2,
    'backoff_factor': 2,
    'max_delay': 10
}

RATE_LIMIT_CONFIG = {
    'delay_between_requests': 1
}
