"""
Migrate financial_ratios schema to add new ratio columns
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_financial_ratios_schema(db_path: str):
    """Add new columns to financial_ratios table"""
    logger.info(f"Opening database: {db_path}")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(financial_ratios)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    logger.info(f"Existing columns: {existing_columns}")
    
    new_columns = {
        'npm': 'REAL',
        'opm': 'REAL',
        'roe': 'REAL',
        'roa': 'REAL',
        'roce': 'REAL',
        'debt_to_equity': 'REAL',
        'icr': 'REAL',
        'asset_turnover': 'REAL',
        'fcf': 'REAL',
        'ocf_to_sales': 'REAL',
        'capex_intensity': 'REAL',
        'revenue_cagr_3yr': 'REAL',
        'revenue_cagr_5yr': 'REAL',
        'revenue_cagr_10yr': 'REAL',
        'pat_cagr_3yr': 'REAL',
        'pat_cagr_5yr': 'REAL',
        'pat_cagr_10yr': 'REAL',
        'eps_cagr_3yr': 'REAL',
        'eps_cagr_5yr': 'REAL',
        'eps_cagr_10yr': 'REAL',
        'capital_allocation': 'TEXT',
        'fcf_conversion': 'REAL'
    }
    
    # Add missing columns
    for col_name, col_type in new_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE financial_ratios ADD COLUMN {col_name} {col_type}")
                logger.info(f"Added column: {col_name}")
            except Exception as e:
                logger.error(f"Failed to add column {col_name}: {e}")
        else:
            logger.info(f"Column already exists: {col_name}")
    
    connection.commit()
    connection.close()
    logger.info("Migration complete")


if __name__ == '__main__':
    db_file = Path(__file__).parent / 'nifty100.db'
    migrate_financial_ratios_schema(str(db_file))
