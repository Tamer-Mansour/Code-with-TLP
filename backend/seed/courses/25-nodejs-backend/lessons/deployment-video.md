This video from TechWorld with Nana provides a practical walkthrough of containerising a Node.js application with Docker — writing a Dockerfile, building and tagging an image, running it locally with environment variables, and pushing it to a container registry for deployment.

Key takeaways:
- Multi-stage Docker builds to keep production images small.
- Why `npm ci` should be used instead of `npm install` in CI and Docker.
- Running Node containers as a non-root user for security.

Combine the concepts here with the Deployment reading lesson to build a complete mental model of shipping Node APIs to production.
