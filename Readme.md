A NLP QA dataset generator simple staged inference questions. i.e. those questions that
require little reasoning or world knowledge to answer, but may require large working
memory or effective use of scratch memory.

Examples:
    Q: What is the number of letters in: the item(s) whose 10th letter (including spaces) is a 'r' from: the string(s) whose length (including spaces) is 10 in: the names of the first ten us presidents in chronological order ?
    A: 10
    Reasoning: 10 | john tyler | ['john adams', 'john tyler'] | ['george washington', 'john adams', 'thomas jefferson', 'james madison', 'james monroe', 'john quincy adams', 'andrew jackson', 'martin van buren', 'william henry harrison', 'john tyler']

    Q: What is the 4th letter of: the string(s) whose length (including spaces) is 4 in: the item(s) whose 2nd letter (including spaces) is an 'a' from: names of the planets from closest to the sun to furthest, including pluto ?
    A: s
    Reasoning: s | mars | ['earth', 'mars', 'saturn'] | ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']