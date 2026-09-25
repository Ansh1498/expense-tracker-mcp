import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from libsql_client import create_client

load_dotenv()


def validate_expense(
    date: str,
    amount: float,
    category: str
):
    """Validate expense input."""

    if not date:
        raise ValueError("Date is required.")

    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")

    if not category.strip():
        raise ValueError("Category is required.")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")

    return True



logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)





async def init_db():
    """
    Initialize the Turso database and create required tables.
    """

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        await client.batch([
            (
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    payment_method TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """,
                ()
            ),
            (
                """
                CREATE TABLE IF NOT EXISTS budgets (
                    user_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    monthly_limit REAL NOT NULL,
                    PRIMARY KEY (user_id, category)
                )
                """,
                ()
            )
        ])

        print("Turso database initialized successfully.")

    finally:
        await client.close()


# Add Expense function
async def add_expense(
    user_id: str,
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    description: str = "",
    payment_method: str = ""
):
    """Add a new expense for a specific user."""

    validate_expense(date, amount, category)

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        now = datetime.now().isoformat()

        await client.batch([
            (
                """
                INSERT INTO expenses (
                    user_id,
                    date,
                    amount,
                    category,
                    subcategory,
                    description,
                    payment_method,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    date,
                    amount,
                    category,
                    subcategory,
                    description,
                    payment_method,
                    now,
                    now
                )
            )
        ])

        result = await client.execute(
            """
            SELECT id
            FROM expenses
            WHERE user_id = ?
              AND date = ?
              AND amount = ?
              AND category = ?
              AND created_at = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user_id,
                date,
                amount,
                category,
                now
            )
        )

        return result.rows[0][0]

    except Exception as e:
        logging.error(f"Database error while adding expense: {e}")
        raise RuntimeError(f"Database error while adding expense: {e}")

    finally:
        await client.close()


# List Expenses function
async def list_expenses(user_id: str):
    """Get all expenses for a specific user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT *
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC, id DESC
            """,
            (user_id,)
        )

        columns = result.columns

        return [
            dict(zip(columns, row))
            for row in result.rows
        ]

    except Exception as e:
        logging.error(f"Database error while listing expenses: {e}")
        raise RuntimeError(f"Database error while listing expenses: {e}")

    finally:
        await client.close()



# Update Expense function
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
    """Update an existing expense for a specific user."""

    validate_expense(date, amount, category)

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        now = datetime.now().isoformat()

        await client.batch([
            (
                """
                UPDATE expenses
                SET
                    date = ?,
                    amount = ?,
                    category = ?,
                    subcategory = ?,
                    description = ?,
                    payment_method = ?,
                    updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    date,
                    amount,
                    category,
                    subcategory,
                    description,
                    payment_method,
                    now,
                    expense_id,
                    user_id
                )
            )
        ])

        # Verify whether the expense exists for this user
        result = await client.execute(
            """
            SELECT id
            FROM expenses
            WHERE id = ? AND user_id = ?
            """,
            (expense_id, user_id)
        )

        return 1 if result.rows else 0

    except Exception as e:
        logging.error(f"Database error while updating expense: {e}")
        raise RuntimeError(f"Database error while updating expense: {e}")

    finally:
        await client.close()


