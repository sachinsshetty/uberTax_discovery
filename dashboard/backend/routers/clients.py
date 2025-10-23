# File: routers/clients.py (minor tweaks for robustness)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, ClientProfile
from schemas import ClientProfileCreate, ClientProfileUpdate, ClientProfileResponse  # Updated schemas
from datetime import date
from typing import List
from pydantic import Field  # If using explicit Fields in schemas

import os
from openai import OpenAI
import json
from sqlalchemy import text
from typing import Any, Dict


router = APIRouter(prefix="/api/clients", tags=["clients"])

@router.get("/", response_model=List[ClientProfileResponse])
async def get_clients(db: Session = Depends(get_db)):
    """Fetch all client profiles with Pydantic validation."""
    clients = db.query(ClientProfile).all()
    return clients  # Now serializes correctly with aliases

@router.post("/", response_model=ClientProfileResponse, status_code=201)
async def create_client(
    client: ClientProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new client profile with Pydantic validation."""
    # Check if client_id already exists
    existing = db.query(ClientProfile).filter(ClientProfile.client_id == client.client_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Client ID already exists")
    
    # Parse deadline
    deadline_date = None
    if client.deadline:
        try:
            deadline_date = date.fromisoformat(client.deadline)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline format. Use ISO format (YYYY-MM-DD).")
    
    db_client = ClientProfile(
        client_id=client.client_id,
        company_name=client.company_name,
        country=client.country,
        new_regulation=client.new_regulation,
        deadline=deadline_date,
        status=client.status
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client  # Serializes to camelCase JSON

@router.put("/{client_id}", response_model=ClientProfileResponse)
async def update_client(
    client_id: str,
    update_data: ClientProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing client profile with Pydantic validation."""
    db_client = db.query(ClientProfile).filter(ClientProfile.client_id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    if "deadline" in update_dict and update_dict["deadline"]:
        try:
            update_dict["deadline"] = date.fromisoformat(update_dict["deadline"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline format. Use ISO format (YYYY-MM-DD).")
    else:
        update_dict["deadline"] = None
    
    for field, value in update_dict.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client

@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: str,
    db: Session = Depends(get_db)
):
    """Delete a client profile."""
    db_client = db.query(ClientProfile).filter(ClientProfile.client_id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(db_client)
    db.commit()
    return None

# File: routers/clients.py (corrected query_database function)

import os
from openai import OpenAI
import json
from sqlalchemy import text
from typing import Any, Dict

# ... (existing imports and code remain the same)

# Define the query_database tool function
def query_database(sql_query: str, db: Session) -> str:
    """
    Execute a SQL query on the client_profiles table and return results as JSON.
    """
    try:
        # Assuming the table name is 'client_profiles' based on the model name
        # Add safety: only allow SELECT queries starting with 'SELECT'
        if not sql_query.strip().upper().startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed.")
        
        result = db.execute(text(sql_query))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return json.dumps(rows, default=str)  # Handle dates
    except Exception as e:
        return f"Error executing query: {str(e)}"


DWANI_API_BASE_URL = os.getenv('DWANI_API_BASE_URL')

@router.post("/natural-query", response_model=Dict[str, Any])
async def natural_query(
    query_data: Dict[str, str],  # e.g., {"user_query": "Show me all pending clients from USA"}
    db: Session = Depends(get_db)
):
    """
    Query the client profiles table using natural language via Qwen3-VL tool calling.
    Expects JSON body with 'user_query' key.
    """
    user_query = query_data.get("user_query")
    if not user_query:
        raise HTTPException(status_code=400, detail="Missing 'user_query' in request body")
    
    # Initialize OpenAI-compatible client for DashScope
    client = OpenAI(
        api_key="asdasd",
        base_url= f"{DWANI_API_BASE_URL}/v1",
    )

    # Define the tool for database querying
    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "description": "Execute a SQL SELECT query on the client_profiles table to retrieve client profiles based on the natural language request. Use only SELECT statements on columns: client_id, company_name, country, new_regulation, deadline, status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "A valid SQL SELECT query, e.g., 'SELECT * FROM client_profiles WHERE status = \"pending\" AND country = \"USA\"'",
                        }
                    },
                    "required": ["sql_query"],
                },
            },
        }
    ]

    # Initialize messages with system prompt
    messages = [
        {
            "role": "system",
            "content": """You are a helpful database assistant. Analyze the user's natural language query about client profiles and use the query_database tool to fetch relevant data from the client_profiles table. After getting the results, summarize them clearly in your response, including key details like company names, countries, statuses, and deadlines if applicable. If no data matches, explain why."""
        },
        {"role": "user", "content": user_query}
    ]

    # Make the initial API call
    response = client.chat.completions.create(
        model="gemma3",  # Use Qwen3-VL model; adjust if exact name differs (e.g., qwen-vl-max)
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message)

    # Handle tool calls in a loop until no more are needed
    while assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            if function_name == "query_database":
                arguments = json.loads(tool_call.function.arguments)
                tool_result = query_database(arguments["sql_query"], db)
                tool_message = {
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_call.id,
                }
                messages.append(tool_message)
                print(f"Tool result: {tool_result}")  # For debugging; remove in production

        # Make follow-up API call with tool results
        response = client.chat.completions.create(
            model="gemma3",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        assistant_message = response.choices[0].message
        messages.append(assistant_message)

    # Return the final natural language response
    return {
        "natural_response": assistant_message.content,
        "raw_data": None,  # Optionally parse and include raw JSON data here if needed
        "query_used": user_query
    }