!(function(window, $) {
    $(function() {
        var queryElem = $('#query_string'),
            lat = queryElem.data('lat'),
            lng = queryElem.data('lng'),
            latlng = new google.maps.LatLng(lat, lng),
            //can be customized later
            image = 'http://www.google.com/intl/en_us/mapfiles/ms/micons/blue-dot.png';

        var mapOptions = {
                center: new google.maps.LatLng(lat, lng),
                zoom: 10,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            },
            map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions),
            marker = new google.maps.Marker({
                position: latlng,
                map: map,
                icon: image
            }),
            geocoder = new google.maps.Geocoder(),
            input = document.getElementById('query_string'),
            autocomplete = new google.maps.places.Autocomplete(input, {
                types: ["geocode"]
            });

        autocomplete.bindTo('bounds', map);
        var infowindow = new google.maps.InfoWindow();

        google.maps.event.addListener(autocomplete, 'place_changed', function() {
            infowindow.close();
            var place = autocomplete.getPlace(),
                location = place.geometry && place.geometry.location ?
                place.geometry.location : latlng;
            if (place.geometry && place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else if (place.geometry && place.geometry.location) {
                map.setCenter(place.geometry.location);
                map.setZoom(17);
            }

            moveMarker(place.name, location);
        });

        queryElem.focusin(function() {
            $(document).keypress(function(e) {
                if (e.which == 13) {
                    infowindow.close();
                    var firstResult = $(".pac-container .pac-item:first").text();

                    geocoder.geocode({
                        "address": firstResult
                    }, function(results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            var lat = results[0].geometry.location.lat(),
                                lng = results[0].geometry.location.lng(),
                                placeName = results[0].address_components[0].long_name,
                                latlng = new google.maps.LatLng(lat, lng);

                            moveMarker(placeName, latlng);
                            queryElem.val(placeName);
                        }
                    });
                }
            });
        });

        // TODO: implement via dependency injection
        window.mapRefocus = function() {
            map.setCenter(marker.getPosition());
        };

        function moveMarker(placeName, latlng) {
            updateCoordinates(latlng);
            marker.setIcon(image);
            marker.setPosition(latlng);
            infowindow.setContent(placeName);
            infowindow.open(map, marker);
        }

        function updateCoordinates(latlng) {
            queryElem.data('lat', latlng.lat());
            queryElem.data('lng', latlng.lng());
        }

        function geocodeLatLng(loc) {
            var latlngStr = {
                    lat: loc.coords.latitude,
                    lng: loc.coords.longitude
                },
                latlng = new google.maps.LatLng(latlngStr.lat, latlngStr.lng);

            console.log(latlngStr);
            geocoder.geocode({
                'location': latlngStr
            }, function(results, status) {
                if (status === google.maps.GeocoderStatus.OK) {
                    if (results[1]) {
                        var res = results[1].formatted_address;

                        map.setZoom(13);
                        queryElem.val(res);
                        moveMarker(res, latlng)
                    } else {
                        window.alert('No results found');
                    }
                } else {
                    window.alert('Geocoder failed due to: ' + status);
                }
            });
        }

        function getBrowserLocation(e) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(geocodeLatLng);
            }
        }

        $("#current_location").click(getBrowserLocation);
        $(".image-tile").click(function(){
            var offset = $("section.parallax").offset(),
                val = $(this).data("cat"),
                elem = $('#category option[value="' + val + '"]');
            console.log(val, elem);
            elem.prop('selected', true).change();
            $('html, body').animate({
                scrollTop: offset.top,
                scrollLeft: offset.left
            });
        });
    });
}(window, window.jQuery));