# Delete Expense function
async def delete_expense(user_id: str, expense_id: int):
    """Delete an expense by its ID for a specific user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        await client.batch([
            (
                """
                DELETE FROM expenses
                WHERE id = ? AND user_id = ?
                """,
                (expense_id, user_id)
            )
        ])

        # Verify whether the expense was deleted
        result = await client.execute(
            """
            SELECT id
            FROM expenses
            WHERE id = ? AND user_id = ?
            """,
            (expense_id, user_id)
        )

        return 0 if result.rows else 1

    except Exception as e:
        logging.error(f"Database error while deleting expense: {e}")
        raise RuntimeError(f"Database error while deleting expense: {e}")

    finally:
        await client.close()
    

# Search Expenses function
async def search_expenses(user_id: str, keyword: str):
    """Search expenses by category, subcategory, description, or payment method."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        search_term = f"%{keyword}%"

        result = await client.execute(
            """
            SELECT *
            FROM expenses
            WHERE user_id = ?
              AND (
                  category LIKE ?
                  OR subcategory LIKE ?
                  OR description LIKE ?
                  OR payment_method LIKE ?
              )
            ORDER BY date DESC, id DESC
            """,
            (
                user_id,
                search_term,
                search_term,
                search_term,
                search_term
            )
        )

        columns = result.columns

        return [
            dict(zip(columns, row))
            for row in result.rows
        ]

    except Exception as e:
        logging.error(
            f"Database error while searching expenses: {e}"
        )
        raise RuntimeError(
            f"Database error while searching expenses: {e}"
        )

    finally:
        await client.close()

# Get Expense function
async def get_expense(user_id: str, expense_id: int):
    """Retrieve a specific expense belonging to a user by expense ID."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT *
            FROM expenses
            WHERE id = ?
              AND user_id = ?
            """,
            (expense_id, user_id)
        )

        if not result.rows:
            return None

        return dict(zip(result.columns, result.rows[0]))

    except Exception as e:
        logging.error(
            f"Database error while retrieving expense: {e}"
        )
        raise RuntimeError(
            f"Database error while retrieving expense: {e}"
        )

    finally:
        await client.close()



# Expense Summary function
async def get_expense_summary(user_id: str):
    """Get expense summary and category-wise totals for a specific user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        # Total expenses and total amount
        result = await client.execute(
            """
            SELECT
                COUNT(*) AS total_expenses,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM expenses
            WHERE user_id = ?
            """,
            (user_id,)
        )

        summary = result.rows[0]

        # Category-wise total
        result = await client.execute(
            """
            SELECT
                category,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY total_amount DESC
            """,
            (user_id,)
        )

        category_summary = [
            {
                "category": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in result.rows
        ]

        return {
            "total_expenses": summary[0],
            "total_amount": summary[1],
            "category_summary": category_summary
        }

    except Exception as e:
        logging.error(f"Database error while getting expense summary: {e}")
        raise RuntimeError(f"Database error while getting expense summary: {e}")

    finally:
        await client.close()

    

# Date Range Expense Summary
async def get_expense_summary_by_date(
    user_id: str,
    start_date: str,
    end_date: str
):
    """Get expense summary for a specific date range and user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        # Total expenses and total amount
        result = await client.execute(
            """
            SELECT
                COUNT(*) AS total_expenses,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM expenses
            WHERE user_id = ?
              AND date BETWEEN ? AND ?
            """,
            (user_id, start_date, end_date)
        )

        summary = result.rows[0]

        # Category-wise summary
        result = await client.execute(
            """
            SELECT
                category,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE user_id = ?
              AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total_amount DESC
            """,
            (user_id, start_date, end_date)
        )

        category_summary = [
            {
                "category": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in result.rows
        ]

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_expenses": summary[0],
            "total_amount": summary[1],
            "category_summary": category_summary
        }

    except Exception as e:
        logging.error(
            f"Database error while getting date range summary: {e}"
        )
        raise RuntimeError(
            f"Database error while getting date range summary: {e}"
        )

    finally:
        await client.close()

    

