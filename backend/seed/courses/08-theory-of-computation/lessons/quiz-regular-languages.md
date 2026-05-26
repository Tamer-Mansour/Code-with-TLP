# Quiz: Regular Expressions & Regular Languages

**Q1. Which of the following languages is regular?**
- [ ] {0ⁿ1ⁿ | n ≥ 0}
- [x] {w ∈ {0,1}* | w contains at least two 1s}
- [ ] {0ⁿ | n is prime}
- [ ] {ww | w ∈ {0,1}*}

**Q2. The regular expression (0∪1)*1(0∪1)* describes:**
- [ ] All binary strings
- [x] All binary strings that contain at least one 1
- [ ] Binary strings starting with 1
- [ ] Binary strings ending with 1

**Q3. In the pumping lemma for regular languages, condition |xy| ≤ p guarantees:**
- [x] The pumped portion y lies within the first p symbols (the loop occurs early in the string)
- [ ] y is at least as long as z
- [ ] The string s has length exactly p
- [ ] y can be any non-empty substring of s

**Q4. Thompson's construction builds which model directly from a regular expression?**
- [ ] A minimal DFA
- [x] An NFA (with at most 2|R| states, where |R| is the regex size)
- [ ] A pushdown automaton
- [ ] A Turing machine

**Q5. To prove L is NOT regular using the pumping lemma, you must show:**
- [ ] One specific split xyz where pumping fails for all i
- [x] For every valid split xyz (with |y|≥1, |xy|≤p), there exists some i≥0 such that xyⁱz ∉ L
- [ ] That L has more strings than the pumping length allows
- [ ] That the Myhill-Nerode relation has infinitely many classes (that is a different tool)

**Q6. Regular languages are closed under all of the following EXCEPT:**
- [ ] Union
- [ ] Intersection
- [ ] Complement
- [x] There is no exception — regular languages are closed under union, intersection, complement, concatenation, Kleene star, and reversal

**Q7. The language {0^(n²) | n ≥ 0} is not regular because:**
- [ ] It contains strings of length 0
- [ ] It has infinitely many strings
- [x] The Myhill-Nerode equivalence classes for this language are infinite: 0^(n²) and 0^(m²) are distinguishable for n≠m
- [ ] The pumping lemma applies only to languages over {0,1}
