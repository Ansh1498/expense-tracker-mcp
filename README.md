# 💰 Expense Tracker MCP Server

A lightweight and asynchronous **Expense Tracker MCP Server** built with **FastMCP**, **SQLite**, and **Python**.

This project exposes expense-management functionality as **Model Context Protocol (MCP) tools**, allowing MCP-compatible AI clients to interact with an expense database through natural language.

---

## 🚀 Features

- ➕ Add new expenses
- 🔍 Get a specific expense by ID
- 📋 List all expenses
- ✏️ Update existing expenses
- 🗑️ Delete expenses
- 🔎 Search expenses by keyword

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

### 🛡️ Reliability

- ✅ Expense input validation
- ⚠️ Database error handling
- 📝 Error logging

### ⚙️ Infrastructure

- 💾 SQLite database for persistent storage
- ⚡ Asynchronous database operations using `aiosqlite`
- 🔌 MCP interface using `FastMCP`
- 🌐 Streamable HTTP transport
- 🧩 Modular project structure separating MCP tools and database logic

---

## 🛠️ Tech Stack

| Technology      | Purpose                                   |
| --------------- | ----------------------------------------- |
| Python          | Core programming language                 |
| FastMCP         | MCP server and tool integration           |
| SQLite          | Local database                            |
| aiosqlite       | Asynchronous SQLite operations            |
| uv              | Python package and environment management |
| Streamable HTTP | MCP server transport                      |

---

## 📁 Project Structure

```text
expense-tracker-mcp/
│
├── src/
│   └── expense_tracker_mcp/
│       ├── __init__.py
│       ├── database.py
│       ├── server.py
│       └── expenses.db
│
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
└── uv.lock
```