# Monthly Expense Report
async def get_monthly_expense_report(
    user_id: str,
    year: int,
    month: int
):
    """Get expense report for a specific month and user."""

    month_str = f"{month:02d}"
    start_date = f"{year}-{month_str}-01"

    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT
                COUNT(*) AS total_expenses,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM expenses
            WHERE user_id = ?
              AND date >= ?
              AND date < ?
            """,
            (user_id, start_date, end_date)
        )

        summary = result.rows[0]

        result = await client.execute(
            """
            SELECT
                category,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE user_id = ?
              AND date >= ?
              AND date < ?
            GROUP BY category
            ORDER BY total_amount DESC
            """,
            (user_id, start_date, end_date)
        )

        category_summary = [
            {
                "category": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in result.rows
        ]

        return {
            "year": year,
            "month": month,
            "total_expenses": summary[0],
            "total_amount": summary[1],
            "category_summary": category_summary
        }

    except Exception as e:
        logging.error(
            f"Database error while getting monthly expense report: {e}"
        )
        raise RuntimeError(
            f"Database error while getting monthly expense report: {e}"
        )

    finally:
        await client.close()
    


# Category Expense Report
async def get_category_expense_report(
    user_id: str,
    category: str
):
    """Get expense report for a specific category and user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT
                COUNT(*) AS expense_count,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM expenses
            WHERE user_id = ?
              AND category = ?
            """,
            (user_id, category)
        )

        summary = result.rows[0]

        result = await client.execute(
            """
            SELECT *
            FROM expenses
            WHERE user_id = ?
              AND category = ?
            ORDER BY date DESC, id DESC
            """,
            (user_id, category)
        )

        columns = result.columns

        expenses = [
            dict(zip(columns, row))
            for row in result.rows
        ]

        return {
            "category": category,
            "expense_count": summary[0],
            "total_amount": summary[1],
            "expenses": expenses
        }

    except Exception as e:
        logging.error(
            f"Database error while getting category expense report: {e}"
        )
        raise RuntimeError(
            f"Database error while getting category expense report: {e}"
        )

    finally:
        await client.close()
    


# Expense Statistics
async def get_expense_statistics(user_id: str):
    """Get expense statistics for a specific user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT
                COUNT(*) AS total_expenses,
                COALESCE(SUM(amount), 0) AS total_amount,
                COALESCE(AVG(amount), 0) AS average_expense,
                COALESCE(MAX(amount), 0) AS highest_expense,
                COALESCE(MIN(amount), 0) AS lowest_expense
            FROM expenses
            WHERE user_id = ?
            """,
            (user_id,)
        )

        row = result.rows[0]

        return {
            "total_expenses": row[0],
            "total_amount": row[1],
            "average_expense": row[2],
            "highest_expense": row[3],
            "lowest_expense": row[4]
        }

    except Exception as e:
        logging.error(
            f"Database error while getting expense statistics: {e}"
        )
        raise RuntimeError(
            f"Database error while getting expense statistics: {e}"
        )

    finally:
        await client.close()


# Budget Management
async def set_budget(
    user_id: str,
    category: str,
    monthly_limit: float
):
    """
    Create or update a monthly budget for a specific user.

    Each user can maintain an independent budget for the same
    category without affecting other users.

    Args:
        user_id: Unique identifier of the user.
        category: Expense category for which the budget is set.
        monthly_limit: Maximum amount allowed for the category
                       per month.

    Returns:
        A dictionary containing the user ID, category, and
        configured monthly budget.
    """

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        await client.batch([
            (
                """
                INSERT INTO budgets (
                    user_id,
                    category,
                    monthly_limit
                )
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, category)
                DO UPDATE SET
                    monthly_limit = excluded.monthly_limit
                """,
                (
                    user_id,
                    category,
                    monthly_limit
                )
            )
        ])

        return {
            "user_id": user_id,
            "category": category,
            "monthly_limit": monthly_limit
        }

    except Exception as e:
        logging.error(f"Database error while setting budget: {e}")
        raise RuntimeError(f"Database error while setting budget: {e}")

    finally:
        await client.close()
    

# Get Budgets function
async def get_budgets(user_id: str):
    """
    Get all monthly budgets for a specific user.

    Args:
        user_id: Unique identifier of the user whose budgets
                 should be retrieved.

    Returns:
        A list of the user's category budgets, including the
        category name and monthly spending limit.
    """

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT
                category,
                monthly_limit
            FROM budgets
            WHERE user_id = ?
            ORDER BY category
            """,
            (user_id,)
        )

        return [
            {
                "category": row[0],
                "monthly_limit": row[1]
            }
            for row in result.rows
        ]

    except Exception as e:
        logging.error(f"Database error while getting budgets: {e}")
        raise RuntimeError(f"Database error while getting budgets: {e}")

    finally:
        await client.close()


