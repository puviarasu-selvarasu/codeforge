# apps/chat/router.py
import re
from datetime import datetime, timedelta

class SmartRouter:
    @staticmethod
    def handle(query):
        query = query.lower().strip()
        
        # Greetings
        if re.match(r'^(hi|hello|hey|good morning|good evening|what\'s up)', query):
            return True, "Hello! I'm CodeForge, your AI developer studio. How can I help you build something today?"
        
        # Time – more flexible
        if re.search(r'what.*time', query) or re.search(r'time now', query):
            now = datetime.now().strftime('%I:%M %p')
            return True, f"The current time is {now}."
        
        # Date
        if re.search(r'what.*date', query) or re.search(r'today\'?s date', query):
            today = datetime.now().strftime('%B %d, %Y')
            return True, f"Today is {today}."
        
        # Relative date – we'll keep simple; for complex, we'll rely on LLM
        # (to avoid dateutil dependency)
        match = re.match(r'^what (was|is|will be) (\d+) (day|days|month|months|year|years) (ago|from now)', query)
        if match:
            amount = int(match.group(2))
            unit = match.group(3).rstrip('s')
            direction = match.group(4)
            today = datetime.now()
            if unit == 'day':
                delta = timedelta(days=amount)
            elif unit == 'month':
                # approximate – we'll skip for now or use timedelta(days=30*amount)
                # better to rely on LLM for such complex queries
                return False, None
            elif unit == 'year':
                # approximate
                return False, None
            else:
                return False, None
            if direction == 'ago':
                result_date = today - delta
            else:
                result_date = today + delta
            return True, f"That date is {result_date.strftime('%B %d, %Y')}."
        
        return False, None