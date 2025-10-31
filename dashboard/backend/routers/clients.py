# File: routers/clients.py (minor tweaks for robustness)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, ClientProfile
from schemas import ClientProfileCreate, ClientProfileUpdate, ClientProfileResponse, RegulatoryFeed  # Updated schemas
from datetime import date
from typing import List
from pydantic import Field, BaseModel  # If using explicit Fields in schemas

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

# Define the query_database tool function
def query_database(sql_query: str, db: Session) -> str:
    """
    Execute a SQL query on the specified table and return results as JSON.
    """
    try:
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
    query_data: Dict[str, str],  # e.g., {"user_query": "Show me all pending clients from USA", "table_name": "client_profiles"}
    db: Session = Depends(get_db)
):
    """
    Query any table using natural language via Qwen3-VL tool calling.
    Expects JSON body with 'user_query' and 'table_name' keys.
    """
    user_query = query_data.get("user_query")
    table_name = query_data.get("table_name")
    if not user_query:
        raise HTTPException(status_code=400, detail="Missing 'user_query' in request body")
    if not table_name:
        raise HTTPException(status_code=400, detail="Missing 'table_name' in request body")
    
    # Fetch schema dynamically for SQLite
    schema_description = ""
    try:
        schema_result = db.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
        schema_fields = []
        for row in schema_result:
            col_name = row[1]
            col_type = row[2].lower()
            # Map to simple types
            if 'char' in col_type or 'text' in col_type:
                type_str = 'string'
            elif 'int' in col_type or 'integer' in col_type:
                type_str = 'integer'
            elif 'real' in col_type:
                type_str = 'float'
            elif 'blob' in col_type:
                type_str = 'binary'
            else:
                type_str = col_type
            schema_fields.append(f"- {col_name}: {type_str}")
        schema_description = " The table schema is:\n" + "\n".join(schema_fields)
    except Exception as e:
        print(f"Error fetching schema: {e}")
        schema_description = ""
    
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
                "description": f"Execute a SQL SELECT query on the {table_name} table to retrieve data based on the natural language request. Use only SELECT statements on the {table_name} table.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": f"A valid SQL SELECT query, e.g., 'SELECT * FROM {table_name} WHERE status = \"pending\" AND country = \"USA\"'",
                        }
                    },
                    "required": ["sql_query"],
                },
            },
        }
    ]

    # Initialize messages with updated system prompt
    messages = [
        {
            "role": "system",
            "content": f"""You are a helpful and precise database assistant specialized in translating natural language to SQL for the {table_name} table.{schema_description}
Analyze the user's natural language query carefully. Generate an efficient SQL SELECT query that exactly matches the request, using appropriate WHERE clauses, ORDER BY, LIMIT if needed, and JOINs only if necessary (but prefer simple queries on this single table).
Use the query_database tool exactly once with your generated SQL query.
After receiving the tool results (which will be a JSON array of rows), respond ONLY with the raw JSON array of results as your message content. Do not add summaries, explanations, or any other text. If no data matches, the array will be empty []. Ensure your final response is valid JSON."""
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

    # Handle tool calls in a loop until no more are needed (typically one call)
    query_results = []  # Capture all tool results
    while assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            if function_name == "query_database":
                arguments = json.loads(tool_call.function.arguments)
                tool_result = query_database(arguments["sql_query"], db)
                query_results.append(tool_result)
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
            tool_choice="auto",  # Set to "none" if you want to force final response without further tools
        )
        assistant_message = response.choices[0].message
        messages.append(assistant_message)

    # Use the final assistant message as the raw JSON results (per updated prompt)
    final_results = []
    if assistant_message.content:
        try:
            # Expecting just the JSON array
            final_results = json.loads(assistant_message.content)
        except json.JSONDecodeError:
            # Fallback to last tool result if AI didn't output clean JSON
            if query_results:
                last_result = query_results[-1]
                if "Error" not in last_result:
                    final_results = json.loads(last_result)

    # Return only the final results in JSON format
    return {"results": final_results}