# Budget Status function
async def get_budget_status(
    user_id: str,
    category: str
):
    """
    Compare a user's monthly budget with their actual spending
    for a specific category.

    The calculation uses only the specified user's budget and
    expenses for the current calendar month.

    Args:
        user_id: Unique identifier of the user.
        category: Expense category whose budget status should
                  be checked.

    Returns:
        A dictionary containing the category budget, current
        monthly spending, remaining budget, and a message when
        no budget is configured.
    """

    from datetime import datetime

    current_date = datetime.now()

    year = current_date.year
    month = current_date.month

    month_str = f"{month:02d}"
    start_date = f"{year}-{month_str}-01"

    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT monthly_limit
            FROM budgets
            WHERE user_id = ?
              AND category = ?
            """,
            (user_id, category)
        )

        if not result.rows:
            return {
                "category": category,
                "budget": 0,
                "spent": 0,
                "remaining": 0,
                "message": "No budget set for this category."
            }

        budget_amount = result.rows[0][0]

        result = await client.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE user_id = ?
              AND category = ?
              AND date >= ?
              AND date < ?
            """,
            (user_id, category, start_date, end_date)
        )

        spent_amount = result.rows[0][0]
        remaining = budget_amount - spent_amount

        return {
            "category": category,
            "budget": budget_amount,
            "spent": spent_amount,
            "remaining": remaining
        }

    except Exception as e:
        logging.error(f"Database error while getting budget status: {e}")
        raise RuntimeError(f"Database error while getting budget status: {e}")

    finally:
        await client.close()


# Spending Alert function
async def get_spending_alert(
    user_id: str,
    category: str
):
    """
    Check whether a user's spending is approaching or exceeding
    the monthly budget for a specific category.

    An alert is generated when spending reaches 80% or more of
    the configured monthly budget.

    Args:
        user_id: Unique identifier of the user.
        category: Expense category whose spending should be
                  checked against its monthly budget.

    Returns:
        A dictionary containing the budget, amount spent,
        percentage used, alert status, and a descriptive message.
    """

    budget_status = await get_budget_status(
        user_id,
        category
    )

    budget = budget_status["budget"]
    spent = budget_status["spent"]

    if budget == 0:
        return {
            "category": category,
            "alert": False,
            "message": "No budget set for this category."
        }

    percentage_used = (spent / budget) * 100

    if percentage_used >= 100:
        message = "Budget exceeded."
        alert = True

    elif percentage_used >= 80:
        message = "You have used 80% or more of your budget."
        alert = True

    else:
        message = "Spending is within the budget."
        alert = False

    return {
        "category": category,
        "budget": budget,
        "spent": spent,
        "percentage_used": round(percentage_used, 2),
        "alert": alert,
        "message": message
    }


