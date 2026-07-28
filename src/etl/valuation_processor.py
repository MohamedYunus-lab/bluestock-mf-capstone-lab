"""
Valuation Batch Processor - Generate valuation outputs
Day 26: Valuation module processor for output generation
"""

import logging
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from analytics.valuation import generate_valuation_summary, generate_valuation_flags

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_valuation_processor(year: int = 2023, output_dir: str = None):
    """
    Run valuation processor for given year
    
    Args:
        year: Fiscal year to process
        output_dir: Output directory (default: ./output)
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
    
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Starting valuation processor for FY {year}")
    
    try:
        # Generate valuation summary
        summary_path = os.path.join(output_dir, f'valuation_summary_{year}.xlsx')
        logger.info(f"Generating valuation summary: {summary_path}")
        
        summary_df = generate_valuation_summary(year, summary_path)
        logger.info(f"✓ Valuation summary: {len(summary_df)} companies processed")
        
        # Generate valuation flags
        flags_path = os.path.join(output_dir, f'valuation_flags_{year}.csv')
        logger.info(f"Generating valuation flags: {flags_path}")
        
        flags_df = generate_valuation_flags(year, flags_path)
        logger.info(f"✓ Valuation flags: {len(flags_df)} flagged companies")
        
        # Summary stats
        caution_count = len(flags_df[flags_df['Valuation Flag'] == 'Caution'])
        discount_count = len(flags_df[flags_df['Valuation Flag'] == 'Discount'])
        fair_count = len(summary_df[summary_df['Valuation Flag'] == 'Fair'])
        
        logger.info(f"\nValuation Summary:")
        logger.info(f"  Total Companies: {len(summary_df)}")
        logger.info(f"  Fair Valued: {fair_count}")
        logger.info(f"  Caution (Overvalued): {caution_count}")
        logger.info(f"  Discount (Undervalued): {discount_count}")
        logger.info(f"\nOutput Files:")
        logger.info(f"  Summary: {summary_path}")
        logger.info(f"  Flags: {flags_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error in valuation processor: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    import sys
    
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2023
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = run_valuation_processor(year, output_dir)
    sys.exit(0 if success else 1)
