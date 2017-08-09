import requests
import os
import datetime
import time
from bs4 import BeautifulSoup
from OAuth_cal import getFutureEvents, insertEvent

def main():
    print("Updating calendar with any new shifts")
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
    text = soup.text
    
    #split the page into sections 
    #NOTE: did this through string manipulation as bs4 was being weird and only returning two table rows
    #EG everything after My Shifts but before Calendar
    sections = text.split('My Shifts')
    shifts = sections[1].split('Calendar')[0]

    #divide shift information into lines
    lines = shifts.split('\n')

    #set up a dictionary to create the events with 
    times = parseShiftStringToDateTime(lines)

    loadWorkEvents(times)

def parseShiftStringToDateTime(lines):
    "Turns the string lines into a dictionary startTime : endTime"
    #input is in the form of:
    #
    #Tomorrow           <-- date line
    #2:00PM-8:00PM      <-- time line
    #26/02
    #5:00PM-8:00PM
    #
    #this will return a dictionary like (date of writing is 24/02/2017):
    #{
    #   2017-02-25T14:00 : 2017-02-25T20:00
    #   2017-02-26T17:00 : 2017-02-26T20:00 
    #}

    #Get the current year
    CURRENT_YEAR = datetime.date.today().strftime("%Y")

    shiftData = {}
    for line in lines:
        #if the line is not whiteSpace (no data)
        if line.strip():
            #find out if this is a date or time line
            shiftTimes = line.split('-')
            if(len(shiftTimes) == 1):
                #must be date line since no '-' present
                if(line == 'Tomorrow'):
                    #calculate tomorrow's date by adding one day to today 
                    line = datetime.date.today() + datetime.timedelta(days=1)
                    line = str(line)
                elif(line == 'Today'):
                    line = datetime.date.today()
                    line = str(line)
                else: #26/02 into 2017-02-26
                    #format string in the correct form
                    line = CURRENT_YEAR + '-' + line
                    line = line.replace('/', '-')
                    line = dateFormat(line)
                #store this date for use on the next loop (time line)
                shiftDate = line
            else:
                #must be time line
                start = shiftDate + ' ' + shiftTimes[0]
                end = shiftDate + ' ' + shiftTimes[1]
                start =datetime.datetime.strptime(start, "%Y-%m-%d %I:%M%p")
                start = start.isoformat()
                end = datetime.datetime.strptime(end, "%Y-%m-%d %I:%M%p")
                end = end.isoformat()
                shiftData.update({start : end})
    return shiftData

def dateFormat(string):
    "formats a date from (year/day/month) to (year/month/day) assuming perfect input"
    #for use to turn 
    #2017-26-02 (year/day/month)
    #into
    #2017-02-26 (year/month/day) <-- standard format
    #
    #kinda hacky but its just for me so meh
    #WARNING: ASSUMES PERFECT INPUT IN FORM ABOVE
    temp1 = string[5]
    temp2 = string[6]

    stringl = list(string)

    stringl[5] = string[8]
    stringl[6] = string[9]

    stringl[8] = temp1
    stringl[9] = temp2

    return ''.join(stringl)

def loadWorkEvents(times):
    #INPUT: dictionary with the form String(startTime) : String(endTime)
    #OUTPUT: inserts new shifts into the calendar and notifies user of any inserts
    events = getFutureEvents()

    for key in times:
        shift = {
            'summary': 'Work',
            'start': {
                'dateTime' : key,
                'timeZone' : 'Australia/Victoria',
            },
            'end': {
                'dateTime' : times[key],
                'timeZone' : "Australia/Victoria",
            },
            'description' : 'Auto generated by Lachlan Porters webscrapper python script',
            'colorId' : '9',
            'location' : 'Champions IGA Grovedale Central',
        }
        duplicateEvent = False
        for event in events:
            # +10:00 for timezone conversion
            #TODO: find better way to do timezone conversion
            if(event['start'].get('dateTime') == key + "+10:00" and event['summary'] == shift['summary']):
                duplicateEvent = True
        if not duplicateEvent:
            insertEvent(shift)
        else:
            print("Found duplicate shift on " + key)


if __name__ == '__main__':
    main()

#keep console open for 5 seconds before closing
time.sleep(5)