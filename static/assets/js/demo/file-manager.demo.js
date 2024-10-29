/*
Template Name: STUDIO - Responsive Bootstrap 5 Admin Template
Version: 4.4.0
Author: Sean Ngu
Website: http://www.seantheme.com/studio/
*/

var handleFileManagerClick = function() {
	var fileHasSubNodes = document.querySelectorAll(".file-node.has-sub");

	fileHasSubNodes.forEach(node => {
		var fileArrow = node.querySelector(".file-link > .file-arrow");
		
		fileArrow.addEventListener("click", function (event) {
			event.preventDefault();
			node.classList.toggle("expand");
		});
	});
	
	var fileInfoNodes = document.querySelectorAll(".file-node");

	fileInfoNodes.forEach(node => {
		var fileInfo = node.querySelector(".file-link > .file-info");
		
		fileInfo.addEventListener("click", function (event) {
			event.preventDefault();
			fileInfoNodes.forEach(otherNode => {
				if (otherNode !== node) {
					otherNode.classList.remove("selected");
				}
			});
			node.classList.add("expand");
			node.classList.add("selected");
		});
	});
};

/* Controller
------------------------------------------------ */
$(document).ready(function() {
  handleFileManagerClick();
});