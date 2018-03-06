import requests

DEFAULT_BASE_ENDPOINT = 'http://localhost:8080/'


class TranslationClient(object):
    def __init__(self, username, password, base_endpoint=DEFAULT_BASE_ENDPOINT):
        assert isinstance(username, unicode)
        assert isinstance(password, unicode)
        
        self._base_endpoint = base_endpoint
        self._sid = self._login(username, password)
    
    def __del__(self):
        self._logout()

    def _check_for_errors(self, json):
        if 'error_type' not in json:
            return
        error_type = eval(json['error_type'], {})
        error_msg = json['error_msg']
        raise error_type(error_msg)

    def _login(self, username, password):
        endpoint = self._base_endpoint + 'login'
        r = requests.post(endpoint, json={'username': username,
                                        'password': password})
        json = r.json()
        self._check_for_errors(json)
        assert 'sid' in json
        return json['sid']
    
    def _logout(self):
        endpoint = self._base_endpoint + 'logout'
        r = requests.post(endpoint, json={'sid': self._sid})
        if r.status_code == 200:
            return
        self._check_for_errors(r.json())
        assert False

    def translate(self, string, src_lang, target_lang, sync=False):
        assert isinstance(string, unicode)
        assert isinstance(src_lang, unicode)
        assert isinstance(target_lang, unicode)
        
        endpoint = self._base_endpoint + 'translate'
        r = requests.post(endpoint, json={'sid': self._sid,
                                        'string': string,
                                        'src_lang': src_lang,
                                        'target_lang': target_lang,
                                        'sync': sync})
        json = r.json()
        self._check_for_errors(json)
        
        if not sync:
            assert 'uuid' in json
            return json['uuid']
        
        assert 'result' in json
        return json['result']
    
    def poll(self, uuid=None):
        endpoint = self._base_endpoint + 'poll'
        
        json = {'sid': self._sid}
        if uuid is not None:
            json['uuid'] = uuid
        
        r = requests.post(endpoint, json=json)
        json = r.json()
        self._check_for_errors(json)
        
        assert 'result' in json
        return json['result']
    
    def cancel(self, uuid=None):
        endpoint = self._base_endpoint + 'cancel'
        
        json = {'sid': self._sid}
        if uuid is not None:
            json['uuid'] = uuid
        
        r = requests.post(endpoint, json=json)
        if r.status_code == 200:
            return
        
        self._check_for_errors(r.json())
        assert False
