# Ashfall Outpost - weekly status report (constraint stack v1)

Write this week's status report for the Ashfall Outpost colony. The content
itself is not graded - only the numbered constraints below are, checked by a
script using exactly the definitions given here.

Some constraints are deliberately in tension. It is possible that some cannot
be satisfied together at all. Satisfy every constraint you can. If two
constraints genuinely cannot both hold, do NOT silently break one: satisfy the
one that is consistent with the rest of the document, and report the conflict
in a FLAG line (format below). Credit is earned for flagging genuinely
conflicting pairs and lost for flagging pairs that are jointly satisfiable.

## Definitions (the checker's exact semantics)

- **document**: starts at the line `== SUMMARY ==` and ends at the line
  `END OF REPORT.` Everything outside the document is ignored, except FLAG
  lines after the end.
- **section**: a header line plus the content lines that follow it, up to the
  next header or the end line. A header line has the exact form `== NAME ==`.
- **word**: a whitespace-separated token.
- **whole word**: bounded by non-letter/non-digit characters.
- **sentence**: ends at `.`, `!`, or `?`. A trailing fragment with no
  terminator also counts as one sentence.
- Trailing spaces on a line are ignored.

## Constraints

1. The document contains exactly 6 sections, each introduced by a header line
   of the exact form `== NAME ==` (name in capital letters, nothing else on
   the line).
2. The section names, in order: SUMMARY, POWER, WATER, FOOD, MORALE,
   DIRECTIVE.
3. The total word count of all section content is between 180 and 260
   inclusive (header lines and the `END OF REPORT.` line do not count).
4. No line of the document is longer than 72 characters.
5. Blank lines appear only immediately before the 2nd through 6th header
   lines - exactly one before each, and none anywhere else in the document.
6. The word "colony" appears exactly 3 times in the document
   (case-insensitive, whole word).
7. The letter z (either case) appears only inside occurrences of "hazard"
   (case-insensitive substring), and "hazard" appears exactly once in the
   document.
8. Digits (0-9) appear only in the POWER section.
9. Every section contains at least one digit.
10. The POWER section contains exactly 3 integers (maximal digit runs), and
    they sum to 100.
11. The first word after the first header line is exactly `Dust`.
12. The last line of the document is exactly `END OF REPORT.`
13. The first sentence of each section contains that section's own name in
    lowercase, as a whole word (e.g. "power" somewhere in POWER's first
    sentence).
14. The FOOD and WATER sections contain the same number of words.
15. The WATER section contains exactly 3 sentences.
16. The word "ration" (case-insensitive, whole word) appears at least once in
    FOOD, at least once in WATER, and nowhere else.
17. The word "hazard" does not appear anywhere in the document.
18. The document contains no commas.
19. The document contains no apostrophes (straight or curly).
20. The SUMMARY section contains each of the words "power", "water", "food",
    "morale", "directive" (lowercase, whole word) exactly once.
21. The MORALE section contains exactly 2 question marks, and no other
    section contains any.
22. Every sentence in the SUMMARY section begins with a word of at most 4
    characters (surrounding punctuation ignored).
23. The exact text `grit-index nominal` appears exactly twice in the
    document, in two different sections.

## FLAG lines

Report each genuine conflict on its own line AFTER the `END OF REPORT.` line,
in exactly this format (one line per conflict):

```
FLAG: <number> conflicts with <number> - <one short reason>
```

FLAG lines are outside the document, so no constraint applies to them.

When both members of a conflicting pair are individually consistent with the
rest of the document, satisfy the **lower-numbered** one and leave the
higher-numbered one unsatisfied.

## Output

Output only the document followed by any FLAG lines. No preamble, no
commentary, no code fences.
