import random
from datetime import datetime, timedelta
import os
import winsound

import pickle
from time import sleep

# Base class for accepting user command requests.
class Requester(object):
    
    def __init__(self, time_limit=timedelta(seconds=0)):
        self._time_limit = time_limit
        self._accepting = True
        self._data = {}

    def can_request(self, user):
        return datetime.now() - self._data.get(user, datetime.min) > self._time_limit

    def request(self, user, command):
        if self._accepting and self.can_request(user):
            self._data[user] = datetime.now()
            self.perform(user, command)

    def perform(self, user, command):
        raise NotImplementedError("Perform must be overridden in subclasses")

    def set_accepting(self, accepting):
        self._accepting = accepting

    def get_accepting(self):
        return self._accepting

    def set_timeout(self, seconds):
        self._time_limit = timedelta(seconds=seconds)


class TimeRequester(Requester):

    def __init__(self, time_limit=timedelta(seconds=30)):
        super().__init__(time_limit=time_limit)

    def perform(self, user, command):
        pass


class SoundRequester(Requester):
    """ Allow users to request sound effects """

    def __init__(self, sound_file, sound_folder):
        super().__init__(time_limit=timedelta(seconds=30))
        self._sounds = {}
        self._folder = sound_folder
        self.load_sounds(sound_file)

    def load_sounds(self, file):
        with open(file, 'r') as sound_file:
            for line in sound_file:
                if line.strip() == '':
                    continue
                name, path = line.split(':')
                name = name.strip()
                path = os.path.join(self._folder, path.strip())
                self._sounds[name] = path
    
    def perform(self, user, command):
        if command in self._sounds:
            winsound.PlaySound(self._sounds[command], (winsound.SND_FILENAME | winsound.SND_NOSTOP))


class ImageRequester(Requester):

    def __init__(self):
        super().__init__()
        self._requests = {}

    def perform(self, user, command):
        self._requests.setdefault(command, set())
        self._requests[command].add(user)

    def clear_requests(self):
        self._requests.clear()

    def get_requests(self):
        return self._requests

    def get_users_from_request(self, request):
        return self._requests.get(request, set())

    def save(self, filename):
        with open(filename, 'wb') as save_file:
            pickle.dump(self._requests, save_file)
        

    def load(self, filename):
        with open(filename, 'rb') as load_file:
            self._requests.update(pickle.load(load_file))

    def select_random_request(self):
        converted = [(k, len(v)) for (k, v) in self._requests.items()]
        if len(converted) == 0:
            return None

        total = sum(v for (_, v) in converted)

        chosen = random.choices(
            [name for (name, _) in converted],
            [v / total for (_, v) in converted],
            k=1
        )[0]

        del self._requests[chosen]
        return chosen


class RequestMuxer(object):

    def __init__(self):
        self._requesters = {}

    def add_requester(self, name, requester):
        self._requesters[name] = requester

    def get_requester(self, name):
        return self._requesters.get(name, None)

    def make_request(self, request_type, user, command):
        self._requesters.get(request_type).request(user, command)


def test_images():
    model = ImageRequester()

    model.request('die', 'harry')
    model.request('die', 'harry')
    model.set_accepting(False)
    model.request('hohohoho', 'troll')

    print(model.get_requests())

    res = model.select_random_request()
    print(res)
    print(model.get_requests())

def test_sounds():
    sounds = SoundRequester(sound_file='sounds/soundfile', sound_folder='sounds')
    sounds.request('harry', 'dickhead')
    sounds.request('haa', 'raw2')

def main():
    test_sounds()
    print('x')
    winsound.PlaySound(os.path.join(os.getcwd(), 'sounds', 'stop.wav'), winsound.SND_FILENAME)
    

   
    


if __name__ == "__main__":
    main()