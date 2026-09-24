from fastmcp import FastMCP

from expense_tracker_mcp.database import (
    init_db,
    add_expense as db_add_expense,
    get_expense as db_get_expense,
    list_expenses as db_list_expenses,
    update_expense as db_update_expense,
    delete_expense as db_delete_expense,
    search_expenses as db_search_expenses,
    get_expense_summary as db_get_expense_summary,
    get_expense_summary_by_date as db_get_expense_summary_by_date,
    get_monthly_expense_report as db_get_monthly_expense_report,
    get_category_expense_report as db_get_category_expense_report,
    get_expense_statistics as db_get_expense_statistics,
    set_budget as db_set_budget,
    get_budgets as db_get_budgets,
    get_budget_status as db_get_budget_status,
    get_spending_alert as db_get_spending_alert,
    get_top_spending_categories as db_get_top_spending_categories,
    get_expense_insights as db_get_expense_insights,
    get_expense_trends as db_get_expense_trends,
    get_daily_spending_summary as db_get_daily_spending_summary,
)


mcp = FastMCP("ExpenseTracker")


@mcp.tool
async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    description: str = "",
    payment_method: str = ""
):
    """Add a new expense."""

    expense_id = await db_add_expense(
        date,
        amount,
        category,
        subcategory,
        description,
        payment_method
    )

    return {
        "success": True,
        "expense_id": expense_id,
        "message": "Expense added successfully"
    }

@mcp.tool
async def get_expense(expense_id: int):
    """Get a single expense by ID."""

    expense = await db_get_expense(expense_id)

    if expense is None:
        return {
            "success": False,
            "message": f"Expense with ID {expense_id} not found"
        }

    return expense


@mcp.tool
async def list_expenses():
    """Get all expenses."""

    return await db_list_expenses()


@mcp.tool
async def update_expense(
    expense_id: int,
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    description: str = "",
    payment_method: str = ""
):
    """Update an existing expense."""

    rows_updated = await db_update_expense(
        expense_id,
        date,
        amount,
        category,
        subcategory,
        description,
        payment_method
    )

    if rows_updated == 0:
        return {
            "success": False,
            "message": f"Expense with ID {expense_id} not found"
        }

    return {
        "success": True,
        "message": "Expense updated successfully",
        "expense_id": expense_id
    }


@mcp.tool
async def delete_expense(expense_id: int):
    """Delete an expense by ID."""

    rows_deleted = await db_delete_expense(expense_id)

    if rows_deleted == 0:
        return {
            "success": False,
            "message": f"Expense with ID {expense_id} not found"
        }

    return {
        "success": True,
        "message": "Expense deleted successfully",
        "expense_id": expense_id
    }


@mcp.tool
async def search_expenses(keyword: str):
    """Search expenses by keyword."""

    return await db_search_expenses(keyword)


@mcp.tool
async def get_expense_summary():
    """Get overall expense summary and category-wise spending."""

    return await db_get_expense_summary()


@mcp.tool
async def get_expense_summary_by_date(
    start_date: str,
    end_date: str
):
    """Get expense summary for a specific date range."""

    return await db_get_expense_summary_by_date(
        start_date,
        end_date
    )


@mcp.tool
async def get_monthly_expense_report(
    year: int,
    month: int
):
    """Get expense report for a specific month."""

    return await db_get_monthly_expense_report(
        year,
        month
    )

@mcp.tool
async def get_category_expense_report(category: str):
    """Get expense report for a specific category."""

    return await db_get_category_expense_report(category)


@mcp.tool
async def get_expense_statistics():
    """Get overall expense statistics."""

    return await db_get_expense_statistics()


@mcp.tool
async def set_budget(
    category: str,
    monthly_limit: float
):
    """Set or update a monthly budget for a category."""

    return await db_set_budget(
        category,
        monthly_limit
    )


@mcp.tool
async def get_budgets():
    """Get all category budgets."""

    return await db_get_budgets()


@mcp.tool
async def get_budget_status(category: str):
    """Compare monthly budget with actual spending."""

    return await db_get_budget_status(category)


@mcp.tool
async def get_spending_alert(category: str):
    """Check whether spending is approaching or exceeding the budget."""

    return await db_get_spending_alert(category)


@mcp.tool
async def get_top_spending_categories(limit: int = 5):
    """Get top spending categories by total amount."""

    return await db_get_top_spending_categories(limit)


@mcp.tool
async def get_expense_insights():
    """Get overall spending insights."""

    return await db_get_expense_insights()


@mcp.tool
async def get_expense_trends():
    """Get month-wise expense trends."""

    return await db_get_expense_trends()



@mcp.tool
async def get_daily_spending_summary():
    """Get date-wise expense summary."""

    return await db_get_daily_spending_summary()


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )