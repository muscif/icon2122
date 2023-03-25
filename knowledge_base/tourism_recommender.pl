:- debug.
:- set_prolog_flag(encoding, utf8).
:- use_module(library(lists)).
:- initialization(go).

haversine_distance(Lat1, Lon1, Lat2, Lon2, Dis):-
    P is 0.017453292519943295,
    A is (0.5 - cos((Lat2 - Lat1) * P) / 2 + cos(Lat1 * P) * cos(Lat2 * P) * (1 - cos((Lon2 - Lon1) * P)) / 2),
    Dis is ((12742 / 2) * asin(sqrt(A))).

substring(A, B) :-
    append(_, C, B), append(A, _, C).

cuisine(any, _).
cuisine(I, F) :-
    substring(I, F).

distance_accommodation_restaurant(Acc, Restaurant1, Restaurant2) :-
    accommodation(Acc, AccommodationLat, AccommodationLon, _, _, _, _, _, _),
    restaurant(Restaurant1, RestaurantLat, RestaurantLon, _, _, _, _, _, _, _, _),
    restaurant(Restaurant2, Restaurant2Lat, Restaurant2Lon, _, _, _, _, _, _, _, _),
    haversine_distance(AccommodationLat, AccommodationLon, RestaurantLat, RestaurantLon, Restaurant1Dist),
    haversine_distance(AccommodationLat, AccommodationLon, Restaurant2Lat, Restaurant2Lon, Restaurant2Dist),
    Restaurant1Dist =< Restaurant2Dist.

distance_accommodation_attraction(Acc, Attraction1, Attraction2) :-
    accommodation(Acc, AccommodationLat, AccommodationLon, _, _, _, _, _, _),
    attraction(Attraction1, AttractionLat, AttractionLon, _, _, _, _, _, _, _, _),
    attraction(Attraction2, Attraction2Lat, Attraction2Lon, _, _, _, _, _, _, _, _),
    haversine_distance(AccommodationLat, AccommodationLon, AttractionLat, AttractionLon, Attraction1Dist),
    haversine_distance(AccommodationLat, AccommodationLon, Attraction2Lat, Attraction2Lon, Attraction2Dist),
    Attraction1Dist =< Attraction2Dist.

display_accommodation(Name) :-
    accommodation(Name, _, _, Phone, Website, Email, Stars, Internet, Wheelchair),
    nl, nl,
    write("ALLOGGIO\n"),
    write("Nome: "), write(Name),
    write("\nTelefono: "), write(Phone),
    write("\nSito: "), write(Website),
    write("\nE-mail: "), write(Email),
    write("\nStelle: "), write(Stars),
    write("\nAccesso a Internet: "), write(Internet),
    write("\nAccessibilità: "), write(Wheelchair).

display_restaurant(Name) :-
    restaurant(Name, _, _, Phone, Website, Email, Cuisine, Takeaway, Delivery, OpeningHours, Wheelchair),
    nl, nl,
    write("RISTORANTE\n"),
    write("Nome: "), write(Name),
    write("\nTelefono: "), write(Phone),
    write("\nSito: "), write(Website),
    write("\nE-mail: "), write(Email),
    write("\nCucina: "), write(Cuisine),
    write("\nAsporto: "), write(Takeaway),
    write("\nDomicilio: "), write(Delivery),
    write("\nOrario di apertura: "), write(OpeningHours),
    write("\nAccessibilità: "), write(Wheelchair).

display_attraction(Name) :-
    attraction(Name, _, _, Phone, Website, Email, Fee, Wheelchair),
    nl, nl,
    write("ATTRAZIONE\n"),
    write("Nome: "), write(Name),
    write("\nTelefono: "), write(Phone),
    write("\nSito: "), write(Website),
    write("\nE-mail: "), write(Email),
    write("\nQuota d'ingresso: "), write(Fee),
    write("\nAccessibilità: "), write(Wheelchair).

