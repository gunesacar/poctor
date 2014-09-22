import hashlib
FP_NOJS = 'no_js'  # default value when JS is disabled 
DB_CONN_TIMEOUT = 30

class TBFingerprint(object):    
    def __init__(self):
        self.user_agent = ''
        self.http_accept = ''
        self.plugins = FP_NOJS
        self.timezone = FP_NOJS
        self.video = FP_NOJS
        self.fonts = FP_NOJS
        self.cookie_enabled = ''
        self.supercookies = FP_NOJS
        self.js_enabled = '0'
        self.js_user_agent = ''
        self.tbb_v = '3.5'
        self.signature = ''  # complete fingerprint

    def __iter__(self):
        for atrbt in self.__dict__.keys():
        	yield atrbt, self.__getattribute__(atrbt)

def hash_text(text, algo='sha1'):
    """Return the hash value for the text."""
    h = hashlib.new(algo)
    h.update(text.encode('utf-8'))
    return h.hexdigest()
