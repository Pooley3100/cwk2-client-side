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
    return redirect(url_for('placesList'))


# sends selections
@app.route("/recommendations")
def sendSelection():

    url = 'https://d2d5l278t3.execute-api.eu-west-2.amazonaws.com/recommendations'
    citiesList = selected

    # TODO: change extra options
    priceLevel = ['medium']
    activity = ['Restaurant']
    dataOptions = {
        "locations": citiesList,
        "activities": activity,
        "prices": priceLevel}


    x = requests.post(url, json=dataOptions)
    result.append(x)
    return redirect(url_for('displayRecommend'))


@app.route("/displayRecommendations")
def displayRecommend():

    resultObj = (json.loads((result[0].content).decode('utf8', 'strict')))

    for resultS in resultObj:
        print(resultS)
    return render_template('recommendations.html', recommendations = resultObj)

@app.route("/displayFlights/<city>")
def flightSearch(city):
    # TODO
    return "hello"



if __name__ == '__main__':
    app.run(debug=True)
