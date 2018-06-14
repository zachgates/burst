from kivy.uix.floatlayout import FloatLayout
from kivy.app import App


class RootWidget(FloatLayout):
    pass


class MainApp(App):
    def build(self):
        return RootWidget()
if '__main__' == __name__:
    MainApp().run()
