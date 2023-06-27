Parameters
  cap_new2(node,learning_tec,year_all2)        'annual newly installed capacity'
  bin_cap_new(node,learning_tec,year_all2)     'binary of newly installed capacity'
  inv_cost_ref(node,learning_tec)              'initial capex'
  bin_cap_new_glb(learning_tec,year_all2)      'binary of global newly installed capacity';


SCALAR hist_length                       the length of historical periods;
hist_length = card(year_all2) - card(model_horizon);

VARIABLES
  NBR_UNIT(learning_tec,size,year_all2)   number of units for each size every year
  CAPEX_TEC_IDX(learning_tec,year_all2)       capital cost in dollar per kW
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


OBJECTIVE_INNER..                        OBJECT =e= sum((node,learning_tec,year_all2), CAPEX_TEC_IDX(learning_tec,year_all2)*cap_new2(node,learning_tec,year_all2)*duration_period(year_all2)) ;
CAP_NEW_BALANCE(learning_tec,year_all2).. sum(size, NBR_UNIT(learning_tec,size,year_all2)*u(learning_tec,size)) =e=
                                                                                 sum(node, cap_new2(node,learning_tec,year_all2))
                                                                                 *duration_period(year_all2) ;
CAPEX_ESTIMATE(learning_tec,year_all2)..  CAPEX_TEC_IDX(learning_tec,year_all2)*sum(node, cap_new2(node,learning_tec,year_all2))*duration_period(year_all2) =g=
                                                         sum(size, NBR_UNIT(learning_tec,size,year_all2)*u(learning_tec,size)
                                                         * [(((sum((size2,year_all3)$(ord(year_all3) le (ord(year_all2)-1) and ord(year_all3) gt hist_length),
                                                                                 NBR_UNIT(learning_tec,size2,year_all3))
                                                                                 + nbr_unit_ref(learning_tec))/nbr_unit_ref(learning_tec))**(-learning_par(learning_tec)))]
                                                         * [((u(learning_tec,size)/u_ref(learning_tec))**eos_par(learning_tec))/(u(learning_tec,size)/u_ref(learning_tec))]) ;
INITIAL_YEAR(learning_tec,year_all2)$(ord(year_all2) eq 1)..   CAPEX_TEC_IDX(learning_tec,year_all2) =e= 1 ;
NO_BUILT_YEAR(learning_tec,year_all2)$(ord(year_all2) gt 1)..   CAPEX_TEC_IDX(learning_tec,year_all2) =e= bin_cap_new_glb(learning_tec,year_all2)
                                                                                 * CAPEX_TEC_IDX(learning_tec,year_all2)
                                                                                 + (1-bin_cap_new_glb(learning_tec,year_all2))*CAPEX_TEC_IDX(learning_tec,year_all2-1) ;

MODEL learningeos /   OBJECTIVE_INNER, CAP_NEW_BALANCE,
                      CAPEX_ESTIMATE, INITIAL_YEAR, NO_BUILT_YEAR  /;

