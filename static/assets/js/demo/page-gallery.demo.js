/*
Template Name: STUDIO - Responsive Bootstrap 5 Admin Template
Version: 4.4.0
Author: Sean Ngu
Website: http://www.seantheme.com/studio/
*/

import PhotoSwipeLightbox from '../../plugins/photoswipe/dist/photoswipe-lightbox.esm.js';
const lightbox = new PhotoSwipeLightbox({
	gallery: '.gallery-image-list',
	children: 'a',
	pswpModule: () => import('../../plugins/photoswipe/dist/photoswipe.esm.js')
});
lightbox.init();