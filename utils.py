from fastapi import HTTPException

max_scales = 2

def validate_airport_codes(source_airport_code, destination_airport_code, airport_code_type):
    if airport_code_type == "IATA":
        if (len(source_airport_code) != 3) or (len(destination_airport_code) != 3):
            raise HTTPException(status_code=400, detail="IATA code must be 3 characters long")
    elif airport_code_type == "ICAO":
        if (len(source_airport_code) != 4) or (len(destination_airport_code) != 4):
            raise HTTPException(status_code=400, detail="ICAO code must be 4 characters long")
    else:
        raise HTTPException(status_code=400, detail="Airport code type must be IATA or ICAO")

def parseResults(results, code_type, mongoDB):
    airlines = mongoDB.airlines
    airports = mongoDB.airports

    code_type = code_type.lower()
    all_results = []
    for result in results:
        new_result = []
        for direct_route in result['r']:
            this_airline = airlines.find_one({'$or':[{'iata':{'$eq':direct_route['iata']}},{'icao':{'$eq':direct_route['icao']}}]})
            this_source = airports.find_one({code_type: { '$eq': direct_route.nodes[0][code_type] }})
            this_destination = airports.find_one({code_type: { '$eq': direct_route.nodes[1][code_type] }})

            new_result.append({
                'source': direct_route.nodes[0][code_type],
                'source_city': this_source['city'],
                'source_country': this_source['country'],
                'destination': direct_route.nodes[1][code_type],
                'destination_city': this_destination['city'],
                'destination_country': this_destination['country'],
                'distance': direct_route['distance'],
                'airline_name': this_airline['name']
            })
        all_results.append(new_result)        
        
    return all_results