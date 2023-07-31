# Wondrous.day

[wondrous.day](https://wondrous.day/) is a web application that I built along with my partner. The primary use case is for couples to create online wedding invitations to send to their guests by a URL.

At its core is a CMS built with wagtail. As users add details they can see their edits in real time. Users can create their invitations for free and then go through a slack payment workflow when they are happy with the result.

Running on a single server with a Django backend + Wagtail for the CMS component. The backend logic is quite simple so I reasoned that the network traffic of images would be the bottleneck for system resources. That's why static and media assets are cached behind Clourdlares CDN while media assets are hosted in S3.


