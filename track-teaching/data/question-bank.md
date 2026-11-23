# Question bank: describing data

<!--
Example question bank for the track "Teaching materials".
Written for teaching staff from any field; the topic is basic descriptive
statistics and reading plots. Converted to a Canvas-importable QTI zip by
bank2qti.py (in this folder).

FORMAT (one block per question):

  ## <id>: <short title>
  - type: mc            (mc = multiple choice, one correct; numeric = a number)
  - topic: <a word or two>
  - difficulty: easy | medium | hard

  The question text (the "stem"). Blank line = new paragraph.

  For mc: one line per choice, starting with a letter and ")". Put a star
  before the letter of the correct choice. Under each choice, an indented
  "why:" line says why it is right or wrong (shown to students as feedback).

  For numeric: "answer: <number>" and "margin: <allowed error, 0 = exact>".

  explanation: <general feedback, shown after answering>
-->

## q01: Mean or median for skewed data
- type: mc
- topic: centre
- difficulty: easy

Reaction times in a psychology experiment have a long tail to the right: most people answer in about 0.5 s, a few take 3 to 4 s.

Which single number best describes a *typical* reaction time?

A) The mean
   why: The few very slow answers pull the mean upwards, so it is larger than most people's times.
*B) The median
   why: Half of the times are below it and half above, whatever the tail does.
C) The mode
   why: For a continuous measurement, almost every value is unique, so the mode is unstable.
D) The range
   why: The range describes spread, not a typical value.

explanation: For skewed data, the median describes the typical value; report the mean too if a later analysis needs it.

## q02: Median of five values
- type: numeric
- topic: centre
- difficulty: easy

Five seedlings have heights (mm) 3, 8, 5, 12 and 7.

What is the median height in mm?

answer: 7
margin: 0

explanation: Sort the values: 3, 5, 7, 8, 12. The middle value is 7.

## q03: Mean of five values
- type: numeric
- topic: centre
- difficulty: easy

Five students scored 4, 6, 6, 9 and 10 points on a quiz.

What is the mean score?

answer: 7
margin: 0

explanation: The sum is 35, and 35 / 5 = 7.

## q04: Which error bar
- type: mc
- topic: spread
- difficulty: medium

A figure shows the mean height of plants in each treatment. The caption says the error bars "show how much individual plants vary".

Which quantity should the error bars show?

*A) The standard deviation (SD)
   why: The SD describes the spread of individual values around the mean.
B) The standard error of the mean (SE)
   why: The SE describes how precisely the mean is estimated. It shrinks as more plants are measured, even if the plants vary just as much.
C) A 95 % confidence interval for the mean
   why: A confidence interval is about the mean, not about individual plants.
D) The full range, from the smallest to the largest plant
   why: The range shows variation but depends on a single extreme plant in each group, and grows with sample size.

explanation: SD for "how much individuals vary"; SE or a confidence interval for "how well we know the mean". Always say which one in the caption.

## q05: Standard error from SD and n
- type: numeric
- topic: spread
- difficulty: medium

A sample of 36 patients has a standard deviation of 12 mmHg for systolic blood pressure.

What is the standard error of the mean, in mmHg?

answer: 2
margin: 0.01

explanation: SE = SD / sqrt(n) = 12 / sqrt(36) = 12 / 6 = 2.

## q06: A plot for small groups
- type: mc
- topic: plots
- difficulty: medium

You have measured 8 animals in each of 5 groups and want a plot that lets readers compare the groups.

Which plot is the best choice?

A) A bar chart of the group means
   why: With 8 values per group, a bar hides the data: two very different distributions can have the same bar.
*B) A dot plot showing every animal, with the group median marked
   why: Every value is visible, so readers can see spread, overlap and outliers themselves.
C) A pie chart of the group totals
   why: A pie shows parts of a whole. The groups are not parts of a whole, and totals depend on group size.
D) A 3D bar chart of the group means
   why: The third dimension adds nothing and distorts the heights of the bars.

explanation: For small samples, show the data points. Add a box plot or a mean with an interval on top if you like.

## q07: Distances on a log axis
- type: mc
- topic: plots
- difficulty: easy

A plot has a logarithmic (base 10) y axis.

On this axis, the distance from 10 to 100 is the same as the distance from:

A) 100 to 190
   why: That would be true on an ordinary (linear) axis, where equal differences get equal distances.
*B) 100 to 1000
   why: On a log axis, equal ratios get equal distances. Both steps are a factor of 10.
C) 0 to 10
   why: Zero cannot be shown on a log axis: the logarithm of 0 is not defined.
D) 50 to 100
   why: That step is a factor of 2, not 10, so it is shorter.

explanation: Log axes turn equal ratios into equal distances. Useful for data that spans several orders of magnitude.

## q08: Percentage change
- type: numeric
- topic: comparison
- difficulty: medium

The number of students who passed a course went from 40 one year to 50 the next.

By what percentage did the number increase? Enter a number without the % sign.

answer: 25
margin: 0

explanation: The change is 10, and 10 / 40 = 0.25, so 25 %. (Dividing by the new value, 50, gives 20 %: a common mistake.)

## q09: Correlation and cause
- type: mc
- topic: correlation
- difficulty: hard

Across the months of several years, a town's ice-cream sales and the number of drownings have a correlation of r = 0.9.

Which statement is best supported?

A) Eating ice cream increases the risk of drowning.
   why: A correlation alone does not show which way an effect goes, or whether there is one at all.
*B) A third factor, such as warm weather, may drive both.
   why: Warm months bring both more ice cream and more swimming. A shared cause produces a strong correlation without any direct effect.
C) Ice-cream sales explain 90 % of the variation in drownings.
   why: The share of variation explained is r squared (0.81), not r, and even that says nothing about cause.
D) The correlation is too weak to mean anything.
   why: r = 0.9 is a strong correlation. The problem is interpretation, not strength.

explanation: A strong correlation is a reason to look for an explanation, not an explanation. Look for shared causes before you claim an effect.

## q10: The line in a box plot
- type: mc
- topic: plots
- difficulty: easy

In a standard box plot, what does the line inside the box show?

A) The mean
   why: A common mix-up. The standard box plot is built from quartiles; some programs add the mean as a separate symbol.
*B) The median
   why: The box runs from the first to the third quartile, and the line marks the median (the second quartile).
C) The mode
   why: Box plots do not show the mode.
D) The midpoint between the smallest and largest value
   why: That is the mid-range. It depends only on the two extreme values.

explanation: Box = middle half of the data (first to third quartile); line = median; whiskers = the rest, up to a limit; points beyond = possible outliers.
