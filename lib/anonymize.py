import hashlib
import binascii

class Anonymize(object):
    def __init__(self, salt):
        try:
            self.salt = binascii.unhexlify(salt)
            self._selftest()
        except Exception as e:
            print("Error: Could not initialize Netmap_anonymize")
            raise e

    def text(self, data):
        h = hashlib.blake2b(digest_size=8, salt=self.salt, person=b"text")
        h.update(bytes(data, 'utf8'))
        return h.hexdigest()

    def int(self, data):
        h = hashlib.blake2b(digest_size=2, salt=self.salt, person=b"int")
        h.update(data.to_bytes(4, byteorder='big'))
        return int(h.hexdigest(), 16)

    def ip(self, data):
        h = hashlib.blake2b(digest_size=4, salt=self.salt, person=b"ip")
        h.update(bytes(data, 'ascii'))
        d = h.hexdigest()
        return '.'.join([ str(int(d[x:x+2], 16)) for x in range(0, len(d), 2) ])

    def mac(self, data):
        h = hashlib.blake2b(digest_size=6, salt=self.salt, person=b"mac")
        h.update(bytes(data, 'ascii'))
        d = h.hexdigest()
        return ':'.join([ d[x:x+2] for x in range(0, len(d), 2) ])

    def _selftest(self):
        h = hashlib.blake2b(digest_size=8, salt=self.salt, person=b"test")
        h.update(bytes('toto', 'utf8'))
        h.hexdigest()
