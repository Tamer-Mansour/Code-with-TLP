# Quiz: Design Patterns, Observability, and Security

**Q1. The Observer design pattern is best suited for:**
- [ ] Ensuring only one instance of a database connection exists
- [ ] Converting one interface to another for third-party library integration
- [x] Notifying multiple independent components when an event occurs, without the publisher knowing who the subscribers are
- [ ] Selecting between interchangeable algorithm implementations at runtime

**Q2. Which of the following is an example of the Adapter pattern?**
- [ ] A class that can only be instantiated once
- [x] A wrapper that makes a third-party payment SDK conform to your application's `PaymentGateway` interface
- [ ] A function decorator that adds retry logic to any function
- [ ] A configuration object that groups related parameters

**Q3. In the OWASP Top 10, "Broken Access Control" refers to:**
- [ ] Using MD5 instead of bcrypt for password hashing
- [ ] Accepting unsanitised user input in SQL queries
- [x] Failing to verify that a user is authorised to access the specific resource they are requesting
- [ ] Storing secrets in source code rather than environment variables

**Q4. Which log level should be used for a payment processing failure that requires immediate investigation?**
- [ ] DEBUG
- [ ] INFO
- [ ] WARNING
- [x] ERROR

**Q5. A Correlation ID in distributed systems is used to:**
- [ ] Authenticate requests between microservices
- [ ] Measure the latency of individual database queries
- [x] Link all log lines and trace spans from different services that belong to the same user request
- [ ] Enforce rate limiting on API endpoints

**Q6. The Principle of Least Privilege in security means:**
- [ ] Giving all users read-only access by default
- [ ] Using the minimum number of dependencies in your application
- [x] Each component, user, or service should have only the permissions strictly necessary to perform its function
- [ ] Restricting API access to authenticated users only
