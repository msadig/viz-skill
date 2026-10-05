# ASD-STE100 Simplified Technical English: the rules to obey

Source: ASD-STE100 Issue 7 (2017). All 53 rules: `references/writing-rules.md`. The 869 approved words: `references/word-list.md`. Replacements: `references/substitutions.md`. Examples: `references/ste-examples.md`. License: `references/STE-NOTICE.md`.

Apply STE to labels, captions, report prose, PR text and docs that you write. Do not apply it to code, identifiers, commands, paths, quoted error messages, official product names or quoted text.

## 1. Classify the text

- **Procedural** tells the reader to do something: "Remove the 4 bolts."
- **Descriptive** gives information: "The pump supplies fuel to the engine."

Do not mix the two types in 1 paragraph. Diagram labels and captions are descriptive.

## 2. Verbs

- Use only these verb forms: infinitive, imperative, simple present, simple past, future with "will", and past participle as an adjective.
- Do not use "-ing" verb forms. The approved "-ing" words are: mating, missing, remaining, lighting, opening, routing, servicing, during.
- Do not use a helping verb with a past participle. Write "the agent adjusted it", not "has adjusted".
- Use the active voice. In procedures, use the imperative: "Set the switch to ON."
- The only helping verbs are **can, must, will**. Do not use should, would, may, might or shall.

## 3. Sentences

- Procedural sentences: 20 words maximum. Descriptive sentences: 25 words maximum.
- A paragraph has 6 sentences maximum and 1 topic.
- Write 1 instruction per sentence and 1 topic per sentence.
- If a condition comes before a command, put a comma after the condition: "If the light comes on, stop the engine."
- Keep the articles and "that": "make sure that the file exists".
- Do not use contractions. Do not use semicolons.
- For complex text, use a vertical list.

## 4. Words

- Use only approved words, technical names and technical verbs.
- Use an approved word only as its listed part of speech. "Test" is a noun: write "do a test", not "test the system".
- Use 1 name for 1 item in the full text.
- A noun cluster has 3 words maximum. Break longer clusters with of, on, in or for.
- Do not use phrasal verbs. Write "extinguish", not "put out".
- Do not use vague words. Give the quantity, name or action. Write numbers as digits.
- Use American English spelling.

## 5. Safety

- **WARNING** = a risk of injury or death. **CAUTION** = a risk of damage to objects or data.
- Start with the command, then give the risk: "CAUTION: Do not run the migration twice. The table can lose rows."

## 6. Check

Run `scripts/ste_check.py --strict --mode <procedural|descriptive|mixed> <file>`. The diagram and report scripts run it for you. Fix each error and check again.

The tool cannot see if a word has its approved *meaning*. Read your text against the word list for the words you are not sure about.
