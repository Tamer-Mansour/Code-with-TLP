# Quiz: Transactions and Atomicity

**Q1. MongoDB single-document writes are:**
- [x] Always atomic
- [ ] Atomic only when using a session
- [ ] Atomic only with write concern majority
- [ ] Never atomic

**Q2. Multi-document transactions were added to MongoDB replica sets in version:**
- [ ] 3.6
- [x] 4.0
- [ ] 4.2
- [ ] 5.0

**Q3. Which statement about the `session` object in a transaction is correct?**
- [ ] The session is optional and only needed for the commit
- [ ] Each operation uses a different session automatically
- [x] The session must be passed to every read and write operation inside the transaction
- [ ] Sessions are only needed for sharded clusters

**Q4. What happens if you call `abortTransaction()` after some writes have already executed?**
- [ ] The writes that already ran remain committed
- [ ] Only the last write is rolled back
- [x] All writes made within the transaction are rolled back atomically
- [ ] MongoDB will automatically commit them anyway

**Q5. Which `readConcern` level provides a consistent snapshot of all data at the moment the transaction started?**
- [ ] `local`
- [ ] `majority`
- [x] `snapshot`
- [ ] `linearizable`

**Q6. What is the purpose of retrying on the `TransientTransactionError` error label?**
- [ ] To avoid creating duplicate documents
- [ ] To renegotiate the write concern
- [x] To safely retry a transaction that was aborted due to a temporary conflict or network issue
- [ ] To upgrade the transaction to a multi-shard transaction
