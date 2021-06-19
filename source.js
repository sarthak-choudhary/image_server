var mymap = L.map("map").setView([28.61, 77.2090], 7);
var layer = L.tileLayer.wms("http://127.0.0.1:8000/?red=6&blue=4&green=3",{
	format: "image/png"
});

layer.addTo(mymap);