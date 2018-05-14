from bs4 import BeautifulSoup
import urllib.request
import csv
import smtplib
import email
import time
import keyring

gmail_user = 'SENDER_EMAIL'
gmail_password = keyring.get_password(,'SENDER_EMAIL')

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(gmail_user, gmail_password)

positions = {}

portfoliocsv = open('portfolio_real.csv', newline='')
portfolio = csv.DictReader(portfoliocsv, delimiter=',')
total_value = 0.0
body = 'You should perform the following operations: \n\n'

for row in portfolio:
	tickerDict = {}
	ticker = row['Ticker']
	print(ticker)

	#turn this into a function, dude

	page = urllib.request.urlopen('http://www.barrons.com/quote/mutualfund/us/' + ticker)
	soup = BeautifulSoup(page, 'html.parser')

	tickerDict['Count'] = float(row['Count'])
	tickerDict['Allocation'] = float(row['Allocation'])
	tickerDict['Cost'] =  float(soup.find("span", {"class": "bgLast"}).string)
	tickerDict['Value'] = tickerDict['Count'] * tickerDict['Cost']

	positions[ticker] = tickerDict
	total_value += tickerDict['Value']
	time.sleep(1)

for key in positions:
	info = positions[key]
	projCount = total_value*info['Allocation']/info['Cost']
	realAllocation = info['Value'] / total_value
	positions[key]['ProjectedCount'] = projCount
	positions[key]['RealAllocation'] = realAllocation
	positions[key]['ToDo'] = positions[key]['ProjectedCount'] - info['Count']
	body += str(key) + ": " + str(positions[key]['ToDo']) + "\n"

message = email.message.EmailMessage()
message['Subject'] = 'Stock Action'
message['From'] = gmail_user
message['To'] = keyring.get_password(,'RECEIVER_EMAIL')
message.set_content(body)

server.send_message(message)
server.close()