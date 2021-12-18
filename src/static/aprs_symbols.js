//
// APRS icon split up..
// Requires jquery...
//


var aprs_icon_0_path = "static/aprs_symbols/aprs-symbols-24-0x2.png";
var aprs_icon_1_path = "static/aprs_symbols/aprs-symbols-24-1x2.png";
var aprs_icons_x_count = 16;
var aprs_icons_y_count = 6;
var aprs_char_table = ['!"#$5&\'()*+,-./0', '123456789:;<=>?@', 'ABCDEFGHIJKLMNOP', 'QRSTUVWXYZ[\\]^_`', 'abcdefghijklmnop', 'qrstuvwxyz{|}~  '];


var aprs_icon_0_images = {};
var aprs_icon_1_images = {};
var aprs_icon_loader_counter = 0;

function aprs_symobols_init(call_on_complete)
{

    let end = function(x)
    {
        console.log("end called - "+x);
        aprs_icon_loader_counter |= x;
        console.log("aprs_icon_loader_counter - "+aprs_icon_loader_counter);
        if (aprs_icon_loader_counter === 3)
        {
            console.log("end complete - "+aprs_icon_loader_counter);
            if(call_on_complete)
                call_on_complete();
        }
    }
    fetch_symbols(aprs_icon_0_path, aprs_icon_0_images, function(){end(1);});
    fetch_symbols(aprs_icon_1_path, aprs_icon_1_images, function(){end(2);});


}

function fetch_symbols(image_path, table_to_update, call_on_complete)
{
    let c = document.createElement("canvas");
    let ctx = c.getContext('2d');
    let full_table_img = new Image();
    //onload event listener to process the image data after it was loaded
    let let_on_load = function () {
        console.log("loaded - "+image_path);
        // pop the image onto a canvas to manipulate the image from...
        let icon_width = full_table_img.width / aprs_icons_x_count;
        let icon_height = full_table_img.height / aprs_icons_y_count;
        c.width = icon_width;
        c.height = icon_height;
        $.each( aprs_char_table, function( y, x_row ) {
                $.each( x_row.split(''), function( x, icon_char ) {
                    ctx.clearRect(0, 0, c.width, c.height);
                    ctx.drawImage(full_table_img, -icon_width*x, -icon_height*y);
                    let icon_img = new Image();
                    icon_img.src = c.toDataURL("image/png");
                    // Populate the table...
                    table_to_update[icon_char] = icon_img;
                });
            });
        console.log("processed - "+image_path);
        call_on_complete();

    };
    full_table_img.onload = let_on_load;
    //start loading image
    full_table_img.src = image_path;
}

function aprs_symbol_fetch(a, b)
{
    //
    // Return a IMG object of the given icon
    //
    let table = aprs_icon_0_images;
    if (a === '/')
    {
        table = aprs_icon_1_images;
    }

    if (b in table)
    {
        return table[b];
    }
    return null;
}

