import streamlit as st
import pandas as pd
import os
from pathlib import Path
import time
import logging
from datetime import datetime
from openai import OpenAI
# Removed .env file dependency - using only system environment variables and Streamlit secrets

# Configure the page
st.set_page_config(
    page_title="Restaurant Operations Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("Restaurant Operations Dashboard")
st.markdown("### Comprehensive view of restaurant data across all operational modules")

# Database path
DATABASE_PATH = Path("database")

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_filename = f"restaurant_app_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = log_dir / log_filename
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()

# Define the CSV files and their display names
CSV_FILES = {
    "Menu": "menu.csv",
    "Inventory": "inventory.csv", 
    "POS Sales": "pos_sales.csv",
    "Reservations": "reservations.csv",
    "Reviews": "reviews.csv",
    "HR & Staff": "hr_staff.csv",
    "Vendor & Supply": "vendor_supply.csv",
    "CRM & Loyalty": "crm_loyalty.csv",
    "Finance & Accounting": "finance_accounting.csv",
    "Marketing & Promotions": "marketing_promotions.csv"
}

def load_csv_data(file_path):
    """Load CSV data with error handling"""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return None

def format_currency_columns(df, currency_columns):
    """Format currency columns for better display"""
    df_formatted = df.copy()
    for col in currency_columns:
        if col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) and isinstance(x, (int, float)) else x)
    return df_formatted

def upload_files_to_openai():
    """Upload CSV files to OpenAI and create assistant with code interpreter"""
    logger.info("Starting upload_files_to_openai function")
    
    try:
        # Get API key from environment or Streamlit secrets
        logger.info("Checking for OpenAI API key")
        
        # Check API key sources
        logger.info("Checking API key sources (environment variables and Streamlit secrets)")
        
        api_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"Environment variable OPENAI_API_KEY: {'Found' if api_key else 'Not found'}")
        
        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY")
                logger.info("API key found in Streamlit secrets")
            except Exception as secrets_error:
                logger.error(f"Error accessing Streamlit secrets: {secrets_error}")
        else:
            logger.info("API key found in environment variables")
            
        if not api_key:
            error_msg = "OpenAI API key not found. Please add it to your .env file or Streamlit secrets."
            logger.error(error_msg)
            st.error(error_msg)
            return None, []
        
        logger.info("Initializing OpenAI client")
        client = OpenAI(api_key=api_key)
        
        file_ids = []
        csv_files = [
            "menu.csv", "inventory.csv", "pos_sales.csv", "reservations.csv", 
            "reviews.csv", "hr_staff.csv", "vendor_supply.csv", 
            "crm_loyalty.csv", "finance_accounting.csv", "marketing_promotions.csv"
        ]
        
        logger.info(f"Found {len(csv_files)} CSV files to upload")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Check if database directory exists
        if not DATABASE_PATH.exists():
            error_msg = f"Database directory not found: {DATABASE_PATH}"
            logger.error(error_msg)
            st.error(error_msg)
            return None, []
        
        # Upload files
        for i, filename in enumerate(csv_files):
            filepath = DATABASE_PATH / filename
            logger.info(f"Processing file {i+1}/{len(csv_files)}: {filename}")
            
            if filepath.exists():
                status_text.text(f"Uploading {filename}...")
                logger.info(f"Uploading {filename} (size: {filepath.stat().st_size} bytes)")
                
                try:
                    with open(filepath, "rb") as file:
                        uploaded_file = client.files.create(
                            file=file,
                            purpose="assistants"
                        )
                        file_ids.append(uploaded_file.id)
                        logger.info(f"Successfully uploaded {filename} with ID: {uploaded_file.id}")
                
                except Exception as upload_error:
                    logger.error(f"Error uploading {filename}: {upload_error}")
                    st.error(f"Error uploading {filename}: {upload_error}")
                    continue
                
                progress_bar.progress((i + 1) / len(csv_files))
            else:
                logger.warning(f"File not found: {filepath}")
                st.warning(f"File not found: {filename}")
        
        if not file_ids:
            error_msg = "No files were successfully uploaded"
            logger.error(error_msg)
            st.error(error_msg)
            return None, []
        
        # Create assistant with code interpreter
        status_text.text("Creating AI assistant with code interpreter...")
        logger.info(f"Creating assistant with {len(file_ids)} files")
        
        try:
            # Create assistant with the current OpenAI API v1.0+ format
            logger.info("Attempting to create assistant with current API format...")
            assistant = client.beta.assistants.create(
                name="Restaurant Operations Data Analyst",
                instructions="You are an expert restaurant operations data analyst. Analyze restaurant data including menu, inventory, sales, reservations, reviews, staff, vendors, CRM, finance, and marketing data to provide comprehensive insights and recommendations.",
                model="gpt-4-turbo-preview",
                tools=[{"type": "code_interpreter"}]
            )
            logger.info(f"Successfully created assistant with ID: {assistant.id}")
            
            # Now attach files to the assistant using the tool_resources approach
            logger.info("Attaching files to assistant using tool_resources...")
            try:
                # Update assistant with file resources
                client.beta.assistants.update(
                    assistant_id=assistant.id,
                    tool_resources={
                        "code_interpreter": {
                            "file_ids": file_ids
                        }
                    }
                )
                logger.info(f"Successfully attached {len(file_ids)} files to assistant")
                
            except Exception as update_error:
                logger.warning(f"Could not attach files via tool_resources: {update_error}")
                
                # Try the older file attachment method as fallback
                logger.info("Trying individual file attachment method...")
                for i, file_id in enumerate(file_ids):
                    try:
                        client.beta.assistants.files.create(
                            assistant_id=assistant.id,
                            file_id=file_id
                        )
                        logger.info(f"Attached file {i+1}/{len(file_ids)}: {file_id}")
                    except Exception as file_attach_error:
                        logger.warning(f"Could not attach file {file_id}: {file_attach_error}")
            
        except Exception as assistant_error:
            logger.error(f"Error creating assistant: {assistant_error}")
            st.error(f"Error creating assistant: {assistant_error}")
            return None, file_ids
        
        status_text.text("Setup complete!")
        progress_bar.progress(1.0)
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()
        
        logger.info("upload_files_to_openai completed successfully")
        return assistant, file_ids
        
    except Exception as e:
        error_msg = f"Error setting up OpenAI: {str(e)}"
        logger.error(error_msg, exc_info=True)
        st.error(error_msg)
        return None, []

