import aiosqlite
import os
import logging
from datetime import datetime


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



# SQLite database file
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "expenses.db"
)


async def init_db():
    """Create the expenses table and apply database migrations."""

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                description TEXT DEFAULT '',
                payment_method TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Check existing columns
        cursor = await db.execute("PRAGMA table_info(expenses)")
        columns = await cursor.fetchall()

        column_names = [column[1] for column in columns]

        # Add user_id for existing databases
        if "user_id" not in column_names:
            await db.execute("""
                ALTER TABLE expenses
                ADD COLUMN user_id TEXT DEFAULT 'default_user'
            """)

        await db.commit()

    print("Database initialized successfully.")

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
    """Add a new expense to the database."""

    validate_expense(date, amount, category)

    try:
        now = datetime.now().isoformat()

        async with aiosqlite.connect(DB_PATH) as db:

            cursor = await db.execute(
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

            await db.commit()

            return cursor.lastrowid

    except aiosqlite.Error as e:
        logging.error(f"Database error while adding expense: {e}")
        raise RuntimeError(f"Database error while adding expense: {e}")


# List Expenses function
async def list_expenses(user_id: str):
    """Get all expenses for a specific user."""

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC, id DESC
            """,
            (user_id,)
        )

        rows = await cursor.fetchall()

        return [dict(row) for row in rows]



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
    """Update an existing expense."""

    validate_expense(date, amount, category)

    try:
        now = datetime.now().isoformat()

        async with aiosqlite.connect(DB_PATH) as db:

            cursor = await db.execute(
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

            await db.commit()

            return cursor.rowcount

    except aiosqlite.Error as e:
        logging.error(f"Database error while updating expense: {e}")
        raise RuntimeError(f"Database error while updating expense: {e}")


# Delete Expense function
async def delete_expense(user_id: str, expense_id: int):
    """Delete an expense by its ID for a specific user."""

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            DELETE FROM expenses
            WHERE id = ? AND user_id = ?
            """,
            (expense_id, user_id)
        )

        await db.commit()

        return cursor.rowcount
    

# Search Expenses function
async def search_expenses(user_id: str, keyword: str):
    """Search expenses by category, subcategory, description, or payment method."""

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        search_term = f"%{keyword}%"

        cursor = await db.execute(
            """
            SELECT *
            FROM expenses
            WHERE
                user_id = ?
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

        rows = await cursor.fetchall()

        return [dict(row) for row in rows]

# Get Expense function
async def get_expense(user_id: str, expense_id: int):
    """Get a single expense by its ID."""

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM expenses
            WHERE id = ? AND user_id = ?
            """,
            (expense_id, user_id)
        )

        row = await cursor.fetchone()

        if row is None:
            return None

        return dict(row)



# Expense Summary function
async def get_expense_summary():
    """Get expense summary and category-wise totals."""

    async with aiosqlite.connect(DB_PATH) as db:

        # Total expenses and total amount
        cursor = await db.execute(
            """
            SELECT
                COUNT(*) AS total_expenses,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM expenses
            """
        )

        summary = await cursor.fetchone()

        # Category-wise total
        cursor = await db.execute(
            """
            SELECT
                category,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            GROUP BY category
            ORDER BY total_amount DESC
            """
        )

        rows = await cursor.fetchall()

        category_summary = [
            {
                "category": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in rows
        ]

        return {
            "total_expenses": summary[0],
            "total_amount": summary[1],
            "category_summary": category_summary
        }


# Date Range Expense Summary
async def get_expense_summary_by_date(
    start_date: str,
    end_date: str
):
    """Get expense summary for a specific date range."""

    async with aiosqlite.connect(DB_PATH) as db:

        # Total expenses and total amount
        cursor = await db.execute(
            """
            SELECT
                COUNT(*) AS total_expenses,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """,
            (start_date, end_date)
        )

        summary = await cursor.fetchone()

        # Category-wise summary
        cursor = await db.execute(
            """
            SELECT
                category,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total_amount DESC
            """,
            (start_date, end_date)
        )

        rows = await cursor.fetchall()

        category_summary = [
            {
                "category": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in rows
        ]

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_expenses": summary[0],
            "total_amount": summary[1],
            "category_summary": category_summary
        }

# Monthly Expense Report
async def get_monthly_expense_report(
    year: int,
    month: int
):
    """Get expense report for a specific month."""

    month_str = f"{month:02d}"
    start_date = f"{year}-{month_str}-01"

    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                COUNT(*) AS total_expenses,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM expenses
            WHERE date >= ? AND date < ?
            """,
            (start_date, end_date)
        )

        summary = await cursor.fetchone()

        cursor = await db.execute(
            """
            SELECT
                category,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE date >= ? AND date < ?
            GROUP BY category
            ORDER BY total_amount DESC
            """,
            (start_date, end_date)
        )

        rows = await cursor.fetchall()

        category_summary = [
            {
                "category": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in rows
        ]

        return {
            "year": year,
            "month": month,
            "total_expenses": summary[0],
            "total_amount": summary[1],
            "category_summary": category_summary
        }


# Category Expense Report
async def get_category_expense_report(category: str):
    """Get expense report for a specific category."""

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT
                COUNT(*) AS expense_count,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM expenses
            WHERE category = ?
            """,
            (category,)
        )

        summary = await cursor.fetchone()

        cursor = await db.execute(
            """
            SELECT *
            FROM expenses
            WHERE category = ?
            ORDER BY date DESC, id DESC
            """,
            (category,)
        )

        rows = await cursor.fetchall()

        return {
            "category": category,
            "expense_count": summary["expense_count"],
            "total_amount": summary["total_amount"],
            "expenses": [dict(row) for row in rows]
        }


