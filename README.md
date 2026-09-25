# 💰 Expense Tracker MCP Server

A production-ready Expense Tracker MCP Server built with **FastMCP, Python, and Turso**.

This project exposes expense management, budgeting, analytics, and financial insight functionality as **Model Context Protocol (MCP) tools**, allowing MCP-compatible AI clients to manage personal expenses through natural language.

---

## 🚀 Features

### 💸 Expense Management

- ➕ Add expenses
- 🔍 Get expense by ID
- 📋 List expenses
- ✏️ Update expenses
- 🗑️ Delete expenses
- 🔎 Search expenses

### 📊 Analytics & Reports

- 📈 Expense summary
- 📅 Date-range expense summary
- 🗓️ Monthly expense reports
- 🏷️ Category-wise expense reports
- 💰 Expense statistics
- 📉 Expense spending trends
- 📆 Daily spending summary
- 💳 Payment method analysis
- 🔁 Recurring expense detection
- 📊 Financial dashboard summary

### 💵 Budget Management

- 🎯 Set expense budgets
- 📋 View budgets
- 📊 Budget vs actual spending
- 🚨 Spending alerts
- 🔝 Top spending categories
- 💡 Expense insights

### 👤 User Isolation

- 🔐 Expenses are associated with a `user_id`
- 🛡️ Users can only access their own expense data
- 🔒 Prevents cross-user expense access

### 🛡️ Reliability

- ✅ Input validation
- ⚠️ Database error handling
- 📝 Error logging
- 🔄 Persistent cloud database

---

## ⚙️ Architecture

```text
MCP Client
    │
    ▼
FastMCP Cloud
    │
    ▼
Expense Tracker MCP Server
    │
    ▼
Turso Database
    │
    ▼
Persistent Expense Data
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastMCP | MCP server and tool integration |
| Turso | Cloud SQLite-compatible database |
| libsql-client | Python client for Turso |
| uv | Python package and environment management |
| Streamable HTTP | MCP server transport |

---

## 🌐 Deployment

The MCP server is deployed using **FastMCP Cloud**.

### MCP Endpoint

https://expenseflow-mcp.fastmcp.app/mcp

The server can be connected to MCP-compatible clients using the **Streamable HTTP** transport.

---

## 📁 Project Structure

```text
expense-tracker-mcp/
│
├── src/
│   └── expense_tracker_mcp/
│       ├── __init__.py
│       ├── database.py
│       └── server.py
│
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
└── uv.lock
```

---

## 🔐 Environment Variables

For local development, create a `.env` file:

```env
TURSO_DATABASE_URL="your-turso-database-url"
TURSO_AUTH_TOKEN="your-turso-auth-token"
```

**Never commit `.env` or database credentials to GitHub.**

---

## ▶️ Local Development

### 1. Install dependencies

```bash
uv sync
```

### 2. Run the MCP server

```bash
uv run python -m expense_tracker_mcp.server
```

The local MCP endpoint will be:

```text
http://localhost:8000/mcp
```

---

## 🧪 Testing

The project has been tested for:

- Expense creation
- Expense retrieval
- Expense listing
- Expense updating
- Expense deletion
- Expense search
- User isolation
- Expense analytics
- Budget management
- Turso database connectivity
- FastMCP Cloud deployment

Cloud functionality was tested using the **FastMCP Dev Inspector**.

---

## 🔒 Security

The project uses environment variables for sensitive database credentials.

- `.env` is excluded from Git
- Turso authentication token is not stored in source code
- User-specific expense operations use `user_id`
- Database credentials are configured separately for cloud deployment

---

## 🎯 Project Goal

The goal of this project is to build a practical MCP server demonstrating:

- MCP tool development
- FastMCP
- Cloud database integration
- Turso
- User data isolation
- Expense analytics
- Budget management
- Error handling
- Cloud deployment

---

## 👨‍💻 Author

**Ansh Kumar**

GitHub: https://github.com/Ansh1498