% accommodation(Name, Lat, Lon, Phone, Website, Email, Stars, InternetAccess, Wheelchair).
% restaurant(Name, Lat, Lon, Phone, Website, Email, Cuisine, Takeaway, Delivery, OpeningHours, Wheelchair).
% attraction(Name, Lat, Lon, Phone, Website, Email, Fee, Wheelchair).
go :-
    write("Benvenuto nel sistema di raccomandazione per il turismo!\n"),
    write("Ti verranno poste alcune domande per aiutarti a scegliere come si svolgerà il tuo viaggio.\n"),
    write("> Dove desideri andare?\n1. Berlino\n2. Londra\n3. Parigi\n4. Milano\n"),
    read(DestinationInput),
    (
        DestinationInput == 1 -> Destination = berlino;
        DestinationInput == 2 -> Destination = londra;
        DestinationInput == 3 -> Destination = parigi;
        DestinationInput == 4 -> Destination = milano
    ),
    consult(Destination),

    write("\n> È necessario che i luoghi siano accessibili in sedia a rotelle?\n1. Sì\n2. No\n"),
    read(InputWheelchair),
    (
        InputWheelchair == 1 -> Wheelchair = true;
        InputWheelchair == 2 -> Wheelchair = _
    ),
    
    write("\n> Come desideri contattare le strutture?\n1. Telefono\n2. Sito\n3. Email\n"),
    read(Mode),
    
    write("\n> È necessario che il tuo alloggio abbia una connessione Wi-Fi?\n1. Sì\n2. No\n"),
    read(InputInternet),
    (
        InputInternet == 1 -> Internet = true;
        InputInternet == 2 -> Internet = _
    ),

    write("\n> Inserisci il numero minimo di stelle che deve avere il tuo alloggio.\n"),
    read(InputStars),

    write("\n> Inserisci il tipo di cucina che vorresti mangiare (scrivi 'any.' se ti e' indifferente).\n"),
    read(InputCuisine),

    write("\n> Desideri mangiare da asporto, a domicilio o sul posto?\n1. Asporto\n2. Domicilio\n3. Sul posto\n"),
    read(InputPlace),

    write("\n> Sei disposto a pagare una quota d'ingresso per visitare un'attrazione?\n1. Sì\n2. No\n"),
    read(InputFee),
    (
        InputFee == 1 -> Fee = true;
        InputFee == 2 -> Fee = _
    ),

    findall(Name, (
        accommodation(Name, _, _, Phone, Website, Email, Stars, Internet, Wheelchair),
        (
            Mode == 1 -> Phone \= false;
            Mode == 2 -> Website \= false;
            Mode == 3 -> Email \= false
        ),
        Stars >= InputStars
    ), Accommodations),

    findall(Name, (
        restaurant(Name, _, _, Phone, Website, Email, Cuisine, Takeaway, Delivery, _, Wheelchair),
        (
            Mode == 1 -> Phone \= false;
            Mode == 2 -> Website \= false;
            Mode == 3 -> Email \= false
        ),
        cuisine(InputCuisine, Cuisine),
        (
            InputPlace == 1 -> Takeaway \= false;
            InputPlace == 2 -> Delivery \= false;
            InputPlace == 3 -> Takeaway = _, Delivery = _
        )
    ), Restaurants),

    findall(Name, (
        attraction(Name, _, _, Phone, Website, Email, Fee, Wheelchair),
        (
            Mode == 1 -> Phone \= false;
            Mode == 2 -> Website \= false;
            Mode == 3 -> Email \= false
        )
    ), Attractions),

    nth0(0, Accommodations, Accommodation),

    min_member(distance_accommodation_restaurant(Accommodation), Restaurant, Restaurants),
    min_member(distance_accommodation_restaurant(Accommodation), Attraction, Attractions),

    display_accommodation(Accommodation),
    display_restaurant(Restaurant),
    display_attraction(Attraction),

    nl, nl, write("Grazie!"),

    halt.