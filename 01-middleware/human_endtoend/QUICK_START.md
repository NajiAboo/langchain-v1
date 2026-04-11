# Quick Start Guide - Agent Chat System

## 🎯 One-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Backend
```bash
python main.py
```
You should see: `Uvicorn running on http://127.0.0.1:8000`

### Step 3: Open Frontend
Open `index.html` in your web browser (or serve via HTTP on port 8001)

### Step 4: Start Chatting!
Try these commands:
- "send a email to john@example.com saying hello world"
- "delete all record from customer table with name as john"
- "read email"

---

## 📋 API Response Format Reference

### Response Types

All API responses have a `type` field that determines the response:

#### 1️⃣ Completed - Action Executed
```json
{
  "type": "completed",
  "thread_id": "thread_1234567890_abc",
  "message": "Email sent to john@example.com with content: hello world",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**When it happens:**
- Tool executed successfully
- Action was denied/rejected
- Tool doesn't require approval (like read_email)

---

#### 2️⃣ Interrupt - Waiting for Approval
```json
{
  "type": "interrupt",
  "thread_id": "thread_1234567890_abc",
  "message": "Action pending approval: send_email",
  "pending_actions": [
    {
      "action_id": "550e8400-e29b-41d4-a716-446655440000",
      "tool_name": "send_email",
      "description": "Please review the email content before sending",
      "allowed_decisions": ["approve", "reject", "edit"],
      "tool_args": {
        "email_id": "john@example.com",
        "content": "hello world"
      },
      "parameters": [
        {
          "name": "email_id",
          "value": "john@example.com",
          "type": "str",
          "editable": true
        },
        {
          "name": "content",
          "value": "hello world",
          "type": "str",
          "editable": true
        }
      ]
    }
  ],
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**When it happens:**
- Action requires user approval
- User can approve, reject, or edit

**What the UI shows:**
- Yellow warning box with ⚠️ icon
- Action card with tool name and description
- All parameters listed as read-only fields
- Buttons: Approve, Reject, Edit

---

#### 3️⃣ Error - Something Went Wrong
```json
{
  "type": "error",
  "thread_id": "thread_1234567890_abc",
  "error": "Could not understand the request",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**When it happens:**
- Message doesn't match any known tool
- API processing fails
- Invalid request format

**What the UI shows:**
- Red error message with ❌ icon

---

## 🔄 Complete Workflow Example

### Scenario: Send Email with Edit

#### 1. User Sends Message
```
Input: "send a email to john@example.com saying hello there"
```

#### 2. Backend Response (Interrupt)
The API returns an interrupt because `send_email` requires approval:

```json
{
  "type": "interrupt",
  "pending_actions": [{
    "action_id": "act-123",
    "tool_name": "send_email",
    "allowed_decisions": ["approve", "reject", "edit"],
    "parameters": [
      {"name": "email_id", "value": "john@example.com"},
      {"name": "content", "value": "hello there"}
    ]
  }]
}
```

#### 3. Frontend Displays
- Yellow interrupt panel
- Shows tool: "Send Email"
- Parameters shown in read-only mode
- Three buttons: [Approve] [Reject] [Edit]

#### 4. User Clicks Edit
- Parameters become editable (text fields turn blue)
- Edit indicator appears: "✏️ Edit Mode"
- Buttons change to: [Save & Approve] [Cancel]

#### 5. User Modifies Content
User changes content from "hello there" to "hello, I am on leave"

#### 6. User Clicks Save & Approve
Frontend sends edit request:
```json
{
  "thread_id": "thread_xxx",
  "action_id": "act-123",
  "edited_parameters": {
    "email_id": "john@example.com",
    "content": "hello, I am on leave"
  }
}
```

#### 7. Backend Response (Updated Interrupt)
```json
{
  "type": "interrupt",
  "message": "Action parameters updated",
  "pending_actions": [{
    "action_id": "act-123",
    "parameters": [
      {"name": "email_id", "value": "john@example.com"},
      {"name": "content", "value": "hello, I am on leave"}
    ]
  }]
}
```

#### 8. Frontend Updates
- Action card shown with new parameters
- Back in normal mode (not editing)
- Shows: [Approve] [Reject] [Edit] buttons again

#### 9. User Clicks Approve
Frontend sends approve request:
```json
{
  "thread_id": "thread_xxx",
  "action_id": "act-123",
  "decision": "approve"
}
```

#### 10. Backend Executes
```json
{
  "type": "completed",
  "message": "Email sent to john@example.com with content: hello, I am on leave"
}
```

#### 11. Frontend Shows Result
- Removes action card
- Displays assistant message: "Email sent to john@example.com..."

---

## 🛠️ API Request/Response Summary

### POST `/api/chat` - Send Message
**Request:**
```json
{
  "thread_id": "thread_xxx",
  "message": "your message here"
}
```

**Responses:** `completed`, `interrupt`, or `error`

---

### POST `/api/approve` - Approve Action
**Request:**
```json
{
  "thread_id": "thread_xxx",
  "action_id": "action_yyy",
  "decision": "approve"
}
```

**Response:** `completed` with execution result

---

### POST `/api/edit` - Edit Parameters
**Request:**
```json
{
  "thread_id": "thread_xxx",
  "action_id": "action_yyy",
  "edited_parameters": {
    "parameter_name": "new_value"
  }
}
```

**Response:** `interrupt` with updated action

---

### POST `/api/deny` - Reject Action
**Request:**
```json
{
  "thread_id": "thread_xxx",
  "action_id": "action_yyy"
}
```

**Response:** `completed` with denial message

---

### GET `/api/session/{thread_id}` - Get History
**Response:**
```json
{
  "thread_id": "thread_xxx",
  "messages": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "..."}
  ],
  "pending_actions": [],
  "created_at": "2024-01-15T10:30:00"
}
```

---

## 📝 Supported Commands

### Send Email
```
"send a email to [email_address] saying [message]"

Examples:
- "send a email to john@gmail.com saying I am on leave"
- "send a email to boss@company.com saying project is done"
```
**Requires:** Approve, Reject, or Edit

---

### Delete Customer
```
"delete all record from customer table with name as [name]"

Examples:
- "delete all record from customer table with name as john"
- "delete all record from customer table with name as naji"
```
**Requires:** Approve or Reject

---

### Read Email
```
"read email"
```
**Executes immediately** (no approval needed)

---

## 💡 Key Points

1. **Every response has a `type` field** - Use this to determine how to handle the response
2. **Parameters are always extracted** - All tool arguments become editable parameters in interrupt responses
3. **Action cards are dynamic** - Buttons and fields are rendered based on API response
4. **Session tracking** - Thread ID uniquely identifies each conversation
5. **Full history available** - Use GET `/api/session/{thread_id}` to retrieve conversation history

---

## 🐛 Common Issues

**Q: Chat not connecting to API?**
A: Make sure `python main.py` is running on port 8000

**Q: Buttons not appearing?**
A: Check browser console for errors; verify API response includes `allowed_decisions`

**Q: Edit fields not editable?**
A: Click "Edit" button first to enter edit mode

**Q: Changes not saving?**
A: Click "Save & Approve" (not just close edit mode)

---

## ✅ Test Flow

1. Open browser with `index.html`
2. Send: "send a email to test@example.com saying hello"
3. Click "Edit"
4. Change message to "hello there"
5. Click "Save & Approve"
6. Click "Approve"
7. See completion message in chat

Done! 🎉

