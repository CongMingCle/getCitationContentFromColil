import urllib.parse
import urllib.request

class SendRequest():
    def __init__(self, url, paraDict) -> None:
        self.url = url
        self.paraDict = paraDict
        pass

    def byGet(self):
        fullUrl = self.url + urllib.parse.urlencode(self.paraDict)
        self.data = urllib.request.urlopen(fullUrl).read().decode("utf-8")
        return self.data

    def byPost(self):
        self.data = urllib.request.urlopen(self.url, self.paraDict).read().decode("utf-8")
        return self.data