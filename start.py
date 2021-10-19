# Read stock tickes from yahoo_parser_target.txt and download historical data from yahoo finance

from yahoo_parser import yahoo_parser

targetListFileName = 'yahoo_parser_target.txt'

crawlingList = []
with open(targetListFileName, 'r', encoding='utf8') as source:
    for line in source:
        crawlingList.append(line.strip())
print(crawlingList)

for eachTicker in crawlingList:
    response = False
    while response == False:
        response = yahoo_parser(eachTicker)
