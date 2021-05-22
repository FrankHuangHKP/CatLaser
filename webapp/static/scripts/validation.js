$("#laseron").on("change", function() {
	$("#mode-label").removeClass("hidden");
    $("#auto").removeClass("hidden");
	$("#auto-label").removeClass("hidden");
    $("#manual").removeClass("hidden");
	$("#manual-label").removeClass("hidden");

    
})

// TODO: when user selects cash option
$("#laseroff").on("change", function() {

    $("#mode-label").addClass("hidden");
    $("#auto").addClass("hidden");
	$("#auto-label").addClass("hidden");
    $("#manual").addClass("hidden");
	$("#manual-label").addClass("hidden");
	$("#x").addClass("hidden");
    $("#y").addClass("hidden");
	$("#x-label").addClass("hidden");
    $("#y-label").addClass("hidden");


})


$("#manual").on("change", function() {
	$("#x").removeClass("hidden");
    $("#y").removeClass("hidden");
	$("#x-label").removeClass("hidden");
    $("#y-label").removeClass("hidden");

    
})

// TODO: when user selects cash option
$("#auto").on("change", function() {

    $("#x").addClass("hidden");
    $("#y").addClass("hidden");
	$("#x-label").addClass("hidden");
    $("#y-label").addClass("hidden");

})

function mouseclick(event) {
	console.log('off+'+event.offsetX)
	console.log('off+'+event.offsetY)
	document.getElementById("x").value = parseInt(event.offsetX);
	document.getElementById("y").value = parseInt(event.offsetY);
}

