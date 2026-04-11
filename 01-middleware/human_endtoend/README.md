# Agent Chat System - Complete Documentation

## 📋 Overview

This is a complete implementation of an interactive agent chat system with human-in-the-loop approval for sensitive operations. It consists of:

1. **FastAPI Backend** (`main.py`) - REST API with session management and tool execution
2. **HTML/JavaScript Frontend** (`index.html`) - Pure client-side chat interface
3. **Response Format** - Standardized JSON responses for different interaction types

## 🏗️ Architecture

### Backend Components

#### 1. **PendingAction Class**
Represents a tool execution waiting for user approval with editable parameters.

```python
PendingAction(
    action_id: str,           # Unique identifier
    tool_name: str,           # Name of tool to execute
    tool_args: Dict,          # Arguments for the tool
    description: str,         # User-friendly description
    allowed_decisions: List   # ["approve", "reject", "edit"]
)
```

#### 2. **SessionManager**
Manages chat sessions, message history, and pending actions across threads.

```python
# Creates isolated session for each thread_id
session_manager.create_session(thread_id)

# Add messages to conversation history
session_manager.add_message(thread_id, "user", "message content")

# Store pending actions awaiting approval
session_manager.add_pending_action(thread_id, pending_action)
```

#### 3. **MockAgent**
Simulates the LangGraph agent with tool parsing and execution.

```python
# Parse user intent to determine tool and arguments
tool_name, tool_args = MockAgent.parse_user_intent(message)

# Execute tool and return result
result = MockAgent.execute_tool(tool_name, tool_args)
```

### Response Types

All API responses follow this format:

#### ✅ Completed Response
```json
{
  "type": "completed",
  "thread_id": "thread_xxx",
  "message": "Action result message",
  "timestamp": "2024-01-15T10:30:00"
}
```

#### ⚠️ Interrupt Response (Awaiting Approval)
```json
{
  "type": "interrupt",
  "thread_id": "thread_xxx",
  "message": "Action pending approval: send_email",
  "pending_actions": [
    {
      "action_id": "action_xxx",
      "tool_name": "send_email",
      "description": "Please review the email content before sending",
      "allowed_decisions": ["approve", "reject", "edit"],
      "tool_args": {
        "email_id": "user@example.com",
        "content": "Hello there"
      },
      "parameters": [
        {
          "name": "email_id",
          "value": "user@example.com",
          "type": "str",
          "editable": true
        },
        {
          "name": "content",
          "value": "Hello there",
          "type": "str",
          "editable": true
        }
      ]
    }
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

#### ❌ Error Response
```json
{
  "type": "error",
  "thread_id": "thread_xxx",
  "error": "Error message",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🔌 API Endpoints

### 1. Chat Endpoint
**POST** `/api/chat`

Process user message and determine if action requires approval.

**Request:**
```json
{
  "thread_id": "thread_1234",
  "message": "send a email to john@example.com saying hello"
}
```

**Response:** `completed`, `interrupt`, or `error`

### 2. Approve Action
**POST** `/api/approve`

Execute a pending action after user approval.

**Request:**
```json
{
  "thread_id": "thread_1234",
  "action_id": "action_5678",
  "decision": "approve"
}
```

### 3. Edit Action
**POST** `/api/edit`

Modify parameters of a pending action.

**Request:**
```json
{
  "thread_id": "thread_1234",
  "action_id": "action_5678",
  "edited_parameters": {
    "email_id": "newemail@example.com",
    "content": "Updated content"
  }
}
```

### 4. Deny Action
**POST** `/api/deny`

Reject a pending action.

**Request:**
```json
{
  "thread_id": "thread_1234",
  "action_id": "action_5678"
}
```

### 5. Get Session
**GET** `/api/session/{thread_id}`

Retrieve session history and pending actions.

### 6. Health Check
**GET** `/health`

Check API status.

## 🎨 Frontend Features

### Chat Interface
- Real-time conversation display
- Timestamps for each message
- Auto-scroll to latest messages
- Thread ID tracking

### Interrupt Handling
When action requires approval:
1. **Action Card** displays tool name, description, and parameters
2. **Dynamic Buttons** based on allowed decisions:
   - ✅ Approve - Execute immediately
   - ❌ Reject - Cancel action
   - ✏️ Edit - Modify parameters

### Edit Mode
- Parameters become editable
- Edit mode indicator appears
- "Save & Approve" and "Cancel" buttons
- Updated parameters returned for approval

### Supported Commands

#### Delete Customer
```
"delete all record from customer table with name as [name]"
```
Decisions: approve, reject

#### Send Email
```
"send a email to [email] saying [content]"
```
Decisions: approve, reject, edit

#### Read Email
```
"read email"
```
Executes immediately (no approval needed)

## 🚀 Getting Started

### Installation
```bash
pip install -r requirements.txt
```

### Running

1. **Start backend:**
```bash
python main.py
```
Server runs on `http://localhost:8000`

2. **Open frontend:**
Open `index.html` in browser or serve via HTTP:
```bash
python -m http.server 8001
```

3. **API Docs:**
Open `http://localhost:8000/docs`

## 📝 Adding New Tools

### 1. Add Tool Config
```python
TOOL_CONFIG = {
    "my_tool": {
        "allowed_decisions": ["approve", "reject", "edit"],
        "description": "Tool description"
    }
}
```

### 2. Add Parsing Logic
```python
elif "keyword" in message_lower:
    return "my_tool", {"param": value}
```

### 3. Add Execution Logic
```python
elif tool_name == "my_tool":
    result = do_something(tool_args)
    return result
```

## 🔄 Workflow Example

```
User Input
    ↓
Parse Intent & Extract Parameters
    ↓
Check if Approval Needed
    ├─ No → Execute & Return Result
    └─ Yes → Show Interrupt Panel
        ↓
    User Decision
        ├─ Approve → Execute & Return Result
        ├─ Edit → Enable Editing Mode
        │        ↓
        │   User Modifies Parameters
        │        ↓
        │   Save Edits (return to approval state)
        └─ Reject → Return Denial Message
```

## 📦 Response Format Summary

| Type | When | Contains |
|------|------|----------|
| `completed` | Action executed or denied | message, result |
| `interrupt` | Awaiting user approval | pending_actions with parameters |
| `error` | Processing failed | error message |

## 🔐 Key Features

- **Session Isolation**: Independent sessions per thread_id
- **Editable Parameters**: All action parameters can be modified
- **Dynamic UI**: Buttons and inputs generated from API response
- **Type Detection**: Automatically uses textarea for long text
- **History Tracking**: Full message history per session
- **No External Dependencies**: Pure HTML/JavaScript frontend

## 📁 File Structure
```
├── main.py          # FastAPI backend
├── index.html       # Chat interface
├── requirements.txt # Dependencies
└── README.md        # Documentation
```

---

**Ready to use!** Start the server and open the chat interface to begin.
