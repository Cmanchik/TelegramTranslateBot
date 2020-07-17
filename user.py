import json


class User:
    def __init__(self, first_lang='ru', second_lang='en', choice_lang=0, is_translate=False, jsonStr=''):
        if jsonStr:
            params = json.loads(jsonStr)
            self.first_lang = params['first_lang']
            self.second_lang = params['second_lang']
            self.choice_lang = params['choice_lang']
            self.is_translate = params['is_translate']
        else:
            self.first_lang = first_lang
            self.second_lang = second_lang
            self.choice_lang = choice_lang
            self.is_translate = is_translate

    def serialisation(self):
        params = {
            'first_lang': self.first_lang,
            'second_lang': self.second_lang,
            'choice_lang': self.choice_lang,
            'is_translate': self.is_translate
        }

        return json.dumps(params)
