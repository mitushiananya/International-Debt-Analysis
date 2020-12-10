import requests
import pandas as pd
import datetime
import wbdata
import plotly.express as px

# Get all sources from the World Bank API
sources = requests.get("http://api.worldbank.org/v2/sources?per_page=100&format=json")
sourcesJSON = sources.json()

# View the JSON response
print("JSON Response: \n",sourcesJSON)


# Parse through the response to see the source names and ID numbers
for i in sourcesJSON[1]:
    if i["name"] == "International Debt Statistics":
        print("\n")
        print("The source ID for International Debt Statistics is " + i["id"])
    else:
        pass
    # View all the source names and IDs
    print(i["id"],i["name"])

# Requesting the indicators for the topic External Debt
indicators = requests.get("http://api.worldbank.org/v2/indicator?format=json&source=6")
indicatorsJSON = indicators.json()

# The total number of indicators
print("There are " + str(indicatorsJSON[0]["total"]) + " IDS indicators")

# Get all External Debt indicators, with a per_page parameter of 500.
indicators = requests.get("http://api.worldbank.org/v2/indicator?format=json&source=6&per_page=500")
indicatorsJSON = indicators.json()

# View ALL the indicators
print("All the indicators: \n",indicatorsJSON)

# Parse through the response to see the Indicator IDs and Names
print("Indicator IDs and Names: \n")
for i in indicatorsJSON[1]:
    IDSindicators = (i["id"],i["name"])
    print(IDSindicators) # View the indicator ids and names

# Use the indicator code to define the "indicator" variable
indicator = "DT.DOD.DLXF.CD"

# Parse through the response to get the "sourceNote" or definition for the desired indicator
print("Source Note: \n")
for dict_entity in indicatorsJSON[1]:
    if dict_entity["id"] == indicator:
        print(dict_entity["sourceNote"])
    else:
        pass

# Requesting the countries
dlocations = requests.get("http://api.worldbank.org/v2/sources/6/country?per_page=300&format=JSON")
dlocationsJSON = dlocations.json()

# Parse through the response to see the country IDs and names
dlocations = dlocationsJSON["source"][0]["concept"][0]["variable"]
listLen = int(len(dlocations))

# Create dataframe with country values
df = pd.DataFrame(columns=["id", "value"])
for i in range(0,listLen):
    code = dlocations[i]["id"]
    name = dlocations[i]["value"]
    df = df.append({"id":code, "value":name}, ignore_index = True)
dlocationsList = df

# First few rows in the dataframe
print("Location/Countries: \n",dlocationsList.head(n=10))

# Get the full list of the creditor codes and names
# We'll use a query like the one above, but in the get request we will replace "country" with "counterpart-area."
# Requesting the locations (Using the same query as above)
clocations = requests.get("http://api.worldbank.org/v2/sources/6/counterpart-area?per_page=300&format=JSON")
clocationsJSON = clocations.json()

# Parse through the response to see the location IDs and names
clocations = clocationsJSON["source"][0]["concept"][0]["variable"]
listLen = int(len(clocations))

# Create dataframe with location values
df = pd.DataFrame(columns=["id", "value"])
for i in range(0,listLen):
    code = clocations[i]["id"]
    name = clocations[i]["value"]
    df = df.append({"id":code, "value":name}, ignore_index = True)
clocationsList = df

# First few rows in the dataframe
print(clocationsList.head(n=10))

# Selecting the indicator
indicatorSelection = {"DT.DOD.DLXF.CD":"ExternalDebtStock"}

# Select the countries or regions
locationSelection = ["ECA","SSA","SAS","LAC","MNA","EAP"]

# Selecting the time frame
timeSelection = (datetime.datetime(2009, 1, 1), datetime.datetime(2019, 12, 31))

# Making the API call and assigning the resulting DataFrame to "EXD"
EXD = wbdata.get_dataframe(indicatorSelection, country = locationSelection, data_date = timeSelection, convert_date = False)

# Print the first 5 lines of the DataFrame
print("External Debt Data: \n",EXD.head())

# Reshape the data
EXDreshaped = pd.DataFrame(EXD.to_records())

# Creating a function that will change units to billions and round to 0 decimal places
def formatNum(x):
    y = x/1000000000
    z = round(y)
    return(z)

# Running the function on the desired data column
EXDreshaped.ExternalDebtStock = formatNum(EXDreshaped.ExternalDebtStock)

# Renaming column headers
EXDclean = EXDreshaped.rename(index=str, columns={ "date":"Year", "country":"Region" })

# Remove the "(excluding high income)" from each of the region names
EXDclean["Region"] = EXDclean["Region"].str.replace("excluding high income","").str.replace(")","").str.replace("(","")

print(EXDclean.head())

# Defining the data source
source = EXDclean

# Creating the chart
chart = px.line(EXDclean, x="Year", y="ExternalDebtStock", color="Region", color_discrete_sequence = px.colors.qualitative.Vivid, title="Regional Long-term External Debt Stock (excluding High-Income countries)(USD billion)")
chart.update_layout(plot_bgcolor="white")

# Displaying the chart
chart.show()