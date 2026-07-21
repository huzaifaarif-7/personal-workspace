import os

def fix_calendar():
    with open('server/calendar.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'get_current_user' not in content:
        content = content.replace('from . import data', 'from . import data\nfrom fastapi import Depends\nfrom .deps import get_current_user\nfrom .models import User')
        
        content = content.replace('def events(): return data.calendar_events()', 'def events(user: User = Depends(get_current_user)): return data.calendar_events()')
        content = content.replace('def today(): return data.today_events()', 'def today(user: User = Depends(get_current_user)): return data.today_events()')
        content = content.replace('def create_event(body: schemas.CreateEventRequest): return data.create_event(body)', 'def create_event(body: schemas.CreateEventRequest, user: User = Depends(get_current_user)): return data.create_event(body)')
        
        with open('server/calendar.py', 'w', encoding='utf-8') as f:
            f.write(content)

def fix_email():
    with open('server/email.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'get_current_user' not in content:
        content = content.replace('from . import data', 'from . import data\nfrom fastapi import Depends\nfrom .deps import get_current_user\nfrom .models import User')
        
        content = content.replace('def messages(): return data.emails()', 'def messages(user: User = Depends(get_current_user)): return data.emails()')
        content = content.replace('def important(): return [e for e in data.emails() if e.important]', 'def important(user: User = Depends(get_current_user)): return [e for e in data.emails() if e.important]')
        
        with open('server/email.py', 'w', encoding='utf-8') as f:
            f.write(content)

fix_calendar()
fix_email()
