import streamlit as st
import os
import json
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from datetime import datetime
from groq import Groq
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up environment variables
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize tools with error handling
try:
    search_tool = SerperDevTool()
except Exception as e:
    st.error(f"Error initializing SerperDevTool: {str(e)}")
    search_tool = None

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def perform_groq_chat_completion(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error performing Groq chat completion: {str(e)}")
        return None

# Database setup
def init_db():
    conn = sqlite3.connect('crewai_results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  crew_name TEXT,
                  result TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_result(crew_name, result):
    conn = sqlite3.connect('crewai_results.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO results (crew_name, result, timestamp) VALUES (?, ?, ?)",
              (crew_name, result, timestamp))
    conn.commit()
    conn.close()

def get_results():
    conn = sqlite3.connect('crewai_results.db')
    c = conn.cursor()
    c.execute("SELECT * FROM results ORDER BY timestamp DESC")
    results = c.fetchall()
    conn.close()
    return results

# AI-assisted agent creation
def ai_create_agent(description):
    prompt = f"Parse the following agent description into a role, goal, and backstory. Respond in the format 'Role: [role]\nGoal: [goal]\nBackstory: [backstory]':\n\n{description}"
    response = perform_groq_chat_completion(prompt)
    if not response:
        return None
    
    # Initialize default values
    agent_info = {
        "role": "Undefined Role",
        "goal": "Undefined Goal",
        "backstory": "Undefined Backstory"
    }
    
    # Parse the response
    for line in response.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key == 'role':
                agent_info['role'] = value
            elif key == 'goal':
                agent_info['goal'] = value
            elif key == 'backstory':
                agent_info['backstory'] = value
    
    return agent_info

# AI-generated task
def ai_create_task(description):
    prompt = f"Generate a formal task description and expected output based on this natural language description. Respond in the format 'Description: [description]\nExpected Output: [expected output]':\n\n{description}"
    response = perform_groq_chat_completion(prompt)
    st.write("Debug - AI Response:", response)  # Debug line
    if not response:
        return None
    
    # Initialize default values
    task_info = {
        "description": "Undefined Description",
        "expected_output": "Undefined Expected Output"
    }
    
    # Parse the response
    for line in response.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key == 'description':
                task_info['description'] = value
            elif key == 'expected output':
                task_info['expected_output'] = value
    
    st.write("Debug - Parsed Task Info:", task_info)  # Debug line
    return task_info

# Streamlit app
st.set_page_config(page_title="CrewAI Crew Builder", layout="wide")

# Custom CSS for improved styling and readability
st.markdown("""
    <style>
    .stApp {
        background-color: #2E3440;
        color: #D8DEE9;
    }
    .stButton>button {
        background-color: #5E81AC;
        color: #ECEFF4;
    }
    .stTextInput>div>div>input {
        background-color: #3B4252;
        color: #E5E9F0;
    }
    .stTextArea>div>div>textarea {
        background-color: #3B4252;
        color: #E5E9F0;
    }
    .stExpander {
        background-color: #434C5E;
    }
    .stExpander > div > div > div > div > div > p {
        color: #E5E9F0;
    }
    h1, h2, h3 {
        color: #88C0D0;
    }
    .stSidebar {
        background-color: #3B4252;
    }
    .stSidebar [data-testid="stSidebarNav"] {
        background-color: #2E3440;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Enhanced CrewAI Crew Builder")

# Initialize session state
if 'agents' not in st.session_state:
    st.session_state.agents = []
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'crew_name' not in st.session_state:
    st.session_state.crew_name = ""
if 'result' not in st.session_state:
    st.session_state.result = None

# Sidebar for adding agents and tasks
st.sidebar.header("Crew Configuration")
st.session_state.crew_name = st.sidebar.text_input("Crew Name", st.session_state.crew_name)

# AI-generated agent
with st.sidebar.expander("Add Agent (AI-Assisted)"):
    agent_description = st.text_area("Describe your agent")
    if st.button("Generate Agent"):
        if agent_description:
            agent_info = ai_create_agent(agent_description)
            if agent_info:
                st.session_state.agents.append(agent_info)
                st.success("Agent added successfully!")
            else:
                st.error("Failed to generate agent. Please try again.")
        else:
            st.error("Please provide a description for the agent.")

# AI-generated task
with st.sidebar.expander("Add Task (AI-Generated)"):
    task_description = st.text_area("Describe your task")
    if st.button("Generate Task"):
        if task_description:
            task_info = ai_create_task(task_description)
            if task_info:
                st.session_state.tasks.append(task_info)
                st.success("Task added successfully!")
                st.write("Debug - Tasks after adding:", st.session_state.tasks)  # Debug line
                st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
            else:
                st.error("Failed to generate task. Please try again.")
        else:
            st.error("Please provide a description for the task.")

# Template Library
with st.sidebar.expander("Template Library"):
    template_type = st.selectbox("Select template type", ["Agent", "Task"])
    if template_type == "Agent":
        agent_templates = {
            "Researcher": {"role": "Researcher", "goal": "Gather and analyze information", "backstory": "Experienced academic with a passion for discovery"},
            "Writer": {"role": "Writer", "goal": "Create engaging content", "backstory": "Published author with a flair for storytelling"},
            "Data Analyst": {"role": "Data Analyst", "goal": "Extract insights from data", "backstory": "Statistical expert with a keen eye for patterns"},
        }
        selected_template = st.selectbox("Select an agent template", list(agent_templates.keys()))
        if st.button("Use Template"):
            st.session_state.agents.append(agent_templates[selected_template])
            st.success(f"{selected_template} template added!")
    else:
        task_templates = {
            "Market Research": {"description": "Conduct market research on a specific product", "expected_output": "Comprehensive market analysis report"},
            "Content Creation": {"description": "Write a blog post on a given topic", "expected_output": "1500-word SEO-optimized blog post"},
            "Data Analysis": {"description": "Analyze sales data for the past quarter", "expected_output": "Executive summary with key insights and visualizations"},
        }
        selected_template = st.selectbox("Select a task template", list(task_templates.keys()))
        if st.button("Use Template"):
            st.session_state.tasks.append(task_templates[selected_template])
            st.success(f"{selected_template} template added!")

# Main content area
col1, col2 = st.columns(2)

# Display and edit agents
with col1:
    st.header("Agents")
    for i, agent in enumerate(st.session_state.agents):
        with st.expander(f"Agent {i+1}: {agent['role']}"):
            agent['role'] = st.text_input("Role", agent['role'], key=f"agent_role_{i}")
            agent['goal'] = st.text_area("Goal", agent['goal'], key=f"agent_goal_{i}")
            agent['backstory'] = st.text_area("Backstory", agent['backstory'], key=f"agent_backstory_{i}")
            if st.button(f"Remove Agent {i+1}"):
                st.session_state.agents.pop(i)
                st.experimental_rerun()

# Display and edit tasks
with col2:
    st.header("Tasks")
    if not st.session_state.tasks:
        st.write("No tasks added yet.")
    for i, task in enumerate(st.session_state.tasks):
        with st.expander(f"Task {i+1}"):
            task['description'] = st.text_area("Description", task['description'], key=f"task_desc_{i}")
            task['expected_output'] = st.text_area("Expected Output", task['expected_output'], key=f"task_output_{i}")
            if st.button(f"Remove Task {i+1}"):
                st.session_state.tasks.pop(i)
                st.rerun()  # Use st.rerun() here as well

# Visualization of crew structure
if st.session_state.agents and st.session_state.tasks:
    st.header("Crew Structure Visualization")
    crew_structure = {
        "name": st.session_state.crew_name,
        "children": [
            {"name": "Agents", "children": [{"name": agent["role"]} for agent in st.session_state.agents]},
            {"name": "Tasks", "children": [{"name": task["description"][:30] + "..."} for task in st.session_state.tasks]}
        ]
    }
    st.json(crew_structure)  # This is a simple JSON representation; you could use a proper visualization library for a more interactive display

# Run the crew
if st.button("Run Crew"):
    if st.session_state.crew_name and len(st.session_state.agents) > 0 and len(st.session_state.tasks) > 0:
        if search_tool is None:
            st.error("SerperDevTool is not initialized. Please check your API keys and try again.")
        else:
            # Create Agent and Task objects
            agents = [Agent(
                role=a['role'],
                goal=a['goal'],
                backstory=a['backstory'],
                verbose=True,
                allow_delegation=True,
                tools=[search_tool]
            ) for a in st.session_state.agents]

            tasks = [Task(
                description=t['description'],
                agent=agents[i % len(agents)],
                expected_output=t['expected_output']
            ) for i, t in enumerate(st.session_state.tasks)]

            # Create and run the crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
                max_delegation_depth=2
            )

            with st.spinner("Running crew..."):
                try:
                    st.session_state.result = crew.kickoff()
                    st.success("Crew execution completed successfully!")
                    st.write(st.session_state.result)
                    
                    # Save result to database
                    init_db()
                    save_result(st.session_state.crew_name, str(st.session_state.result))
                except Exception as e:
                    st.error(f"An error occurred during crew execution: {str(e)}")
    else:
        st.error("Please provide a crew name and add at least one agent and one task before running the crew.")

# View saved results
if st.button("View Saved Results"):
    results = get_results()
    for result in results:
        with st.expander(f"Crew: {result[1]} - {result[3]}"):
            st.write(result[2])

# Export configuration
if st.sidebar.button("Export Configuration"):
    config_data = {
        "crew_name": st.session_state.crew_name,
        "agents": st.session_state.agents,
        "tasks": st.session_state.tasks
    }
    st.sidebar.download_button(
        label="Download Configuration",
        data=json.dumps(config_data, indent=2),
        file_name=f"{st.session_state.crew_name}_config.json",
        mime="application/json"
    )

# AI Suggestions
if st.button("Get AI Suggestions"):
    crew_info = json.dumps({"agents": st.session_state.agents, "tasks": st.session_state.tasks})
    prompt = f"Analyze this crew configuration and provide suggestions for improvement:\n\n{crew_info}"
    suggestions = perform_groq_chat_completion(prompt)
    st.write("AI Suggestions:", suggestions)

# Initialize the database
init_db()