🐝 QuizBee – AI-Powered Quiz Generator
QuizBee is an interactive AI-powered quiz generator designed to create engaging quizzes for children and learners. It allows users to generate quizzes on any Topic using Generative AI, making learning fun, personalized, and efficient.
________________________________________
🚀 Features
•	📘 Generate quizzes on any Topic
•	🤖 AI-based question generation using LLMs
•	🧠 Supports multiple difficulty levels
•	📝 Generates multiple question sets
•	👶 Kid-friendly and interactive UI
•	🌐 Web-based interface (Streamlit)
•	📄 Option to export quizzes as PDF
•	⚡ Fast and easy to use
________________________________________
🛠️ Tech Stack
•	Python
•	Streamlit  (Frontend)
•	Generative AI (LLMs)
•	LangChain / Prompt Engineering
•	ReportLab (PDF generation)
•	Docker (Optional – for deployment)
________________________________________
📂 Project Structure
QuizBee/
│
├── app.py # Main application file
├── quiz_gen.py # Core quiz generation logic
├── prompts/ # Prompt templates
├── utils/ # Helper functions
├── requirements.txt # Python dependencies
├── Dockerfile # Docker configuration
├── .env # Environment variables
└── README.md # Project documentation
________________________________________
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/sumakumar27-ux/Quizzbee.git
cd quizzbee
2️⃣ Create Virtual Environment
python -m venv env
env\Scripts\activate # Windows
source env/bin/activate # macOS/Linux
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Set Environment Variables
Create a .env file:
API_KEY=your_api_key_here
________________________________________
▶️ Running the App
streamlit run app.py

