/*
Template Name: STUDIO - Responsive Bootstrap 5 Admin Template
Version: 4.4.0
Author: Sean Ngu
Website: http://www.seantheme.com/studio/
*/

var handleRenderTableData = function() {
	var height = $(window).height() - $('#header').height() - 165;
	var options = {
		dom: "<'row mb-2'<'col-7 col-md-6 d-flex justify-content-start'f><'col-5 col-md-6 text-end'B>><'row'<'col-sm-12'tr>><'row mt-n1'<'col-sm-12 col-md-5 fs-12px'i><'col-sm-12 col-md-7 fs-12px'p>>",
		scrollY:        height,
		scrollX:        true,
		paging:         false,
		fixedColumns:   {
			left: 3
		},
		order: [[1, 'asc']],
		columnDefs: [
			{ targets: 'no-sort', orderable: false }
		],
		buttons: [{ 
			extend: 'excel', 
			text: '<i class="fa fa-download fa-fw me-1 text-theme"></i> Export Excel',
			className: 'btn-default fs-13px fw-semibold py-5px pe-3',
			footer: true
		}]
	};
	
	if ($(window).width() < 767) {
		options.fixedColumns = { left: 2 };
	}
	$('#datatable').DataTable(options);
	
	$('[data-id="table"]').removeClass('d-none');
	handelTooltipPopoverActivation();
	$(window).trigger('resize');
};


/* Controller
------------------------------------------------ */
$(document).ready(function() {
	handleRenderTableData();
});