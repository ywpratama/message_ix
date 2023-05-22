$title Prime Number Generation (PRIME,SEQ=157)

$onText
This example shows how to use a WHILE statement to find a set of prime numbers.


GAMS Development Corporation, Formulation and Language Example.

Keywords: GAMS formulation and language example, prime number generation, mathematics
$offText

$eolCom //

Set
   s     'set of prime numbers' / 1*200 /
   ss(s) 'primes found until now';

Scalar
   more      'temporary flag'
   candidate 'prime candidate';

Parameter ps(s) 'first s prime numbers';

ps(s) = 0;       // clear prime array
ss(s) = no;      // make primes found set empty

candidate = 3;   // set prime to get started

loop(s,
   more = 1;                             // turn on the search
   while(more,                           // search until found
      loop(ss,                           // only test if still a candidate
         break$(sqr(ps(ss)) > candidate);// leave loop if we check sufficient large prime factors
         more = mod(candidate,ps(ss));   // a prime must have a remainder
         break$(not more);               // leave loop if we found a divisor with remainer 0
      );
      if(more,                           // check if we got one
         ss(s) = yes;                    // bump set of found primes
         ps(s) = candidate;              // save prime number
      );
      more = not more;                   // flip the search flag
      candidate = candidate + 2;         // next candidate has to be odd
   );
);
display ps;