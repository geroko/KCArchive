document.querySelectorAll('.post__reply, .quoteLink').forEach(replyLink => {
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
	var reply = document.getElementById(replyNum)
	var cloneReply = reply.cloneNode(true);

	cloneReply.classList.add('reply-preview');

	// Vertical position
	if (document.body.offsetHeight - replyLink.offsetTop > reply.offsetHeight + 50) {
		cloneReply.style.top = replyLink.offsetTop + replyLink.offsetHeight + 'px';
	} else {
		cloneReply.style.bottom = document.body.offsetHeight - replyLink.offsetTop + 'px';
	}

	// Horizontal position
	if (window.innerWidth - replyLink.offsetLeft < window.innerWidth / 2) {
		cloneReply.style.right = window.innerWidth - replyLink.offsetLeft + 'px';
	} else {
		cloneReply.style.left = replyLink.offsetLeft + 'px';
	}

	document.body.appendChild(cloneReply);
};
