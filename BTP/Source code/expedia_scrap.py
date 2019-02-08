# -*- coding: utf-8 -*-

from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import codecs

# GLOBAL VARIABLES THAT WILL STORE THE REVIEW, DATE OF REVIEW AND RATING
review = []
date = []
rating = []

# OPENING THE URL USING SELENIUM IN CHROME AND PASSING THE PAGE SOURCE TO SOUP
def get_response_from_server(url):
	try:
		# Defining the browser
		browser = webdriver.Chrome()
		browser.get(url)
		# Clicking on element to load user review's
		browser.find_element_by_xpath('.//*[@id="link-to-reviews"]').click()
		# Waiting for the reviews to load
		wait = WebDriverWait(browser, 13)

		while(True):
			# Wait time after we click 'Next' button of review list every time
			time.sleep(15)
			# Store page source into a string variable
			page = browser.page_source
			# Passing the page source to BeautifulSoup
			soup=BeautifulSoup(page, 'html.parser')
			# Calling the main function to extract the details of review
			scrap_logic(soup)

			# Logic to keep loading new reviews until no new reviews can be loaded
			# Each block of reviews are processed and then next button is clicked
			try:
				element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'pagination-next')))
				print(element)
				element.click()
			except:
				break

	except Exception as e:
		print ("Error Occured")
		print (e)
		return

def scrap_logic(soup):
	# Getting details from the page
	detail = soup.find_all('div', {'class': 'details'})
	dt = soup.find_all('div', {'class': 'date-posted'})
	x = 0
	for tag in detail:
		rvtxt = tag.find('span', {'class': 'translate-text'})
		# If review text is empty then, we do not fetch date and rating for that review
		if rvtxt == None:
			x += 1
			continue
		review.append(rvtxt.get_text())
		
		rtsc = tag.find('span', {'class': 'badge badge-notification rating-score left'})
		rating.append(rtsc.get_text())

		tmp = dt[x].get_text().split()
		date.append(' '.join(word for word in tmp))
		x += 1

if __name__=="__main__" :
	# URL of hotel for which details have to be fetched
	url = "https://www.expedia.com/Madrid-Hotels-Courtyard-By-Marriott-Madrid-Princesa.h24814.Hotel-Information?chkin=11/8/2018&chkout=11/12/2018&rm1=a2&misId=cabbd6d0-0c47-447f-8855-c4af66736601&sort=recommended&hwrqCacheKey=e8348406-2206-4589-b0b9-2031be8b4c4eHWRQ1538244936940&cancellable=false&regionId=178281&vip=false&c=d3ceb056-5375-4e47-a507-450c025b68fd&packageType=fh&exp_dp=1258.06&exp_ts=1538225125302&exp_curr=USD&swpToggleOn=false&exp_pg=HSR&inttkn=EZavZHGtCkqlWhKP"
	get_response_from_server(url)

	print ("Total reviews are")
	print (len(review), len(date))

	# Writing results to a text file
	with codecs.open("output.txt", "w", encoding="utf-8") as thefile:
		for x in range(len(review)):
			thefile.write("%s\n" % date[x].decode("utf-8"))
			thefile.write("%s\n" % rating[x].decode("utf-8"))
			thefile.write("%s\n\n" % review[x])
	thefile.close()
