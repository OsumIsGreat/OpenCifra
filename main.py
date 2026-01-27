from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
import threading
import requests
import logging
import json
import re
from bs4 import BeautifulSoup

KV = """
<SongItem@MDCard+ButtonBehavior>:
    title: ""
    artist: ""
    radius: [12, 12, 12, 12]
    padding: "12dp"
    size_hint_y: None
    height: dp(72)
    md_bg_color: app.theme_cls.bg_light
    elevation: 1
    ripple_behavior: True
    on_release: app.open_song(root.title, root.artist)

    MDBoxLayout:
        orientation: "horizontal"
        spacing: "10dp"
        adaptive_height: True
        pos_hint: {"center_y": .5}

        MDBoxLayout:
            size_hint: None, None
            size: dp(28), dp(28)
            radius: [14]
            md_bg_color: app.theme_cls.accent_color
            pos_hint: {"center_y": .5}
            
            MDIcon:
                icon: "music"
                size_hint: None, None
                size: dp(14), dp(14)
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {"center_x": .5, "center_y": .5}

        MDBoxLayout:
            orientation: "vertical"
            spacing: "2dp"
            adaptive_height: True
            pos_hint: {"center_y": .5}

            MDLabel:
                text: root.title
                font_style: "Body1"
                theme_text_color: "Primary"
                shorten: True
                shorten_from: "right"
                adaptive_height: True
                bold: True

            MDLabel:
                text: root.artist
                font_style: "Caption"
                theme_text_color: "Hint"
                shorten: True
                shorten_from: "right"
                adaptive_height: True

        MDIcon:
            icon: "chevron-right"
            size_hint: None, None
            size: dp(20), dp(20)
            theme_text_color: "Hint"
            pos_hint: {"center_y": .5}

<SearchScreen>:
    name: "search"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: app.theme_cls.bg_darkest

        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(140)
            padding: ["20dp", "24dp", "20dp", "16dp"]
            spacing: "8dp"
            md_bg_color: app.theme_cls.primary_color
            
            MDBoxLayout:
                orientation: "horizontal"
                adaptive_height: True
                spacing: "8dp"
                
                MDIcon:
                    icon: "guitar-pick"
                    size_hint: None, None
                    size: dp(32), dp(32)
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_y": .5}
                
                MDLabel:
                    text: "OpenCifra"
                    font_style: "H5"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    bold: True
                    adaptive_height: True
            
            MDLabel:
                text: "Your guitar companion"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 0.7
                adaptive_height: True

            MDTextField:
                id: search_field
                hint_text: "Search songs, artists..."
                mode: "round"
                size_hint_x: 1
                on_text: app.on_search_text(self.text)
                multiline: False
                fill_color_normal: 1, 1, 1, 0.15
                fill_color_focus: 1, 1, 1, 0.2
                hint_text_color_normal: 1, 1, 1, 0.5
                text_color_normal: 1, 1, 1, 1
                text_color_focus: 1, 1, 1, 1

        MDRecycleView:
            id: rv
            viewclass: "SongItem"
            RecycleBoxLayout:
                spacing: "8dp"
                padding: ["16dp", "16dp", "16dp", "80dp"]
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: "vertical"

        MDBoxLayout:
            size_hint_y: None
            height: dp(48)
            md_bg_color: app.theme_cls.bg_darkest
            
            MDLabel:
                text: "Made by Kayk Caputo"
                halign: "center"
                theme_text_color: "Hint"
                font_style: "Caption"

<LyricsScreen>:
    name: "lyrics"
    song_title: ""
    song_text: ""
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.08, 0.08, 0.1, 1

        MDTopAppBar:
            title: root.song_title
            anchor_title: "left"
            left_action_items: [["arrow-left", lambda x: app.back_to_search()]]
            elevation: 0
            md_bg_color: 0.08, 0.08, 0.1, 1
            specific_text_color: 1, 1, 1, 1

        MDScrollView:
            id: lyrics_scroll
            do_scroll_x: True
            do_scroll_y: True
            bar_width: dp(4)
            bar_color: app.theme_cls.primary_color
            
            MDBoxLayout:
                orientation: "vertical"
                size_hint: None, None
                height: self.minimum_height
                padding: 0
                spacing: 0
                
                MDCard:
                    id: lyrics_card
                    orientation: "vertical"
                    size_hint: None, None
                    height: lyrics_container.height + dp(32)
                    padding: ["20dp", "16dp", "20dp", "16dp"]
                    radius: [16]
                    md_bg_color: 0.12, 0.12, 0.14, 1
                    elevation: 0
                    
                    MDBoxLayout:
                        id: lyrics_container
                        orientation: "vertical"
                        size_hint: None, None
                        height: self.minimum_height
                        spacing: 0
"""


