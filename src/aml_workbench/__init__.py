"""AML Transaction Monitoring Workbench foundation.

Synthetic scenario labels are test ground truth only. They are not findings about
real people, accounts, transactions, or suspicious activity.
"""

from aml_workbench.database import create_connection, load_synthetic_data
from aml_workbench.synthetic import generate_synthetic_data

__all__ = ["create_connection", "generate_synthetic_data", "load_synthetic_data"]
