# CrewAI Crew Builder
[![CrewAI Builder Demo](https://img.youtube.com/vi/esawlDqXCls/0.jpg)](https://youtu.be/esawlDqXCls)

CrewAI Crew Builder is a Streamlit-based web application that allows users to create, configure, and run AI crews using the CrewAI framework. This tool provides an intuitive interface for defining agents, tasks, and executing AI-powered workflows.

## Features

- Create and configure AI agents with specific roles, goals, and backstories
- Define tasks for your AI crew to accomplish
- Run AI crews and view results in real-time
- Save and view past crew execution results
- Export crew configurations for later use

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/crewai-crew-builder.git
   cd crewai-crew-builder
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   SERPER_API_KEY=your_serper_api_key
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Use the interface to:
   - Add agents and define their roles, goals, and backstories
   - Create tasks for your AI crew
   - Run the crew and view the results
   - Save and view past execution results
   - Export your crew configuration

## Contributing

Contributions to the CrewAI Crew Builder are welcome! Please feel free to submit pull requests, create issues, or suggest new features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project uses the [CrewAI](https://github.com/joaomdmoura/crewAI) framework
- Built with [Streamlit](https://streamlit.io/)
- Special thanks to the open-source community for their invaluable contributions

