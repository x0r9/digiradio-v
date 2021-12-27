

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
        ws_init();
    });
}

function create_aprs_icon(a,b, blink)
{
    let iconOptions = {iconSize: [32, 32],  iconUrl: 'static/basic_symbol.png'}
    let img_obj = aprs_symbol_fetch(a,b);
    if(img_obj != null)
    {
        iconOptions['iconUrl'] = img_obj.src;
    }

    if(blink)
    {
        iconOptions['className'] = "map_marker_blink";
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
    marker_qth = L.marker(qth_latlon,
                {title: qth_name, icon:create_aprs_icon(qth_symbol[0], qth_symbol[1], false), clickable: true}).addTo(mapping_map);
    let text = 'QTH :'+qth_name;
    marker_qth.bindPopup(text);
    var markers = {};
    // data points
     $.each( data.points, function( n, point ) {
            let marker = L.marker([point.latitude, point.longitude],
                {title: point.from, icon:create_aprs_icon(point.symbol[0], point.symbol[1], false), clickable: true}).addTo(mapping_map);
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

            // add into markers
            markers[n] = marker;

        });

}

function ws_init()
{
    // Connect to the Websocket and start listening...
    var map_ws = new WebSocket(map_ws_url);
    map_ws.onmessage = ws_on_msg;
    map_ws.onconnect = ws_on_connect;
}

function ws_on_connect(event)
{
    console.log("ws conencted");
}

function ws_on_msg(event)
{
    // On a message from the websocket
    console.log("on msg");
    let raw_data = event.data;
    console.log(raw_data);
    let json_data = JSON.parse(raw_data);
    if (json_data.dtype == "ping")
    {
        console.log("ping!!! "+raw_data);
        ping_qth();
    }
    else
    {
        console.log("unkown dtype: "+json_data.dtype);
    }
}

function ping_qth()
{
    let new_icon = create_aprs_icon(qth_symbol[0], qth_symbol[1], true);
    let reset_icon = create_aprs_icon(qth_symbol[0], qth_symbol[1], false);
    //console.log("animate");
    marker_qth.setIcon(new_icon);

    setTimeout(function() {
        marker_qth.setIcon(reset_icon);
        //console.log("no-animate");
    }, 4000);
}
