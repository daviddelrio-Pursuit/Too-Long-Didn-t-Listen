Here is the updated `README.md` content, clearly outlining that the app now uses **URL retrieval** instead of file uploads to process audio content.

-----

## 📄 Final `README.md` Content (Updated for URL Input)

```markdown
# 🎙️ TLDL (Too Long Didn't Listen) Podcast Summarizer

## 🚀 Project Overview: Solving Time-Debt

TLDL is a Minimum Viable Product (MVP) web application designed to solve the critical problem of **time-consuming audio consumption** and **information overload**. It automates the process of transcribing and summarizing long-form audio content to facilitate **immediate knowledge gain**.

---

## 🎯 The Problem & The Informed Professional

The core issue is **efficiency**. Our users are facing **time-debt** when trying to process valuable, long-form content.

* **The Problem:** Professionals lose hours manually sifting through audio or long transcripts. They need $\mathbf{90}$ minutes of information delivered in $\mathbf{2}$ minutes.
* **Target User:** The **Informed Professional** (e.g., consultant, researcher). This persona values **efficiency** and demands a **concise, executive-style summary** to inform quick decisions.

---

## 🛠️ Technical Progress (MVP)

The application foundation is complete, live, and ready for API integration, based on a URL-first workflow:

* **Web Framework:** Streamlit (Python) for a simple, single-page UI.
* **Deployment:** The application is live and hosted on **Streamlit Community Cloud**, linked to this GitHub repository for Continuous Deployment (CD).
* **Core Feature (UX):** The app accepts a **public URL** (e.g., YouTube, podcast link) as input, providing a smoother, URL-based user experience for content retrieval.
* **Audio Output:** The MVP integrates a **Text-to-Speech (TTS)** component to allow the user to listen to the final summary.

---

## 🔮 Next Steps

The final phase will focus on integrating the robust, three-step audio processing backbone:

1.  **URL Fetching:** The system will fetch and prepare the audio file from the provided URL.
2.  **Transcription & Summarization:** Integration of the **OpenAI API**. We will use the **Whisper API** for high-accuracy audio transcription and the **GPT API** to generate the final, high-quality, executive summary.
3.  **TTS Generation:** Convert the summary text back into a listenable audio file using the OpenAI TTS API.
```