# Expense Statistics
async def get_expense_statistics():
    """Get overall expense statistics."""

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                COUNT(*) AS total_expenses,
                COALESCE(SUM(amount), 0) AS total_amount,
                COALESCE(AVG(amount), 0) AS average_expense,
                COALESCE(MAX(amount), 0) AS highest_expense,
                COALESCE(MIN(amount), 0) AS lowest_expense
            FROM expenses
            """
        )

        row = await cursor.fetchone()

        return {
            "total_expenses": row[0],
            "total_amount": row[1],
            "average_expense": row[2],
            "highest_expense": row[3],
            "lowest_expense": row[4]
        }


# Budget Management
async def set_budget(
    category: str,
    monthly_limit: float
):
    """Set or update a monthly budget for a category."""

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                monthly_limit REAL NOT NULL
            )
            """
        )

        await db.execute(
            """
            INSERT INTO budgets (category, monthly_limit)
            VALUES (?, ?)
            ON CONFLICT(category)
            DO UPDATE SET monthly_limit = excluded.monthly_limit
            """,
            (category, monthly_limit)
        )

        await db.commit()

        return {
            "category": category,
            "monthly_limit": monthly_limit
        }

# Get Budgets function
async def get_budgets():
    """Get all category budgets."""

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                monthly_limit REAL NOT NULL
            )
            """
        )

        cursor = await db.execute(
            """
            SELECT category, monthly_limit
            FROM budgets
            ORDER BY category
            """
        )

        rows = await cursor.fetchall()

        return [
            {
                "category": row[0],
                "monthly_limit": row[1]
            }
            for row in rows
        ]


# Budget Status function
async def get_budget_status(category: str):
    """Compare monthly budget with actual spending."""

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

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT monthly_limit
            FROM budgets
            WHERE category = ?
            """,
            (category,)
        )

        budget = await cursor.fetchone()

        if budget is None:
            return {
                "category": category,
                "budget": 0,
                "spent": 0,
                "remaining": 0,
                "message": "No budget set for this category."
            }

        cursor = await db.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE category = ?
            AND date >= ?
            AND date < ?
            """,
            (category, start_date, end_date)
        )

        spent = await cursor.fetchone()

        budget_amount = budget[0]
        spent_amount = spent[0]
        remaining = budget_amount - spent_amount

        return {
            "category": category,
            "budget": budget_amount,
            "spent": spent_amount,
            "remaining": remaining
        }


# Spending Alert function
async def get_spending_alert(category: str):
    """Check whether spending is approaching or exceeding the budget."""

    budget_status = await get_budget_status(category)

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
async def get_top_spending_categories(limit: int = 5):
    """Get top spending categories by total amount."""

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                category,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            GROUP BY category
            ORDER BY total_amount DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = await cursor.fetchall()

        return [
            {
                "category": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in rows
        ]


# Expense Insights function
async def get_expense_insights():
    """Get overall spending insights."""

    statistics = await get_expense_statistics()
    categories = await get_top_spending_categories(limit=1)

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
async def get_expense_trends():
    """Get month-wise expense trends."""

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                strftime('%Y-%m', date) AS month,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month
            """
        )

        rows = await cursor.fetchall()

        return [
            {
                "month": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in rows
        ]


# Daily Spending Summary function
async def get_daily_spending_summary():
    """Get date-wise expense summary."""

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                date,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            GROUP BY date
            ORDER BY date DESC
            """
        )

        rows = await cursor.fetchall()

        return [
            {
                "date": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in rows
        ]


async def get_payment_method_analysis():
    """Get expense analysis by payment method."""

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                payment_method,
                COUNT(*) AS expense_count,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE payment_method != ''
            GROUP BY payment_method
            ORDER BY total_amount DESC
            """
        )

        rows = await cursor.fetchall()

        return [
            {
                "payment_method": row[0],
                "expense_count": row[1],
                "total_amount": row[2]
            }
            for row in rows
        ]


# Recurring Expenses function
async def get_recurring_expenses():
    """Detect recurring expenses based on same category and amount."""

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                category,
                amount,
                COUNT(*) AS occurrence_count
            FROM expenses
            GROUP BY category, amount
            HAVING COUNT(*) >= 2
            ORDER BY occurrence_count DESC
            """
        )

        rows = await cursor.fetchall()

        return [
            {
                "category": row[0],
                "amount": row[1],
                "occurrence_count": row[2]
            }
            for row in rows
        ]


# Financial Dashboard Summary function
async def get_financial_dashboard_summary():
    """Get a complete financial dashboard summary."""

    statistics = await get_expense_statistics()
    top_categories = await get_top_spending_categories(limit=5)
    trends = await get_expense_trends()
    budgets = await get_budgets()

    return {
        "statistics": statistics,
        "top_categories": top_categories,
        "monthly_trends": trends,
        "budgets": budgets
    }



if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())

