class EmailSorter:
    PROVIDER_DOMAINS = {
        'gmail': ['gmail.com', 'googlemail.com'],
        'outlook': ['outlook.com', 'hotmail.com', 'live.com', 'msn.com'],
        'office365': ['office365.com', 'microsoft.com', 'exchange.com'],
        'yahoo': ['yahoo.com', 'ymail.com', 'rocketmail.com'],
        'icloud': ['icloud.com', 'me.com', 'mac.com'],
        'godaddy': ['godaddy.com', 'secureserver.net'],
        'protonmail': ['protonmail.com', 'proton.me'],
        'zoho': ['zoho.com', 'zohomail.com'],
        'other': []
    }
    
    @classmethod
    def classify(cls, email):
        try:
            domain = email.split('@')[1].lower()
        except:
            return 'other'
        for provider, domains in cls.PROVIDER_DOMAINS.items():
            if any(domain == d or domain.endswith('.' + d) for d in domains):
                return provider
        return 'other'
    
    @classmethod
    def sort_batch(cls, emails):
        groups = {p: [] for p in cls.PROVIDER_DOMAINS.keys()}
        for email in emails:
            provider = cls.classify(email)
            groups[provider].append(email)
        return groups 
