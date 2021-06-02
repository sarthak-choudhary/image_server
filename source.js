var mymap = L.map("map").setView([25.505, 92.09], 7);
var layer = L.tileLayer.wms("http://127.0.0.1:8000/",{
	
});

layer.addTo(mymap);