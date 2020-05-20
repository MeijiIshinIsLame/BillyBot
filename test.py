from datetime import datetime
from datetime import timedelta 
from pytz import timezone
import time

def time_status():
	while True:
		last_updated = datetime.now(timezone('US/Hawaii'))
		if int(last_updated.strftime("%H")) > 12:
			last_updated = last_updated - timedelta(hours=12)
			print(last_updated.strftime("%H:%M PM"))
		else:
			print(last_updated.strftime("%H:%M AM"))
		time.sleep(5)

time_status()