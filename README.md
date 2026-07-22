# 🏛️ Architectural Land Measurement & Value Predictor

An interactive Streamlit web dashboard for real-time architectural land assessment and predictions, featuring an immersive glassmorphism design and custom video backdrop.

---

## 🌟 Key Features

* **Real-Time Prediction Engine:** Input land parameters and survey numbers to calculate architectural assessments instantly.
* **Continuous Background Video:** Ultra-smooth 60fps slow-motion background video embedded via Base64 caching for uninterrupted session playback.
* **Glassmorphism UI:** Translucent dark-mode dashboard cards built with custom CSS, optimized for high contrast and readability over motion graphics.
* **Optimized Performance:** Utilizes `@st.cache_data` and GPU hardware acceleration for low latency and zero flickering during script reruns.

---

## 🛠️ Tech Stack

* **Frontend / Framework:** [Streamlit](https://streamlit.io/) (Python)
* **Custom Styling:** HTML5, CSS3 (Glassmorphism, Backdrop Filters, CSS Animations)
* **Machine Learning / Data Processing:** Python, Pandas, NumPy, Scikit-Learn
* **Deployment:** Streamlit Community Cloud

---

## 📂 Project Structure

```text
architectural-land-app/
├── static/
│   └── bg_video.mp4        # Background slow-motion video asset
├── .streamlit/
│   └── config.toml          # Custom theme configuration
├── streamlit_app.py        # Main Streamlit application code
├── style.css               # Custom CSS for layering & animation
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation