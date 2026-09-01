# keyword_engine.py - Manage custom keywords for sorting and monitoring
from app import db
from app.models import KeywordRule  # we need to add this model later

class KeywordEngine:
    # Default built‑in keywords (Kali365 style)
    DEFAULT_KEYWORDS = {
        'invoice': ['invoice', 'bill', 'payment due', 'overdue', 'receipt'],
        'payment': ['wire transfer', 'ach', 'bank account', 'routing', 'payment'],
        'financial': ['payroll', 'salary', 'bonus', 'commission', 'reimbursement'],
        'contract': ['contract', 'agreement', 'signed', 'legal', 'terms'],
        'internal': ['internal', 'confidential', 'staff', 'employee', 'hr'],
        'urgent': ['urgent', 'immediate', 'asap', 'deadline', 'critical']
    }

    def __init__(self, tenant_id=None):
        self.tenant_id = tenant_id
        self.custom_keywords = self._load_custom()

    def _load_custom(self):
        """Load tenant‑specific custom keywords from DB"""
        if self.tenant_id is None:
            return {}
        # Query the KeywordRule model (if you add it to models.py)
        # For now, we'll just return an empty dict.
        # You can extend this later.
        return {}

    def get_all_keywords(self):
        """Merge default and custom keywords"""
        all_rules = dict(self.DEFAULT_KEYWORDS)
        # Add custom rules (if any) – placeholder
        # for category, words in self.custom_keywords.items():
        #    all_rules.setdefault(category, []).extend(words)
        return all_rules

    def add_custom_keyword(self, category, keyword, user_id):
        """Add a new keyword for monitoring (stub – needs KeywordRule model)"""
        # This would save to the database. For now, print it.
        print(f"Added keyword '{keyword}' to category '{category}' (user {user_id})")
        return True 
