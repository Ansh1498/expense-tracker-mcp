import aiosqlite
import os
from datetime import datetime


# SQLite database file
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "expenses.db"
)


async def init_db():
    """Create the expenses table if it doesn't exist."""

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

        await db.commit()

    print("Database initialized successfully.")

# Add Expense function
async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    description: str = "",
    payment_method: str = ""
):
    """Add a new expense to the database."""

    now = datetime.now().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            INSERT INTO expenses (
                date,
                amount,
                category,
                subcategory,
                description,
                payment_method,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
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

# List Expenses function
async def list_expenses():
    """Get all expenses from the database."""

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM expenses
            ORDER BY date DESC, id DESC
            """
        )

        rows = await cursor.fetchall()

        return [dict(row) for row in rows]

# Update Expense function
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
            WHERE id = ?
            """,
            (
                date,
                amount,
                category,
                subcategory,
                description,
                payment_method,
                now,
                expense_id
            )
        )

        await db.commit()

        return cursor.rowcount

# Delete Expense function
async def delete_expense(expense_id: int):
    """Delete an expense by its ID."""

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            DELETE FROM expenses
            WHERE id = ?
            """,
            (expense_id,)
        )

        await db.commit()

        return cursor.rowcount

# Search Expenses function
async def search_expenses(keyword: str):
    """Search expenses by category, subcategory, description, or payment method."""

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        search_term = f"%{keyword}%"

        cursor = await db.execute(
            """
            SELECT *
            FROM expenses
            WHERE
                category LIKE ?
                OR subcategory LIKE ?
                OR description LIKE ?
                OR payment_method LIKE ?
            ORDER BY date DESC, id DESC
            """,
            (
                search_term,
                search_term,
                search_term,
                search_term
            )
        )

        rows = await cursor.fetchall()

        return [dict(row) for row in rows]
    

# Get Expense function
async def get_expense(expense_id: int):
    """Get a single expense by its ID."""

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM expenses
            WHERE id = ?
            """,
            (expense_id,)
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





if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())