def start_session():
    """Start Session function - Upload files to OpenAI and create assistant"""
    logger.info("Starting session")
    
    try:
        logger.info("Calling upload_files_to_openai")
        assistant, file_ids = upload_files_to_openai()
        
        if assistant and file_ids:
            logger.info(f"Session setup successful - Assistant ID: {assistant.id}, Files: {len(file_ids)}")
            st.session_state.assistant = assistant
            st.session_state.file_ids = file_ids
            st.session_state.session_active = True
            success_msg = f"Session started successfully! Created AI assistant with {len(file_ids)} files for code interpreter analysis."
            logger.info(success_msg)
            return success_msg
        else:
            error_msg = "Session started but failed to create assistant or upload files."
            logger.error(f"Session setup failed - Assistant: {assistant}, File IDs: {file_ids}")
            return error_msg
            
    except Exception as e:
        error_msg = f"Error starting session: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

def analyze_with_assistant(user_query):
    """Analyze user query with OpenAI assistant using streaming"""
    logger.info(f"Starting analysis with query: {user_query[:100]}...")
    
    if "assistant" not in st.session_state:
        st.error("No assistant available. Please start a session first.")
        return
    
    try:
        # Get API key and create client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY")
            except:
                pass
        
        if not api_key:
            st.error("OpenAI API key not found.")
            return
            
        client = OpenAI(api_key=api_key)
        assistant = st.session_state.assistant
        
        logger.info(f"Creating thread for assistant {assistant.id}")
        
        # Create a thread
        thread = client.beta.threads.create()
        logger.info(f"Created thread with ID: {thread.id}")
        
        # Add user message to thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_query
        )
        logger.info("Added user message to thread")
        
        # Create and stream the run
        st.subheader("🤖 AI Analysis Results")
        
        # Create a placeholder for streaming content
        response_placeholder = st.empty()
        response_text = ""
        
        logger.info("Starting streaming run...")
        
        with st.spinner("AI is analyzing your restaurant data..."):
            try:
                # Create run with streaming - using the correct API format
                stream = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant.id,
                    instructions="Analyze the restaurant data thoroughly. Use the uploaded CSV files to provide specific insights with numbers, trends, and actionable recommendations. Create visualizations when helpful.",
                    stream=True
                )
                
                # Handle streaming response
                for event in stream:
                    logger.debug(f"Stream event type: {type(event)}")
                    
                    # Handle text delta events
                    if hasattr(event, 'event') and event.event == 'thread.message.delta':
                        if hasattr(event, 'data') and hasattr(event.data, 'delta'):
                            if hasattr(event.data.delta, 'content'):
                                for content in event.data.delta.content:
                                    if hasattr(content, 'text') and hasattr(content.text, 'value'):
                                        response_text += content.text.value
                                        response_placeholder.markdown(response_text + "▌")
                    
                    # Handle completion events
                    elif hasattr(event, 'event'):
                        if event.event == 'thread.message.completed':
                            logger.info("Message completed")
                        elif event.event == 'thread.run.completed':
                            logger.info("Run completed successfully")
                            break
                        elif event.event == 'thread.run.failed':
                            logger.error(f"Run failed: {event.data if hasattr(event, 'data') else 'Unknown error'}")
                            st.error("Analysis failed. Please try again.")
                            return
                        elif event.event == 'thread.run.requires_action':
                            logger.info("Run requires action - handling tool calls")
                            # Handle tool calls if needed
                            pass
                
            except Exception as stream_error:
                logger.error(f"Streaming error: {stream_error}")
                logger.info("Falling back to non-streaming approach...")
                
                # Fallback to non-streaming approach
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant.id,
                    instructions="Analyze the restaurant data thoroughly. Use the uploaded CSV files to provide specific insights with numbers, trends, and actionable recommendations. Create visualizations when helpful."
                )
                
                # Wait for completion
                while run.status in ['queued', 'in_progress']:
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    logger.debug(f"Run status: {run.status}")
                
                if run.status == 'completed':
                    # Get the assistant's response
                    messages = client.beta.threads.messages.list(thread_id=thread.id)
                    
                    for message in messages.data:
                        if message.role == 'assistant':
                            for content in message.content:
                                if hasattr(content, 'text'):
                                    response_text = content.text.value
                                    response_placeholder.markdown(response_text)
                            break
                else:
                    logger.error(f"Run failed with status: {run.status}")
                    st.error(f"Analysis failed with status: {run.status}")
                    return
        
        # Final response without cursor
        response_placeholder.markdown(response_text)
        
        # Show analysis metadata
        with st.expander("Analysis Details"):
            st.write(f"**Query:** {user_query}")
            st.write(f"**Thread ID:** {thread.id}")
            st.write(f"**Assistant ID:** {assistant.id}")
            st.write(f"**Response Length:** {len(response_text)} characters")
            
        logger.info("Analysis completed successfully")
        
    except Exception as e:
        error_msg = f"Error during analysis: {str(e)}"
        logger.error(error_msg, exc_info=True)
        st.error(error_msg)
        
        # Show detailed error in expander for debugging
        with st.expander("Error Details"):
            st.code(str(e))

