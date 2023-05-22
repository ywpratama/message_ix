Scalars
   prev_OBJ    previous objective value / 10 /
   delta_OBJ   difference between current and previous OBJ values  / 2 /
   count_iter  iteration counts / 1 /
   OBJ objective function / 0 /  ;
$SETGLOBAL foresight "0"
$SETGLOBAL learningmode "1"
*$ontext
if (%foresight% = 0,
    IF(%learningmode% = 1,
         while(count_iter <= 10 and delta_OBJ >= 0.1,
               OBJ = prev_OBJ**0.5 ;
               delta_OBJ = (prev_OBJ - OBJ)/prev_OBJ ;
               prev_OBJ = OBJ ;

               display count_iter, OBJ, delta_OBJ, prev_OBJ;

               count_iter = count_iter + 1 ;
         );
         );
    ELSE
*        write a status update to the log file, solve the model
         put_utility 'log' /'+++ Solve the perfect-foresight version of MESSAGEix +++ ' ;
    );

*$offtext
$ontext
Scalar j, k;
j = 1;
k = 10;

While(j <= 5 and k >= 6,
   Display j, k;
   j = j + 1;
   k = k - 1;
);
$offtext