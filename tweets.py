# Importando Bibliotecas Necessárias:
import os, pandas as pd
from datetime import datetime, timedelta

os.system('snscrape --jsonl --progress --max-results 3000000 twitter-hashtag bitcoin > tweetsz.json')
