import webview
from pole import PoleTracking


class API:
    def __init__(self):
        self.VR = PoleTracking()


if __name__ == "__main__":
    api = API()

    webview.create_window(
        'eva',
        'frontend/index.html', 
        js_api=api,
        width=1280,
        height=800,
        min_size=(1280, 800),
        resizable=True
    )

    webview.start()
