# Expense Tracker MCP Server

A production-ready Expense Tracker MCP Server built with FastMCP, Python, and Turso.

This project exposes expense management, budgeting, analytics, and financial insight functionality as Model Context Protocol (MCP) tools, allowing MCP-compatible AI clients to manage personal expenses through natural language.

---

## Features

### Expense Management

- Add expenses
- Get expense by ID
- List expenses
- Update expenses
- Delete expenses
- Search expenses

### Analytics and Reports

- Expense summary
- Date-range expense summary
- Monthly expense reports
- Category-wise expense reports
- Expense statistics
- Expense spending trends
- Daily spending summary
- Payment method analysis
- Recurring expense detection
- Financial dashboard summary

### Budget Management

- Set expense budgets
- View budgets
- Budget vs actual spending
- Spending alerts

### Security and Reliability

- User-specific expense isolation
- Cross-user data access protection
- Input validation
- Database error handling
- Secure environment-based credentials

---

## Architecture

```text
MCP Client
    |
    v
FastMCP Cloud
    |
    v
Expense Tracker MCP Server
    |
    v
Turso Database
    |
    v
Persistent Expense Data
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastMCP | MCP server and tool integration |
| Turso | Cloud SQLite-compatible database |
| libsql | Python client for Turso |
| uv | Python package and environment management |
| Streamable HTTP | MCP server transport |

---

## Project Structure

```text
expense-tracker-mcp/
|
+-- src/
|   +-- expense_tracker_mcp/
|       +-- __init__.py
|       +-- database.py
|       +-- server.py
|
+-- .gitignore
+-- .python-version
+-- README.md
+-- pyproject.toml
+-- uv.lock
```

---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/Ansh1498/expense-tracker-mcp.git
cd expense-tracker-mcp
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
TURSO_DATABASE_URL="your-turso-database-url"
TURSO_AUTH_TOKEN="your-turso-auth-token"
```

Never commit your `.env` file or Turso authentication token.

### 4. Run the MCP server

```bash
uv run python -m expense_tracker_mcp.server
```

The local MCP endpoint is:

```text
http://localhost:8000/mcp
```

---

## Cloud Deployment

The MCP server is deployed using FastMCP Cloud and connected to a Turso database.

Production MCP endpoint:

```text
https://expenseflow-mcp.fastmcp.app/mcp
```

The server can be connected to MCP-compatible clients such as Claude Desktop.

---

## MCP Tools

The server provides tools for:

### Expense Operations

- `add_expense`
- `get_expense`
- `list_expenses`
- `update_expense`
- `delete_expense`
- `search_expenses`

### Analytics

- `get_expense_summary`
- `get_expense_summary_by_date`
- `get_monthly_expense_report`
- `get_category_expense_report`
- `get_expense_statistics`
- `get_expense_trends`
- `get_daily_spending_summary`
- `get_payment_method_analysis`
- `get_recurring_expenses`
- `get_top_spending_categories`
- `get_financial_dashboard_summary`

### Budget Management

- `set_budget`
- `get_budgets`
- `get_budget_status`
- `get_spending_alert`

### Insights

- `get_expense_insights`

---

## Example Natural Language Usage

Once connected to an MCP-compatible client, users can interact with the server using normal language.

```text
add a 600 rupee dinner expense paid by UPI
```

```text
how much did i spend this month?
```

```text
where did most of my money go?
```

```text
show me my financial dashboard
```

```text
am i over my food budget?
```

```text
show me how much i paid by each payment method
```

```text
how much did i spend between september 1 and september 25?
```

```text
do i have any recurring expenses?
```

---

## Testing

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
- Spending alerts
- Financial dashboard
- Turso database connectivity
- FastMCP Cloud deployment
- Claude Desktop integration

Cloud functionality was verified using the FastMCP Dev Inspector and Claude Desktop.

---

## Database

The project uses Turso as the cloud database.

Turso provides a SQLite-compatible database experience while allowing the application to use a cloud-hosted database.

The project uses the `libsql` Python package to connect to Turso.

The main database tables are:

### Expenses

Stores user expense information including:

- User ID
- Date
- Amount
- Category
- Subcategory
- Description
- Payment method
- Created timestamp
- Updated timestamp

### Budgets

Stores:

- User ID
- Category
- Monthly budget limit

---

## Security

The project uses environment variables for sensitive database credentials.

- `.env` is excluded from Git
- Turso authentication tokens are not stored in source code
- Expense operations use `user_id` for data isolation
- Cross-user expense access is prevented
- Cloud database credentials are configured separately

---

## Error Handling and Validation

The server includes:

- Input validation
- Database error handling
- Invalid expense handling
- User access validation
- Safe database operations
- Logging for troubleshooting

---

## Project Goal

The goal of this project is to build a practical MCP server demonstrating:

- MCP tool development
- FastMCP
- Turso cloud database integration
- libSQL database connectivity
- User data isolation
- Expense analytics
- Budget management
- Financial insights
- Error handling
- Cloud deployment
- AI client integration

---

## Author

**Ansh Kumar**

GitHub:

https://github.com/Ansh1498/expense-tracker-mcp
