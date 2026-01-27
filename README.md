# OpenCifra

OpenCifra is a free and open-source Python application built with **Kivy** and **KivyMD** that serves as a songbook and lyrics viewer.
It allows users to search for songs and artists, view lyrics with chord notation, and is designed to be mobile-friendly (desktop and Android).

This repository contains only the source code of the application.


## Features

* Search songs and artists from public online sources
* Display lyrics with chord notation
* Responsive interface using **Kivy / KivyMD**
* Works on desktop and can be packaged for Android
* Fully free, open-source, and non-commercial


## Requirements

* Python 3.x
* Kivy
* KivyMD
* Requests
* BeautifulSoup4
* Pyjnius

Other dependencies (openssl, certifi, etc.) are automatically handled during the Android build process.


## Installation (Desktop)

Clone the repository:

```bash
git clone https://github.com/KaykCaputo/OpenCifra.git
cd OpenCifra
```

Set up a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

Install dependencies:

```bash
pip install kivy kivymd requests beautifulsoup4 pyjnius
```

Run the application:

```bash
python main.py
```


## Installation (Android)

Download the latest pre-built APK from the GitHub **Releases** page.
Install it on your device (you may need to enable "Install from Unknown Sources").

### Building from Source

This project uses **Buildozer**:

1. Install Buildozer following the official guide.
2. Build the APK:

```bash
buildozer android debug
```

3. Transfer the `.apk` file from the `bin/` folder to your device and install it.


## File Structure

* `main.py`: Main application entry point containing UI logic and API handling
* `guitar.json`: Database of guitar chords and finger positions
* `buildozer.spec`: Buildozer configuration file for Android packaging


## Legal Notice

OpenCifra does **not store, host, or redistribute** any copyrighted lyrics, or musical content.

All lyrics and chords displayed are:

* Retrieved in real time from public web sources
* Displayed temporarily at the user’s request
* Owned by their respective authors and copyright holders

OpenCifra functions as a client-side viewer, similar to a web browser, and **does not maintain its own database of musical works**.

If you are a copyright holder and believe that content accessed through this application infringes your rights, please open an issue in this repository.


## Privacy

OpenCifra does **not**:

* Collect personal data
* Track users
* Use analytics
* Store song content on servers

All processing happens locally on the user’s device.


## Educational Purpose

OpenCifra is intended for:

* Music students
* Practice and study
* Educational and non-commercial use

The project aims to democratize access to music learning tools through free and open-source software.


## Contributions

Contributions are welcome:

* Open issues
* Submit pull requests
* Improve documentation
* Suggest architectural or legal improvements

Please ensure contributions respect open-source principles and copyright.


## License

This project is licensed under the **MIT License**.

You are free to:

* Use
* Modify
* Distribute
* Fork

As long as the original copyright notice and license text are included. See the LICENSE file for details.


## Optional Donations

Donations, if any, are voluntary and intended solely to support the development of the open-source software.
They do not provide access to any musical content or additional features.


## Disclaimer

This project is provided “as is,” without warranty of any kind.
The authors are not responsible for the use of third-party content accessed by users through the application.
