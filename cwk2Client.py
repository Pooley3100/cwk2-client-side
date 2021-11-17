from flask import Flask, render_template, redirect, url_for
import requests, json

app = Flask(__name__)

selected = []
result = []


# Gets list of places
@app.route("/")
def placesList():
    results = []

    places = requests.get('https://locations-api-cwk2.azurewebsites.net/api/Place')
    places = json.loads(places.content)
    countries = requests.get('https://locations-api-cwk2.azurewebsites.net/api/Location')
    countries = json.loads(countries.content)

    # Concatenate all places with cityId to send to html form
    for place in places:
        city = findCity(place['CityID'], countries)
        results.append([place, city])

    return render_template('countries.html', countries=results, selected=selected)


# Gets city name from selected place
def findCity(placeID, countries):
    for country in countries:
        if country['Id'] == placeID:
            return country['City']


# Quick route to tell flask which city has been selected
@app.route("/country/<city>")
def countriesSelect(city):
    selected.append(city)
    # TODO change colour of selected items. <<<<
    return redirect(url_for('placesList'))


# sends selections
@app.route("/recommendations")
def sendSelection():
    url = 'https://d2d5l278t3.execute-api.eu-west-2.amazonaws.com/recommendations'
    citiesList = selected

    # TODO: allow client to change these two options <<<<
    priceLevel = ["Medium", "Low"]
    activity = ["Restaurant","Hotel"]
    dataOptions = {
        "locations": citiesList,
        "activities": activity,
        "prices": priceLevel}

    x = requests.post(url, json=dataOptions)
    result.append(x)
    return redirect(url_for('displayRecommend'))


@app.route("/displayRecommendations")
def displayRecommend():
    recommendResponse = result[0]
    print(result[0].content.decode('utf8', 'strict'))

    resultObj = json.loads(result[0].content.decode('utf8', 'strict'))

    for resultS in resultObj:
        print(resultS)
    return render_template('recommendations.html', recommendations=resultObj)


@app.route("/displayFlights/<city>")
def flightSearch(city):
    # TODO
    url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
    payload = {'client_id': 'HPruFliyd5kQxai68oZvgVuaPL5p13NR', 'client_secret': 'vi3L3JTBOoP5eEYk',
               'grant_type': 'client_credentials'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(url, data=payload, headers=headers)

    token = (json.loads(r.content))['access_token']
    print(token)

    auth = 'Bearer {0}'.format(token)
    custom_header = {'Authorization': auth}
    # Now get IATA codes
    url = "https://test.api.amadeus.com/v1/reference-data/locations?subType=CITY&keyword={0}&page%5Blimit%5D=10&page%5Boffset%5D=0&sort=analytics.travelers.score&view=FULL".format(city)

    iataResponse = requests.get(url, headers=custom_header)
    print(iataResponse)

    testR = json.loads(iataResponse.content)
    otherIata = (testR["data"][0]["iataCode"])

    # Now search for flights
    payloadFlightSearch = {
        "currencyCode": "USD",
        "originDestinations": [
            {
                "id": "1",
                "originLocationCode": "LON",
                "destinationLocationCode": otherIata,
                "departureDateTimeRange": {
                    "date": "2021-12-01",
                    "time": "10:00:00"
                }
            },
            {
                "id": "2",
                "originLocationCode": otherIata,
                "destinationLocationCode": "LON",
                "departureDateTimeRange": {
                    "date": "2021-12-18",
                    "time": "17:00:00"
                }
            }
        ],
        "travelers": [
            {
                "id": "1",
                "travelerType": "ADULT",
                "fareOptions": [
                    "STANDARD"
                ]
            },
            {
                "id": "2",
                "travelerType": "CHILD",
                "fareOptions": [
                    "STANDARD"
                ]
            }
        ],
        "sources": [
            "GDS"
        ],
        "searchCriteria": {
            "maxFlightOffers": 2,
            "flightFilters": {
                "cabinRestrictions": [
                    {
                        "cabin": "BUSINESS",
                        "coverage": "MOST_SEGMENTS",
                        "originDestinationIds": [
                            "1"
                        ]
                    }
                ],
                "carrierRestrictions": {
                    "excludedCarrierCodes": [
                        "AA",
                        "TP",
                        "AZ"
                    ]
                }
            }
        }

    }
    url = 'https://test.api.amadeus.com/v2/shopping/flight-offers'

    # payloadFlightSearch = json.dumps(payloadFlightSearch)
    responseSearch = requests.post(url, headers=custom_header, json=payloadFlightSearch)
    print(responseSearch)

    responseSearch = json.loads(responseSearch.content)

    return render_template('flightresults.html', results=responseSearch)

if __name__ == '__main__':
    app.run(debug=True)
