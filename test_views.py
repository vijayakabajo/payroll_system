import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()
from django.test import Client
c = Client()
session = c.session
session['pin_authenticated'] = True
session.save()

urls = ['/dashboard/', '/employees/', '/employees/add/']
for url in urls:
    resp = c.get(url, SERVER_NAME='localhost')
    print(url, resp.status_code)
    if resp.status_code == 500:
        print('Exception found in', url)
        # Parse traceback from resp.content
        import re
        content = resp.content.decode('utf-8', errors='ignore')
        # We can just look for the Exception Type and Value
        import bs4
        try:
            soup = bs4.BeautifulSoup(content, 'html.parser')
            print("Exception Type:", soup.find('th', string='Exception Type:').find_next_sibling('td').text.strip())
            print("Exception Value:", soup.find('th', string='Exception Value:').find_next_sibling('td').text.strip())
            print("Exception Location:", soup.find('th', string='Exception Location:').find_next_sibling('td').text.strip())
        except Exception:
            # Fallback
            m = re.search(r'(?s)<div id="traceback_area".*?>(.*?)</div>', content)
            if m:
                print(m.group(1)[:1000])
            else:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'Exception Type:' in line or 'Exception Value:' in line:
                        print(line)
