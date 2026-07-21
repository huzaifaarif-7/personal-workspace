import re

with open('server/schemas.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure Field is imported
if 'from pydantic import BaseModel, EmailStr' in content and 'Field' not in content:
    content = content.replace('from pydantic import BaseModel, EmailStr', 'from pydantic import BaseModel, EmailStr, Field')

# Let's just do a regex replace for `str` type fields in schemas.py
# Wait, it's safer to just rewrite schemas.py replacing basic str with Field(..., max_length=100) or similar.
# Actually I can replace specific lines:
content = content.replace('name: str', 'name: str = Field(..., max_length=100)')
content = content.replace('password: str', 'password: str = Field(..., max_length=128)')
content = content.replace('description: str', 'description: str = Field(..., max_length=500)')
content = content.replace('sender: str', 'sender: str = Field(..., max_length=100)')
content = content.replace('channel: Optional[str] = None', 'channel: Optional[str] = Field(None, max_length=100)')
content = content.replace('text: str', 'text: str = Field(..., max_length=2000)')
content = content.replace('title: str', 'title: str = Field(..., max_length=200)')
content = content.replace('location: Optional[str] = None', 'location: Optional[str] = Field(None, max_length=200)')
content = content.replace('meet_link: Optional[str] = None', 'meet_link: Optional[str] = Field(None, max_length=500)')
content = content.replace('invitee: str', 'invitee: str = Field(..., max_length=100)')
content = content.replace('when: str', 'when: str = Field(..., max_length=100)')
content = content.replace('duration: str', 'duration: str = Field(..., max_length=50)')
content = content.replace('actor: str', 'actor: str = Field(..., max_length=100)')
content = content.replace('action: str', 'action: str = Field(..., max_length=100)')
content = content.replace('repo: str', 'repo: str = Field(..., max_length=200)')
content = content.replace('message: str', 'message: str = Field(..., max_length=1000)')
content = content.replace('subject: str', 'subject: str = Field(..., max_length=300)')
content = content.replace('preview: str', 'preview: str = Field(..., max_length=500)')
content = content.replace('content: str', 'content: str = Field(..., max_length=4000)')
content = content.replace('reply: str', 'reply: str = Field(..., max_length=4000)')
# Fix the assistant query message
content = content.replace('    message: str\n', '    message: str = Field(..., max_length=1000)\n')

with open('server/schemas.py', 'w', encoding='utf-8') as f:
    f.write(content)
