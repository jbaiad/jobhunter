import datetime

from bs4 import BeautifulSoup

class AngelScraper():
	INIT_DATA = 'data/angel_software_eng_nyc_init.html'
	INIT_DATE = datetime.datetime(2020, 3, 29)

	@classmethod
	def init_scrape(cls) -> list:
		f = open(cls.INIT_DATA, "r")
		soup = BeautifulSoup(f.read(), features ='html.parser')
		postings = soup.find_all('div', attrs={'class':'component_504ac'})
		jobs = []

		for posting in postings:
			title_div = posting.find('div', attrs={'class':'component_70e43'})
			listings = posting.find_all('div', attrs={'class':'listing_4d13a'})

			company_name = title_div.find_all('a')[1].text
			company_url = title_div.find_all('a')[1].get('href')
			company_desc = title_div.find_all('span')[0].text
			company_size = title_div.find_all('span')[1].text

			job_listings = []
			for listing in listings:
				name = listing.find_all('span')[0].text
				url = listing.a.get('href')
				location = listing.find_all('span')[1].text.split("•")[0]
				salary = listing.find('span', attrs={'class':'salaryEstimate_ae61f'}).text.split("•")[0]
				date = listing.find('span', attrs={'class':'posted_1e3fd'})
				date = date.text if date != None else None
				job_listings.append({"name" : name, "url" : url, "location": location, "salary": salary, "date": date})
			jobs.append({"name": company_name, "url": company_url, "desc" : company_desc, "size" : company_size, "listings" : job_listings})
		return jobs


jobs = AngelScraper().init_scrape()
print(len(jobs))
print(jobs[-2])

__all__ = ['AngelScraper']
