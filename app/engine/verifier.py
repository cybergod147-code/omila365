import re
import dns.resolver

class EmailVerifier:
    @staticmethod
    def verify(email):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return {'email': email, 'status': 'invalid', 'score': 0}
        domain = email.split('@')[1]
        try:
            dns.resolver.resolve(domain, 'MX')
            has_mx = True
        except:
            has_mx = False
        if not has_mx:
            return {'email': email, 'status': 'invalid', 'score': 10}
        disposable = ['mailinator.com', 'guerrillamail.com', 'tempmail.com', '10minutemail.com']
        if domain in disposable:
            return {'email': email, 'status': 'invalid', 'score': 20}
        return {'email': email, 'status': 'valid', 'score': 80}
    
    @staticmethod
    def verify_batch(emails):
        results = {'valid': [], 'invalid': []}
        for email in emails:
            res = EmailVerifier.verify(email)
            if res['status'] == 'valid':
                results['valid'].append(res)
            else:
                results['invalid'].append(res)
        return results 
