# 🌐 Focusmate Connections Globe

Ever wondered where in the world your Focusmate partners are? 
This project transforms your session history into a stunning, interactive 3D globe, 
visualizing the real-time locations of every partner you've worked with over the last year.

*This tool is fully private, running entirely in your browser. Your data is yours alone.*

-----

### ✨ Features

  * **Interactive 3D Globe:** A beautifully rendered, rotatable, and zoomable globe.
  * **Live Timezones:** Location markers pulse and change color to reflect the current time of day for your partners.
  * **Personalized Data:** See a list of your partners' first names for each location by tapping (on mobile) or hovering (on desktop).
  * **100% Private & Secure:** Your API key and session data are used locally on your computer to generate a data file.
    They are never stored, shared, or uploaded anywhere.
  * **Static & Serverless:** No backend, no database. The entire experience runs in your browser, making it fast, secure, and easy to host.

-----

## 🚀 How to Generate Your Globe

Follow these simple steps to create your personalized connections globe.

### Step 1: Prerequisites

First, make sure you have Python (>=3.10) installed. Then, open your terminal or command prompt and install the required libraries with this command:

```bash
pip install requests geopy python-dotenv
```

### Step 2: Clone the Repo/Clean jsons

Clone this repository to your computer.
Empty location.json and processed_users.json. 

### Step 3: Run the Script & Get Your Data

1.  The script needs your **Focusmate API Key**. Use an env variable, please.

    > You can get your key by visiting your [Focusmate API Key Page](https://app.focusmate.com/settings?type=account).

2.  Navigate to the repo location in your terminal and run it:

    ```bash
    python actions.py
    ```

3.  The script will securely connect to Focusmate, fetch your session history, and generate your location data. Once it's done, it will print a large block of text.

### Step 4: Create Your Globe\!

1.  Open the `index.html` file (or visit the live website)

-----

### 💻 Technology Stack

  * **Frontend:** HTML, CSS, JavaScript
  * **3D Rendering:** [Three.js](https://threejs.org/)
  * **Data Scripting:** Python
  * **Geocoding:** [Geopy](https://geopy.readthedocs.io/en/stable/)

-----

### 🤝 Contributing & Feedback

This is a personal project, but if you have ideas for improvement or run into any issues, feel free to open an issue in this repository\!
