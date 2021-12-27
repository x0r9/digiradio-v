

function mapping_onload()
{
    // load up the map...
     mapping_map = L.map('mapid').setView(map_center_start, map_center_zoom);

     L.tileLayer(map_tile_url, {
        attribution: map_attribution,
        maxZoom: 18,
        id: map_tile_id,
        accessToken: map_tile_access_token
    }).addTo(mapping_map);

    // Load up the symbols
    let symbol_promise = new Promise((resolve, reject) =>{
        aprs_symobols_init(resolve);
    });


    let points_promise = new Promise((resolve, reject) =>{
        load_points(resolve);
    });

    Promise.all([points_promise, symbol_promise]).then((values) => {
        console.log(values);
        plot_points(values[0]);
    });
}

function create_aprs_icon(a,b)
{
    let iconOptions = {iconSize: [32, 32],  iconUrl: 'static/basic_symbol.png'}
    let img_obj = aprs_symbol_fetch(a,b);
    if(img_obj != null)
    {
        iconOptions['iconUrl'] = img_obj.src;
    }

    return L.icon(iconOptions);
}

function load_points(done_callback)
{
    $.getJSON( "last-points/36000", function( data ) {
        done_callback(data);
        });


}

function plot_points(data)
{
    // data has been fetched, lets draw them

    // qth
    let marker = L.marker(qth_latlon,
                {title: qth_name, icon:create_aprs_icon(qth_symbol[0], qth_symbol[1]), clickable: true}).addTo(mapping_map);
    let text = 'QTH :'+qth_name;
    marker.bindPopup(text);

    // data points
     $.each( data.points, function( n, point ) {
            let marker = L.marker([point.latitude, point.longitude],
                {title: point.from, icon:create_aprs_icon(point.symbol[0], point.symbol[1]), clickable: true}).addTo(mapping_map);
            let text = 'from :'+point.from;
            if (n != point.from)
            {
                text = n + ' ' + text;
            }
            marker.bindPopup(text);

            // Is there a path?
            if (n in data.moves)
            {
                let polyline_path = [[point.latitude, point.longitude]];
                let polyline_opts = {color:'red'};
                // Create a line...
                $.each( data.moves[n], function( n, move_point ) {
                    polyline_path.push([move_point[1], move_point[2]]);
                });
                let pline = new L.Polyline(polyline_path , polyline_opts);
                pline.addTo(mapping_map);
            }

        });

}
