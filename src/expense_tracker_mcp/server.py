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
    get_payment_method_analysis as db_get_payment_method_analysis,
    get_recurring_expenses as db_get_recurring_expenses,
    get_financial_dashboard_summary as db_get_financial_dashboard_summary,
)


mcp = FastMCP("ExpenseTracker")


@mcp.tool
async def add_expense(
    user_id: str,
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    description: str = "",
    payment_method: str = ""
):
    """Add a new expense."""

    expense_id = await db_add_expense(
        user_id,
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
async def get_expense(user_id: str, expense_id: int):
    """Get a single expense by ID."""

    expense = await db_get_expense(user_id, expense_id)

    if expense is None:
        return {
            "success": False,
            "message": f"Expense with ID {expense_id} not found"
        }

    return expense


@mcp.tool
async def list_expenses(user_id: str):
    """Get all expenses."""

    return await db_list_expenses(user_id)


@mcp.tool
async def update_expense(
    user_id: str,
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
        user_id,
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
async def delete_expense(
    user_id: str,
    expense_id: int
):
    """Delete an expense by ID for a specific user."""

    rows_deleted = await db_delete_expense(
        user_id,
        expense_id
    )

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
async def search_expenses(
    user_id: str,
    keyword: str
):
    """Search expenses by keyword for a specific user."""

    return await db_search_expenses(
        user_id,
        keyword
    )



@mcp.tool
async def get_expense_summary(user_id: str):
    """Get expense summary and category-wise spending for a specific user."""

    return await db_get_expense_summary(user_id)



@mcp.tool
async def get_expense_summary_by_date(
    user_id: str,
    start_date: str,
    end_date: str
):
    """Get expense summary for a specific date range."""

    return await db_get_expense_summary_by_date(
        user_id,
        start_date,
        end_date
    )


@mcp.tool
async def get_monthly_expense_report(
    user_id: str,
    year: int,
    month: int
):
    """Get expense report for a specific month and user."""

    return await db_get_monthly_expense_report(
        user_id,
        year,
        month
    )


@mcp.tool
async def get_category_expense_report(
    user_id: str,
    category: str
):
    """Get expense report for a specific category and user."""

    return await db_get_category_expense_report(
        user_id,
        category
    )



@mcp.tool
async def get_expense_statistics(user_id: str):
    """Get expense statistics for a specific user."""

    return await db_get_expense_statistics(user_id)


@mcp.tool
async def set_budget(
    user_id: str,
    category: str,
    monthly_limit: float
):
    """
    Create or update a monthly budget for a specific user.

    Use this tool when the user wants to set or change the
    monthly spending limit for an expense category.

    Args:
        user_id: Unique identifier of the user.
        category: Expense category for the budget.
        monthly_limit: Maximum monthly spending limit.

    Returns:
        A dictionary containing the user ID, category, and
        configured monthly budget.
    """

    return await db_set_budget(
        user_id,
        category,
        monthly_limit
    )


@mcp.tool
async def get_budgets(user_id: str):
    """
    Get all monthly budgets for a specific user.

    Use this tool when the user wants to view their configured
    category budgets and monthly spending limits.

    Args:
        user_id: Unique identifier of the user.

    Returns:
        A list of the user's category budgets, including
        category names and monthly spending limits.
    """

    return await db_get_budgets(user_id)


@mcp.tool
async def get_budget_status(
    user_id: str,
    category: str
):
    """
    Check the current monthly budget status for a specific user
    and expense category.

    Use this tool when the user wants to know how much they have
    spent from a category budget and how much budget remains.

    Args:
        user_id: Unique identifier of the user.
        category: Expense category whose budget status should
                  be checked.

    Returns:
        A dictionary containing the category budget, amount spent
        during the current month, remaining budget, and a message
        if no budget is configured.
    """

    return await db_get_budget_status(
        user_id,
        category
    )


@mcp.tool
async def get_spending_alert(
    user_id: str,
    category: str
):
    """
    Check whether a user's spending is approaching or exceeding
    the monthly budget for a specific category.

    Use this tool when the user wants to know whether they are
    close to or over their budget limit.

    An alert is triggered when spending reaches 80% or more of
    the configured monthly budget.

    Args:
        user_id: Unique identifier of the user.
        category: Expense category whose budget usage should
                  be checked.

    Returns:
        A dictionary containing the budget, amount spent,
        percentage of budget used, alert status, and a
        descriptive spending message.
    """

    return await db_get_spending_alert(
        user_id,
        category
    )


@mcp.tool
async def get_top_spending_categories(
    user_id: str,
    limit: int = 5
):
    """
    Identify the top spending categories for a specific user.

    Use this tool when the user wants to know which expense
    categories account for the most spending.

    Args:
        user_id: Unique identifier of the user.
        limit: Maximum number of top categories to return.

    Returns:
        A list of categories ranked by total spending,
        including expense count and total amount.
    """

    return await db_get_top_spending_categories(
        user_id,
        limit
    )


@mcp.tool
async def get_expense_insights(user_id: str):
    """
    Get overall spending insights for a specific user.

    Use this tool when the user wants a summary of their
    spending patterns, including total expenses, average
    spending, highest and lowest expenses, and top category.

    Args:
        user_id: Unique identifier of the user.

    Returns:
        A dictionary containing the user's expense statistics
        and top spending category.
    """

    return await db_get_expense_insights(user_id)



@mcp.tool
async def get_expense_trends(user_id: str):
    """Get month-wise expense trends for a specific user."""

    return await db_get_expense_trends(user_id)



@mcp.tool
async def get_daily_spending_summary(user_id: str):
    """Get date-wise expense summary for a specific user."""

    return await db_get_daily_spending_summary(user_id)


@mcp.tool
async def get_payment_method_analysis(user_id: str):
    """Get expense analysis by payment method for a specific user."""

    return await db_get_payment_method_analysis(user_id)


@mcp.tool
async def get_recurring_expenses(user_id: str):
    """
    Identify recurring expense patterns for a specific user.

    Use this tool when the user wants to find repeated expenses
    based on the same category and amount.

    Args:
        user_id: Unique identifier of the user.

    Returns:
        A list of recurring expense patterns with category,
        amount, and occurrence count.
    """

    return await db_get_recurring_expenses(user_id)


@mcp.tool
async def get_financial_dashboard_summary(user_id: str):
    """
    Get a complete financial dashboard summary for a specific user.

    Use this tool when the user wants an overall view of their
    financial activity, including expense statistics, top spending
    categories, monthly spending trends, and budgets.

    Args:
        user_id: Unique identifier of the user whose financial
                 dashboard should be retrieved.

    Returns:
        A dictionary containing:
        - Overall expense statistics
        - Top spending categories
        - Monthly spending trends
        - User-specific budgets
    """

    return await db_get_financial_dashboard_summary(user_id)



if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )