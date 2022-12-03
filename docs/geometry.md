!!! quote "interview question"

    If a job candidate has a 1% chance of passing an interview, what is the chance that he receives a job offer after 100 interviews?

The first iteration I saw of this question required solving the problem without a calculator. The exact solution is easy with a bit of probability theory. The approximation requires a bit of intuition, and a much longer explanation.

The probability that they succeed on the Nth interview is the probability of succeeding during an inteview after failing (n-1) interviews i.e.

$$
PMF = p*(1-p)^{n-1}
$$

And the chance that they would have succeeded on at least 1 of the N interviews is the inverse of them failing every interview i.e.

$$
CDF = 1 - (1-p)^n
$$ 

If we plug in our values for p=0.01 and n = 100 With a calculator the answer to two decimal places is 0.63.

Given that p =1/n in the question my first thought was to find a general solution for all values where p is the inverse of n, i.e. p * n =1. Intuitively whether n is 100 or 1000 the answer should be approximately the same since the expected amount of interview successes is the same (p * n).

The mathematical definition of e is close to what we want but we have the wrong sign in the brackets.

$$
e = \lim_{n \to \infty} (1+1/n)^n
$$

Let's introduce an approximation:

$$
\lim_{x \to \infty} (1 + 1/x)^n = (1 + n/x)
$$

!!! note
    in this approximation we can replace x with -x and n with -n and the approximation still holds i.e. for numbers very close to 1 the power operation is similar to multiplication.


``` py title="correect to the 5th decimal place"
assert abs(1.001**4) - 1.004 < 0.00001
```

let's use this to get the negative version of the definition of e. Taking n to the limit of infinity:

$$ (1-1/n)^n = (1+1/n)^{-n} = 1/e $$

Each time we swap a sign we are taking the reciprocal. If we take the reciprocal twice we get the original (applying any inverse function twice is the identity function).

$$ e = \lim_{n \to \infty} (1-1/n)^{-n} $$

$$ 1/e = \lim_{n \to \infty} (1-1/n)^{n} $$

with this second limit we are getting very close to the geometric distributions CDF, let's swap out the expression. for p * n =1

$$ CDF = 1 - (1-p)^n = 1 - 1/e $$


``` py title="e approximation vs calculator"
from math import e
calculated =  1 - (1-0.01)**100 #apprxomiately 0.63
estimated = 1 - 1/e             #approximately 0.63
assert abs(calculated - estimated)  < 0.01
```

This approximation holds roughly to the number of decimal places of p.

The expression is particularly nice when we assume n*p =1, but even without the assumption, we could still receive an answer in terms of e:

$$ estimation = 1 - 1/(e^{p*n}) $$
