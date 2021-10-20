from datetime import datetime as date
import requests
import re
import json
import time
import os

# Data format
# Date,Open,High,Low,Close,Adj Close,Volume
# 2020-07-13,97.264999,99.955002,95.257500,95.477501,94.696587,191649200

# 347155200


def yahoo_parser(ticker):
    start_date = '1594515200'
    if (start_date != '347155200'):
        print("Start date isn't set for maximum period yet!")
    # Set time to 10 minutes ago to be safe
    current_date = str(date.now().timestamp() - 600)[:-7]
    yahoo_link = (
        "https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=1d&events=history&includeAdjustedClose=true"
        % (ticker, start_date, current_date)
    )
    print(yahoo_link)

    headers = {"user-agent": "PostmanRuntime/7.28.4"}

    req = requests.get(yahoo_link, headers=headers)
    if req.status_code != 200:
        time.sleep(5)
        # Return false to make start.py restart the function
        return False
    print(req)

    foldername = "./output/"
    os.makedirs(os.path.dirname(foldername), exist_ok=True)
    print(os.path.dirname(foldername))
    with open("./output/%s.json" % ticker, "w") as fd:
        # Regex format for date catch in such format: 2020-07-13
        compileDate = re.compile(b"[0-9]{4}-[0-9]{2}-[0-9]{2}")
        titleParse = True
        chunkRemaining = 0
        encoding = "utf-8"

        chunkObject = {}
        for chunk in req.iter_content(chunk_size=128):
            # Regex catches all the data before '\n' at the start of the stream to set Titles
            if titleParse:
                parsedTitles = re.compile(
                    b".*?(?=\n)").findall(chunk)[0].split(b",")
                print(parsedTitles)
                titleParse = False

            # Data from previous iteration which wasn't saved into dictionary
            if chunkRemaining:
                chunk = chunkRemaining + chunk

            # Check if there is complete Date data
            findDates = compileDate.findall(chunk)

            # If regex finds any Date value check if there exists complete Data for the Date
            if len(findDates) > 0:
                # chunkObject = {}
                for index in range(len(findDates)):
                    dateString = findDates[index]
                    compileData = re.compile(
                        b"(?<=%b,)(.*?)(?=\n)" % dateString)
                    findData = compileData.search(chunk)
                    # If regex catches data for given date, start parsing it
                    if findData:
                        parsedData = chunk[findData.start(): findData.end()].split(
                            b","
                        )

                        for titleIndex in range(len(parsedTitles)):
                            # First title is Date which is not inside parsed data, set it to date value
                            if titleIndex == 0:
                                # Set key for given Date in Dictionary
                                print(findDates[titleIndex])
                                chunkObject[findDates[index].decode(encoding)] = {
                                }
                            else:
                                # parsed Data doesnt have Date field, so set it's index to -1
                                chunkObject[findDates[index].decode(encoding)].update(
                                    {
                                        parsedTitles[titleIndex]
                                        .decode(encoding): parsedData[titleIndex - 1]
                                        .decode(encoding)
                                    }
                                )
                        print(parsedData)

                        # If there is complete Data set it will be appended to dictionary.
                        # Save the remaining data into variable and prepend to string in the next iteration
                        chunkRemaining = chunk[findData.end():]

        json.dump(chunkObject, fd)
        print('Number of days parsed: ', len(chunkObject.keys()))
        if (start_date != '347155200'):
            print("Start date isn't set for maximum period yet!")
        time.sleep(3)
        return True
