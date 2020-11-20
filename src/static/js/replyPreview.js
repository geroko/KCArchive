document.querySelectorAll('.post__reply, .reply-link').forEach(replyLink => {
	replyLink.addEventListener('mouseenter', function() {
		renderReply(replyLink.text.slice(2), replyLink);
	});

	replyLink.addEventListener('mouseleave', function() {
		var replyPreview = document.querySelector('.reply-preview');
		if (replyPreview) {
			replyPreview.remove();
		}
	});
});

function renderReply(replyNum, replyLink) {
	var cloneReply = document.getElementById(replyNum).cloneNode(true);

	cloneReply.classList.add('reply-preview');
	cloneReply.style.top = replyLink.offsetTop + replyLink.offsetHeight + 'px';
	cloneReply.style.left = replyLink.offsetLeft + 'px';

	document.body.appendChild(cloneReply);
};
