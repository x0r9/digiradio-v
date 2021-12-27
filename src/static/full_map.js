
var markers = {};

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

function create_marker( name, point)
{
    let marker = L.marker([point.latitude, point.longitude],
                    {title: name,
                    icon:create_aprs_icon(point.symbol[0], point.symbol[1], false),
                    clickable: true});
    let text = 'from :'+point.from;
    if (name != point.from)
    {
        text = name + ' ' + text;
    }
    marker.bindPopup(text);
    return marker;
}

function plot_points(data)
{
    // data has been fetched, lets draw them

    // qth
    marker_qth = L.marker(qth_latlon,
                {title: qth_name, icon:create_aprs_icon(qth_symbol[0], qth_symbol[1], false), clickable: true}).addTo(mapping_map);
    let text = 'QTH :'+qth_name;
    marker_qth.bindPopup(text);
    // data points
     $.each( data.points, function( n, point ) {
            let marker = create_marker(n, point);
            marker.addTo(mapping_map);

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
    var setting = new URL(map_ws_url);
    var this_thing = new URL(window.location);

    var new_ws_url = setting.protocol + "//" + this_thing.host + setting.pathname;

    var map_ws = new WebSocket(new_ws_url);
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
    else if (json_data.dtype == "ping_point")
    {
        // Recieved a new  point, animate that?
        $.each( json_data.data, function( n, point ) {
            console.log("updating: "+n);
            update_marker(n, point);
        });

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

function update_marker(marker_name, marker_data)
{
    var marker = null;
    if(marker_name in markers)
    {
        marker = markers[marker_name];
    }
    else
    {
        // create a new marker and update the list
        marker = create_marker(marker_name, marker_data);
        marker.addTo(mapping_map);
        markers[marker_name] = marker;
    }

    // Now the marker is there... Animate the thing
    let new_icon = create_aprs_icon(marker_data.symbol[0], marker_data.symbol[1], true);
    let reset_icon = create_aprs_icon(marker_data.symbol[0], marker_data.symbol[1], false);
    //let new_icon = create_aprs_icon(marker_data.symbol[0], 't', true);
    //let reset_icon = create_aprs_icon(marker_data.symbol[0], 't', false);

    marker.setIcon(new_icon);
    console.log("animate - "+marker_name);
    setTimeout(function() {
        marker.setIcon(reset_icon);
        console.log("no-animate - "+marker_name);
    }, 4000);


}