# Top Spending Categories function
async def get_top_spending_categories(
    user_id: str,
    limit: int = 5
):
    """
    Identify the top spending categories for a specific user.

    Categories are ranked by the total amount spent in each
    category, from highest to lowest.

    Args:
        user_id: Unique identifier of the user whose expenses
                 should be analyzed.
        limit: Maximum number of top categories to return.

    Returns:
        A list containing each category, the number of expenses,
        and the total amount spent in that category.
    """

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT
                category,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY total_amount DESC
            LIMIT ?
            """,
            (user_id, limit)
        )

        return [
            {
                "category": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in result.rows
        ]

    except Exception as e:
        logging.error(
            f"Database error while getting top spending categories: {e}"
        )
        raise RuntimeError(
            f"Database error while getting top spending categories: {e}"
        )

    finally:
        await client.close()


# Expense Insights function
async def get_expense_insights(user_id: str):
    """
    Get overall spending insights for a specific user.

    This combines the user's expense statistics with their
    highest-spending category.

    Args:
        user_id: Unique identifier of the user whose spending
                 insights should be analyzed.

    Returns:
        A dictionary containing total expenses, total amount,
        average expense, highest expense, lowest expense, and
        the user's top spending category.
    """

    statistics = await get_expense_statistics(user_id)

    categories = await get_top_spending_categories(
        user_id,
        limit=1
    )

    top_category = categories[0] if categories else None

    return {
        "total_expenses": statistics["total_expenses"],
        "total_amount": statistics["total_amount"],
        "average_expense": statistics["average_expense"],
        "highest_expense": statistics["highest_expense"],
        "lowest_expense": statistics["lowest_expense"],
        "top_category": top_category
    }


# Expense Trends function
async def get_expense_trends(user_id: str):
    """Get month-wise expense trends for a specific user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT
                strftime('%Y-%m', date) AS month,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE user_id = ?
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month
            """,
            (user_id,)
        )

        return [
            {
                "month": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in result.rows
        ]

    except Exception as e:
        logging.error(
            f"Database error while getting expense trends: {e}"
        )
        raise RuntimeError(
            f"Database error while getting expense trends: {e}"
        )

    finally:
        await client.close()


# Daily Spending Summary function
async def get_daily_spending_summary(user_id: str):
    """Get date-wise expense summary for a specific user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT
                date,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE user_id = ?
            GROUP BY date
            ORDER BY date DESC
            """,
            (user_id,)
        )

        return [
            {
                "date": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in result.rows
        ]

    except Exception as e:
        logging.error(
            f"Database error while getting daily spending summary: {e}"
        )
        raise RuntimeError(
            f"Database error while getting daily spending summary: {e}"
        )

    finally:
        await client.close()


async def get_payment_method_analysis(user_id: str):
    """Get expense analysis by payment method for a specific user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT
                payment_method,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE user_id = ?
              AND payment_method != ''
            GROUP BY payment_method
            ORDER BY total_amount DESC
            """,
            (user_id,)
        )

        return [
            {
                "payment_method": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in result.rows
        ]

    except Exception as e:
        logging.error(
            f"Database error while getting payment method analysis: {e}"
        )
        raise RuntimeError(
            f"Database error while getting payment method analysis: {e}"
        )

    finally:
        await client.close()
    

# Recurring Expenses function
async def get_recurring_expenses(user_id: str):
    """Detect recurring expenses for a specific user."""

    client = create_client(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

    try:
        result = await client.execute(
            """
            SELECT
                category,
                amount,
                COUNT(*) AS occurrence_count
            FROM expenses
            WHERE user_id = ?
            GROUP BY category, amount
            HAVING COUNT(*) >= 2
            ORDER BY occurrence_count DESC
            """,
            (user_id,)
        )

        return [
            {
                "category": row[0],
                "amount": row[1],
                "occurrence_count": row[2]
            }
            for row in result.rows
        ]

    except Exception as e:
        logging.error(
            f"Database error while detecting recurring expenses: {e}"
        )
        raise RuntimeError(
            f"Database error while detecting recurring expenses: {e}"
        )

    finally:
        await client.close()


# Financial Dashboard Summary function
async def get_financial_dashboard_summary(user_id: str):
    """
    Get a complete financial dashboard summary for a specific user.

    This combines key financial information including expense
    statistics, top spending categories, monthly spending trends,
    and budget information.

    Args:
        user_id: Unique identifier of the user whose financial
                 data should be summarized.

    Returns:
        A dictionary containing overall expense statistics,
        top spending categories, monthly trends, and the user's
        budgets.
    """

    statistics = await get_expense_statistics(user_id)
    top_categories = await get_top_spending_categories(user_id, limit=5)
    trends = await get_expense_trends(user_id)
    budgets = await get_budgets(user_id)

    return {
        "statistics": statistics,
        "top_categories": top_categories,
        "monthly_trends": trends,
        "budgets": budgets
    }



if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())

