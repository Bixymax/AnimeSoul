# AnimeSoul 🌸

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)](#)
[![SQLite3](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](#)
[![Jikan API](https://img.shields.io/badge/API-Jikan-orange.svg)](https://jikan.moe/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AnimeSoul is a modern **desktop application** built with Python and Tkinter that allows you to manage your personal anime library locally.

Inspired by MyAnimeList, it provides a clean interface, secure local data management, and automatic poster fetching via the Jikan API.

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Ideas & Feedback](#-ideas--feedback)
- [License](#-license)
- [Support](#-support)

---

## 📖 About the Project

AnimeSoul is a **local MyAnimeList-style manager** designed for personal use.

All anime data is stored locally using SQLite3, ensuring:
- 🔒 Privacy
- ⚡ Fast performance
- 💾 Full offline access

Internet access is only required for fetching anime posters through the Jikan API.

---

## ✨ Features

- ✅ **Full CRUD Management**: Add, edit, and delete anime from your collection.
- 🔎 **Smart Search**: Real-time filtering with text normalization (accent and case insensitive).
- 🖼️ **Automatic Poster Fetching**: Retrieves official posters via the Jikan API (MyAnimeList).
- 🎨 **Dark & Light Themes**: Customize the app's appearance to your liking.
- 📁 **CSV Export**: Easily backup or export your anime list.

---

## 📸 Screenshots

<img width="1400" height="1033" alt="AnimeSoul_Screenshot" src="https://github.com/user-attachments/assets/6dc32d08-6aee-4efd-9264-a110dae05ce4" />

---

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
git clone [https://github.com/Bixymax/AnimeSoul.git](https://github.com/Bixymax/AnimeSoul.git)
cd AnimeSoul
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
```

**Activate it:**

*Windows:*
```bash
venv\Scripts\activate
```

*macOS / Linux:*
```bash
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the application

```bash
python main.py
```

---

## 💡 Usage

1. Launch the application using the `python main.py` command.
2. Click on the **Add Anime** button to search for your first anime.
3. The app will automatically fetch the poster and details using the Jikan API.
4. Set your watch status, score, and episode progress.
5. Use the search bar to filter your library instantly!

---

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **GUI** | Tkinter (Custom styling + Pillow) |
| **Database** | SQLite3 |
| **Networking** | Requests |
| **External API**| Jikan (MyAnimeList unofficial API) |

---

## 📂 Project Structure

```text
AnimeSoul/
│
├── assets/             # Icons, images, and visual resources
├── core/               # Main application logic (e.g., database management)
├── ui/                 # Files related to the graphical interface (Tkinter)
├── utils/              # Utility functions
├── config.py           # Global application configuration
├── main.py             # Entry point to launch the application
├── requirements.txt    # Python dependencies
└── README.md
```

---

## 💬 Ideas & Feedback

I am always looking for ways to improve AnimeSoul! If you have any ideas for new features, interface improvements, or other implementations, I would love to hear them.

Feel free to share your thoughts by opening an [Issue](https://github.com/Bixymax/AnimeSoul/issues) and describing your idea. All feedback is highly appreciated!

---

## 📜 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute it.

---

## ⭐ Support

If you like this project, consider giving it a star ⭐️ on GitHub to support its development!
