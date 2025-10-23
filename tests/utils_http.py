class DummyResp:
    def __init__(self, *, status_code=200, json_data=None, text="OK"):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        return self._json


def make_get_stub(sequence_or_single):
    """
    Devuelve una función stub para sustituir requests.get.
    Si pasas una lista/tupla de DummyResp, irá devolviendo cada una en orden.
    """
    if isinstance(sequence_or_single, (list, tuple)):
        items = list(sequence_or_single)
        def _get(*args, **kwargs):
            if not items:
                return DummyResp(status_code=500, json_data={"error": "exhausted"}, text="exhausted")
            return items.pop(0)
        return _get

    single = sequence_or_single
    def _get(*args, **kwargs):
        return single
    return _get
