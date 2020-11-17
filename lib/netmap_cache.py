import json

import netmap

class Netmap_cache(netmap.Netmap):
    def __init__(self, network_dir, cache_dir, debug=False):
        super().__init__(network_dir, debug)
        self.cache_dir = cache_dir
        self.cache_path = self.cache_dir / ('%s_cache_map.json' % self.network_dir.name)

    def process(self):
        self.cache_is_valid = self._cache_is_valid()
        if not self.cache_is_valid:
            super().process()

    def summary(self):
        raise Exception("Netmap_cache does not support summary")

    def map(self):
        if self.cache_is_valid:
            self._debug("using cache file %s" % self.cache_path)
            map_json = json.loads(self.cache_path.read_text())
            nodes, links, self.stats = map_json['nodes'], map_json['links'], map_json['stats']
        else:
            nodes, links = super().map()
            map_dict = { 'nodes': nodes, 'links': links, 'stats': self.stats }
            map_json = json.dumps(map_dict, indent=4, sort_keys=True)
            if self.cache_path.exists():
                self.cache_path.unlink()
            self.cache_path.write_text(map_json)
            self.cache_is_valid = True
        return nodes, links

    def _cache_is_valid(self):
        if not self.cache_path.is_file():
            return False
        cache_mtime = self.cache_path.stat().st_mtime
        if self.network_dir.stat().st_mtime > cache_mtime:
            return False
        for f in self.network_dir.iterdir():
            if f.stat().st_mtime > cache_mtime:
                return False
        return True
