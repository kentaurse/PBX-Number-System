from Phones import Scraper

url = 'http://10.183.9.58'
userId = '10'
password = '0000'
asr = Scraper(url, userId, password)
asr.go_to_voicemail()
records = asr.get_recent_records()
while True:
    asr.refresh_page()
    records = asr.get_recent_records()