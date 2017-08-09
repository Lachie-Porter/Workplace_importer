import requests
import os
from bs4 import BeautifulSoup

def main():
	text = findSiteText()
	lines = extractShiftInfo(text)
	printShifts(lines)

def findSiteText():
	"finds the raw text of the logged in work site"
	#store the details we need to login to workplace online
	#removed details for public repo
    payload = {
        "account" : "...",
        "username": "...",
        "password": "...",
        "task": "..."
    }

	#https://www.quora.com/What-is-the-best-way-to-log-in-to-a-website-using-Python
	# -- Kashyap Raval reply, Aug 6 (accessed 20/1/2017)
	#This logs into page using data set up above using sesson and post
	with requests.Session() as s:
		p = s.post('https://champions.workplaceonline.com.au/c2/signin/', data=payload)
		#use beautiful soup to find the relevant shift times
		soup = BeautifulSoup(p.text, "html.parser")

	
	#find all the text in the page
	return soup.text

def extractShiftInfo(text):
	"finds the relivant shift information from the websites text information. Returns a list of strings containing shift data"
	#split the page into sections 
	#NOTE: did this through string manipulation as bs4 was being weird and only returning two table rows
	#EG everything after My Shifts but before Calendar
	sections = text.split('My Shifts')
	shifts = sections[1].split('Calendar')[0]

	#divide shift information into lines
	lines = shifts.split('\n')
	return lines

def printShifts(lines):
	"Prints the shift information passed to it by lines"
	print("Your Shifts this week are:")
	for line in lines:
		if line.strip():
			print(line)




if __name__ == '__main__':
    main()

os.system("pause")