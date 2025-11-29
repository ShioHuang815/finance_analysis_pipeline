"""
State management for tracking ingestion runs and watermarks
"""
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


def generate_run_id() -> str:
    """Generate a unique run ID for tracking data loads."""
    return f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def create_run_metadata(
    dataset_name: str,
    status: str = "started",
    records_loaded: int = 0,
    error_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create metadata record for an ingestion run.
    
    Args:
        dataset_name: Name of the dataset being loaded
        status: Run status (started, completed, failed)
        records_loaded: Number of records loaded
        error_message: Error message if status is failed
    
    Returns:
        Dictionary with run metadata
    """
    return {
        'run_id': generate_run_id(),
        'dataset_name': dataset_name,
        'run_timestamp': datetime.now(),
        'status': status,
        'records_loaded': records_loaded,
        'error_message': error_message
    }
