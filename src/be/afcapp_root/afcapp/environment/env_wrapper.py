# Source - https://stackoverflow.com/a
# Posted by ParisNakitaKejser, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-17, License - CC BY-SA 4.0

import os
from dotenv import load_dotenv

load_dotenv()

conn_str = os.getenv('SQL_CONN_STR')

# print(conn_str)

class EnvReader:

    def __init__(self):
       self.conn_str = conn_str
       
     