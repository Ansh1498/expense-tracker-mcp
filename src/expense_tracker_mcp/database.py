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




if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())

