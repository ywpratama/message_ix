Parameters
  cap_new2(node,learning_tec,year_all2)        'annual newly installed capacity'
  bin_cap_new(node,learning_tec,year_all2)     'binary of newly installed capacity'
  inv_cost_ref(node,learning_tec)              'initial capex' ;

SCALAR hist_length                       the length of historical periods;
hist_length = card(year_all2) - card(model_horizon);

VARIABLES
  NBR_UNIT(node,learning_tec,size,year_all2)   number of units for each size every year
  CAPEX_TEC(node,learning_tec,year_all2)       capital cost in dollar per kW
  OBJECT                                 objective function ;

POSITIVE VARIABLES
  NBR_UNIT ;

EQUATIONS
  OBJECTIVE_INNER        total investment cost
  CAP_NEW_BALANCE        installed capacity balance
  CAPEX_ESTIMATE         estimating average capex
  INITIAL_YEAR          annual investment cost
  NO_BUILT_YEAR          annual investment cost
;


OBJECTIVE_INNER..                        OBJECT =e= sum((node,learning_tec,year_all2), CAPEX_TEC(node,learning_tec,year_all2)*cap_new2(node,learning_tec,year_all2)*duration_period(year_all2)) ;
CAP_NEW_BALANCE(node,learning_tec,year_all2).. sum(size, NBR_UNIT(node,learning_tec,size,year_all2)*u(learning_tec,size)) =e= cap_new2(node,learning_tec,year_all2)*duration_period(year_all2) ;
CAPEX_ESTIMATE(node,learning_tec,year_all2)..  CAPEX_TEC(node,learning_tec,year_all2)*cap_new2(node,learning_tec,year_all2)*duration_period(year_all2) =g= sum(size,inv_cost_ref(node,learning_tec)
                                              * NBR_UNIT(node,learning_tec,size,year_all2)*u(learning_tec,size)
                                              * [(((sum((size2,year_all3)$(ord(year_all3) le (ord(year_all2)-1) and ord(year_all3) gt hist_length), NBR_UNIT(node,learning_tec,size2,year_all3))+nbr_unit_ref(learning_tec))/nbr_unit_ref(learning_tec))**(-learning_par(learning_tec)))]
                                              * [((u(learning_tec,size)/u_ref(learning_tec))**eos_par(learning_tec))/(u(learning_tec,size)/u_ref(learning_tec))]) ;
INITIAL_YEAR(node,learning_tec,year_all2)$(ord(year_all2) eq 1)..   CAPEX_TEC(node,learning_tec,year_all2) =e= inv_cost_ref(node,learning_tec) ;
NO_BUILT_YEAR(node,learning_tec,year_all2)$(ord(year_all2) gt 1)..   CAPEX_TEC(node,learning_tec,year_all2) =e= bin_cap_new(node,learning_tec,year_all2)*CAPEX_TEC(node,learning_tec,year_all2)
                                                                              + (1-bin_cap_new(node,learning_tec,year_all2))*CAPEX_TEC(node,learning_tec,year_all2-1) ;

model learningeos /   OBJECTIVE_INNER, CAP_NEW_BALANCE,
                      CAPEX_ESTIMATE, INITIAL_YEAR, NO_BUILT_YEAR  /;
