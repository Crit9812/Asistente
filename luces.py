import urllib.request


ESP_IP = "192.168.1.50"
NUM_STRIPS = 3


def encenderLuces():
    for i in range(NUM_STRIPS):
        url = f"http://{ESP_IP}/power?strip={i}&state=1"
        urllib.request.urlopen(url, timeout=2).read()


def apagarLuces():
    for i in range(NUM_STRIPS):
        url = f"http://{ESP_IP}/power?strip={i}&state=0"
        urllib.request.urlopen(url, timeout=2).read()