CHUNK_SIZE = 50


class SongItem(MDCard):
    title = StringProperty()
    artist = StringProperty()


class SearchScreen(MDScreen):
    pass


class LyricsScreen(MDScreen):
    song_title = StringProperty()
    song_text = StringProperty()


class OpenCifraApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "DeepPurple"
        Builder.load_string(KV)
        self.search_lock = threading.Lock()
        self.sm = MDScreenManager()
        self.sm.add_widget(SearchScreen())
        self.sm.add_widget(LyricsScreen())
        return self.sm

    def on_search_text(self, text):
        if len(text) < 2:
            self.root.get_screen("search").ids.rv.data = []
            return
        if self.search_lock.locked():
            return
        threading.Thread(
            target=self.fetch_suggestions, args=(text,), daemon=True
        ).start()

    def fetch_suggestions(self, query):
        with self.search_lock:
            url = f"https://solr.sscdn.co/cc/h2/?q={query}&limit=20&callback=suggest_callback"
            headers = {"User-Agent": "Mozilla/5.0"}
            try:
                r = requests.get(url, headers=headers, timeout=5)
                raw = r.text.strip().replace("suggest_callback(", "")[:-1]
                data = json.loads(raw)
                results = []
                docs = data.get("response", {}).get("docs", [])
                for item in docs:
                    item_type = item.get("t")
                    if item_type == "2":
                        title = item.get("m")
                        artist = item.get("a")
                        if title and artist:
                            results.append({"title": title, "artist": artist})
                            if len(results) >= 8:
                                break
                Clock.schedule_once(lambda dt: self.update_list(results), 0)

            except requests.Timeout:
                logging.error("Timeout while fetching suggestions")
                Clock.schedule_once(lambda dt: self.show_error("Connection timeout"), 0)

            except requests.RequestException as e:
                logging.error(f"Network error fetching suggestions: {e}")
                Clock.schedule_once(lambda dt: self.show_error("Network error"), 0)

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse suggestion JSON: {e}")
                Clock.schedule_once(lambda dt: self.show_error("Data parsing error"), 0)

    def update_list(self, data):
        self.root.get_screen("search").ids.rv.data = data

    def open_song(self, title, artist):
        threading.Thread(
            target=self.fetch_song, args=(title, artist), daemon=True
        ).start()

    def normalize(self, text):
        text = text.lower()
        text = re.sub(r"[áàãâä]", "a", text)
        text = re.sub(r"[éèêë]", "e", text)
        text = re.sub(r"[íìîï]", "i", text)
        text = re.sub(r"[óòõôö]", "o", text)
        text = re.sub(r"[úùûü]", "u", text)
        text = re.sub(r"ç", "c", text)
        text = re.sub(r"[^a-z0-9& ]", "", text)
        return text.strip()

    def fetch_song(self, title, artist):
        slug_title = re.sub(r"\s+", "-", self.normalize(title))
        artist_norm = self.normalize(artist)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        variants = []
        if "&" in artist_norm:
            parts = [p.strip() for p in artist_norm.split("&")]
            variants.append("-".join(parts).replace(" ", "-"))
            variants.append("-e-".join(parts).replace(" ", "-"))
        else:
            variants.append(artist_norm.replace(" ", "-"))

        base_variants = variants.copy()
        for v in base_variants:
            variant_no_a = re.sub(r"-a-", "-", v)
            if variant_no_a not in variants:
                variants.append(variant_no_a)

        title_variants = [slug_title]
        slug_title_no_a = re.sub(r"-a-", "-", slug_title)
        if slug_title_no_a != slug_title:
            title_variants.append(slug_title_no_a)

        success = False
        for variant in variants:
            variant = re.sub(r"-+", "-", variant)
            for title_slug in title_variants:
                title_slug = re.sub(r"-+", "-", title_slug)
                url = f"https://www.cifraclub.com.br/{variant}/{title_slug}/"
                try:
                    r = requests.get(url, headers=headers, timeout=10)
                    r.raise_for_status()  # Raises HTTPError for non-200 responses
                    soup = BeautifulSoup(r.text, "html.parser")
                    pre = soup.find("pre")
                    if pre:
                        song_text = self.parse_cifra_html(pre)
                        footer_info = self.parse_footer_info(soup)
                        if footer_info:
                            song_text += "\n\n" + footer_info
                        Clock.schedule_once(
                            lambda dt: self.show_song(title, song_text), 0
                        )
                        success = True
                        break
                except requests.Timeout:
                    logging.error(f"Timeout fetching song {title} by {artist}")
                    Clock.schedule_once(
                        lambda dt: self.show_song(title, "Connection timeout"), 0
                    )
                except requests.RequestException as e:
                    logging.error(f"Network error fetching song {title}: {e}")
                    Clock.schedule_once(
                        lambda dt: self.show_song(title, "Network error"), 0
                    )
                except Exception as e:
                    logging.error(f"Error parsing song {title}: {e}")
                    Clock.schedule_once(
                        lambda dt: self.show_song(title, "Failed to fetch song"), 0
                    )
            if success:
                break


        if not success:
            Clock.schedule_once(lambda dt: self.show_song(title, "Song not found."), 0)

    def parse_footer_info(self, soup):
        footer_parts = []

        footer_elem = soup.find("div", class_="cifra-footer")
        if footer_elem:
            composer_elem = footer_elem.find("p", class_="cifra-composer")
            if composer_elem:
                composer_text = ""
                for content in composer_elem.children:
                    if isinstance(content, str):
                        composer_text += content
                composer_text = composer_text.strip()
                if composer_text:
                    footer_parts.append(f"[color=B39DDB]{composer_text}[/color]")

            creditos_elem = footer_elem.find("div", class_="cifra-creditos")
            if creditos_elem:
                user_list = creditos_elem.find("ul", class_="user-list")
                if user_list:
                    users = []
                    for li in user_list.find_all("li", recursive=False):
                        link = li.find("a", class_="tooltip")
                        if link:
                            user_name = link.get("title") or link.get_text(strip=True)
                            if user_name and user_name != "+2":
                                users.append(user_name)
                    if users:
                        footer_parts.append(
                            f"[color=9E9E9E]Contributors: {', '.join(users)}[/color]"
                        )

        return "\n".join(footer_parts)

    def parse_cifra_html(self, pre_tag):
        content = str(pre_tag)
        content = re.sub(r"<b>(.*?)</b>", r"CH_START\1CH_END", content)
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text()
        text = text.replace("CH_START", "[b][color=B388FF]").replace(
            "CH_END", "[/color][/b]"
        )
        return text.strip()

    def create_label_chunk(self, text):
        from kivy.uix.label import Label

        label = Label(
            text=text,
            markup=True,
            font_name="RobotoMono-Regular.ttf",
            font_size=dp(9),
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            halign="left",
            valign="top",
        )
        label.texture_update()
        label.size = label.texture_size
        return label

    def show_song(self, title, text):
        screen = self.root.get_screen("lyrics")
        screen.song_title = title
        container = screen.ids.lyrics_container
        container.clear_widgets()
        lines = text.split("\n")
        max_width = 0
        for i in range(0, len(lines), CHUNK_SIZE):
            chunk = "\n".join(lines[i : i + CHUNK_SIZE])
            label = self.create_label_chunk(chunk)
            container.add_widget(label)
            if label.width > max_width:
                max_width = label.width
        container.width = max_width
        screen.ids.lyrics_card.width = max_width + dp(40)
        self.root.current = "lyrics"
        Clock.schedule_once(self.reset_view, 0.2)

    def reset_view(self, dt):
        scroll = self.root.get_screen("lyrics").ids.lyrics_scroll
        scroll.scroll_y = 1
        scroll.scroll_x = 0

    def back_to_search(self):
        self.root.current = "search"


if __name__ == "__main__":
    OpenCifraApp().run()