def show_home_page():
    """Display the home page"""
    st.title("Restaurant Operations Analysis System")
    st.markdown("---")
    st.write("Welcome to your comprehensive restaurant operations analysis system with AI-powered insights.")
    
    # Session Management
    st.subheader("Session Management")
    
    # Initialize session state
    if "session_active" not in st.session_state:
        st.session_state.session_active = False
    
    # Check for API key from system environment or Streamlit secrets
    api_key = os.getenv("OPENAI_API_KEY")
    streamlit_api_key = None
    
    # Try to get from Streamlit secrets
    try:
        streamlit_api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass
    
    if not api_key and not streamlit_api_key:
        st.warning("⚠️ OpenAI API key not configured!")
        st.info("""
        **Setup Options:**
        
        **Option 1 - System Environment Variable:**
        Set OPENAI_API_KEY in your system environment variables
        
        **Option 2 - Streamlit Secrets (Recommended for Cloud):**
        Add to your app's secrets in Streamlit Cloud dashboard:
        ```toml
        OPENAI_API_KEY = "your_openai_api_key_here"
        ```
        
        **Get your API key from:** https://platform.openai.com/api-keys
        """)
    elif streamlit_api_key:
        st.success("✅  Trex configured via Streamlit Secrets")
    elif api_key:
        st.success("✅ Trex configured via system environment variable")
    
    # Start Session button
    if not st.session_state.session_active:
        if st.button("Start Session", type="primary"):
            logger.info("Start Session button clicked")
            with st.spinner("Setting up AI assistant and uploading restaurant data..."):
                result = start_session()
            
            if "successfully" in result:
                st.success(result)
            else:
                st.error(result)
            
            # Show log file location
            log_dir = Path("logs")
            if log_dir.exists():
                log_files = list(log_dir.glob("restaurant_app_*.log"))
                if log_files:
                    latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                    st.info(f"Check logs for details: {latest_log}")
            
            st.rerun()
    else:
        st.success("Session is active - AI assistant ready with restaurant data")
        if st.button("End Session"):
            logger.info("End Session button clicked")
            st.session_state.session_active = False
            if "assistant" in st.session_state:
                del st.session_state.assistant
            if "file_ids" in st.session_state:
                del st.session_state.file_ids
            st.rerun()
    
    # Analysis tool (only show if session is active)
    if st.session_state.session_active:
        st.markdown("---")
        st.subheader("AI Analysis Tool")
        
        # Initialize conversation history
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
        
        # Show example questions
        st.write("**Example Questions:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🍔 Top-selling menu items?", key="example1"):
                st.session_state.current_query = "What are the top-selling menu items based on the POS sales data?"
            if st.button("💰 Food cost percentage?", key="example2"):
                st.session_state.current_query = "What's our food cost percentage and how can we optimize it?"
        
        with col2:
            if st.button("⭐ Customer satisfaction analysis?", key="example3"):
                st.session_state.current_query = "Analyze customer satisfaction from the reviews data and identify areas for improvement"
            if st.button("👥 Top performing servers?", key="example4"):
                st.session_state.current_query = "Which servers generate the most tips and have the best performance?"
        
        # Query input
        query_input = st.text_area(
            "Enter your analysis request:", 
            value=st.session_state.get("current_query", ""),
            placeholder="Ask about menu performance, customer reviews, financial metrics, staff performance, inventory usage, etc.",
            key="analysis_input"
        )
        
        # Clear the current query after it's been set
        if "current_query" in st.session_state:
            del st.session_state.current_query
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔍 Analyze", type="primary"):
                if query_input.strip():
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        "query": query_input,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    analyze_with_assistant(query_input)
                else:
                    st.warning("Please enter an analysis request.")
        
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.conversation_history = []
                st.rerun()
        
        # Show conversation history
        if st.session_state.conversation_history:
            st.markdown("---")
            st.subheader("Recent Queries")
            for i, item in enumerate(reversed(st.session_state.conversation_history[-5:])):  # Show last 5
                with st.expander(f"[{item['timestamp']}] {item['query'][:60]}..."):
                    st.write(item['query'])
                    if st.button(f"Ask Again", key=f"reask_{i}"):
                        st.session_state.current_query = item['query']
                        st.rerun()
    else:
        st.warning("Please start a session to use the AI analysis tool.")
        st.text_area(
            "Enter your analysis request:", 
            placeholder="Start a session first to analyze your restaurant data...", 
            disabled=True
        )
        st.button("Analyze", disabled=True)
    
    # Debug section
    st.markdown("---")
    st.subheader("Debug Information")
    
    # Show current session state
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Session Status:**")
        st.write(f"Active: {st.session_state.get('session_active', False)}")
        st.write(f"Assistant: {'Yes' if 'assistant' in st.session_state else 'No'}")
        st.write(f"File IDs: {len(st.session_state.get('file_ids', []))}")
    
    with col2:
        st.write("**Environment:**")
        
        # Check different API key sources
        env_api_key = os.getenv("OPENAI_API_KEY")
        secrets_api_key = None
        try:
            secrets_api_key = st.secrets.get("OPENAI_API_KEY")
        except:
            pass
        
        # Environment detection
        is_cloud = "streamlit" in str(Path.cwd()).lower() or not Path("requirements.txt").exists()
        
        st.write(f"Environment: {'Streamlit Cloud' if is_cloud else 'Local'}")
        
        st.write(f"Env API Key: {'✅ Set' if env_api_key else '❌ Not Set'}")
        st.write(f"Secrets API Key: {'✅ Set' if secrets_api_key else '❌ Not Set'}")
        st.write(f"Database Path: {DATABASE_PATH.exists()}")
        if DATABASE_PATH.exists():
            csv_count = len([f for f in DATABASE_PATH.glob("*.csv")])
            st.write(f"CSV Files: {csv_count}")
    
    # Show recent logs
    st.write("**Recent Log Entries:**")
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("restaurant_app_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest_log, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-10:] if len(lines) > 10 else lines
                    st.text_area("Last 10 log entries:", value=''.join(recent_lines), height=200)
            except Exception as e:
                st.error(f"Error reading log file: {e}")
        else:
            st.write("No log files found")
    else:
        st.write("Logs directory not found")

def display_summary_metrics():
    """Display key summary metrics"""
    st.header("Key Metrics Summary")
    
    # Load key data for metrics
    pos_data = load_csv_data(DATABASE_PATH / "pos_sales.csv")
    finance_data = load_csv_data(DATABASE_PATH / "finance_accounting.csv")
    inventory_data = load_csv_data(DATABASE_PATH / "inventory.csv")
    
    if pos_data is not None and finance_data is not None:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_orders = len(pos_data)
            st.metric("Total Orders", total_orders)
        
        with col2:
            if 'Total' in pos_data.columns:
                total_sales = pos_data['Total'].sum()
                st.metric("Total Sales", f"${total_sales:,.2f}")
        
        with col3:
            if 'Total' in pos_data.columns:
                avg_ticket = pos_data['Total'].mean()
                st.metric("Avg Ticket Size", f"${avg_ticket:.2f}")
        
        with col4:
            if inventory_data is not None and 'Total_Used_Cost' in inventory_data.columns:
                total_cogs = inventory_data['Total_Used_Cost'].sum()
                st.metric("Total COGS", f"${total_cogs:,.2f}")

# Sidebar navigation
st.sidebar.title("Navigation")

# Add Home and Dashboard options to the list
page_options = ["Home", "Dashboard"] + list(CSV_FILES.keys())

# Page selection
selected_page = st.sidebar.selectbox(
    "Select a page:",
    page_options,
    index=0
)

# Display pages based on selection
if selected_page == "Home":
    # Home page with AI analysis
    show_home_page()

elif selected_page == "Dashboard":
    # Dashboard page
    st.header("Dashboard Overview")
    display_summary_metrics()
    
    # Quick overview of each table
    st.subheader("Data Overview")
    
    for display_name, file_name in CSV_FILES.items():
        file_path = DATABASE_PATH / file_name
        data = load_csv_data(file_path)
        
        if data is not None:
            with st.expander(f"{display_name} ({len(data)} records)"):
                st.dataframe(data.head(3), use_container_width=True)
                st.caption(f"Showing first 3 rows of {len(data)} total records")

else:
    # Individual table pages
    selected_table = selected_page
    file_path = DATABASE_PATH / CSV_FILES[selected_table]
    data = load_csv_data(file_path)
    
    if data is not None:
        st.header(f"{selected_table}")
        
        # Add filters and search
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Search functionality
            if len(data) > 0:
                search_term = st.text_input(f"Search in {selected_table}:", placeholder="Enter search term...")
                if search_term:
                    # Search across all string columns
                    string_columns = data.select_dtypes(include=['object']).columns
                    mask = data[string_columns].astype(str).apply(
                        lambda x: x.str.contains(search_term, case=False, na=False)
                    ).any(axis=1)
                    data = data[mask]
                    st.info(f"Found {len(data)} records matching '{search_term}'")
        
        with col2:
            # Download button
            csv = data.to_csv(index=False)
            st.download_button(
                label=f"Download {selected_table}",
                data=csv,
                file_name=f"{selected_table.lower().replace(' & ', '_').replace(' ', '_')}.csv",
                mime="text/csv"
            )
        
        # Format currency columns for specific tables
        currency_columns = []
        if selected_table in ["Menu", "POS Sales", "Inventory", "Finance & Accounting"]:
            currency_columns = [col for col in data.columns if any(keyword in col.lower() for keyword in ['price', 'cost', 'total', 'subtotal', 'tax', 'tip', 'value', 'sales'])]
            if currency_columns:
                data = format_currency_columns(data, currency_columns)
        
        # Display the table
        st.dataframe(
            data,
            use_container_width=True,
            height=600
        )
        
        # Table statistics
        st.subheader("Table Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(data))
        with col2:
            st.metric("Total Columns", len(data.columns))
        with col3:
            if len(data) > 0:
                numeric_cols = data.select_dtypes(include=['number']).columns
                st.metric("Numeric Columns", len(numeric_cols))

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Restaurant Operations Dashboard | Built with Streamlit</p>
        <p>Data includes Menu, Inventory, Sales, Reservations, Reviews, Staff, Vendors, CRM, Finance & Marketing</p>
    </div>
    """,
    unsafe_allow_html=True
)



# Check if database folder exists
if not DATABASE_PATH.exists():
    st.error("Database folder not found! Please ensure the 'database' folder exists with CSV files.")
    st.stop()
